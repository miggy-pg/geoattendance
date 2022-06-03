import json
import os
from asgiref.sync import (
    sync_to_async, 
    async_to_sync
)
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
from datetime import datetime
from django.db.models import Q
from django.template.loader import render_to_string

from dashboard.models import (
    EventDay, 
    Event
)
from user.models import (
    User,
    Attendance
)
from datetime import datetime
import pytz


class NewUserConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        print('connected')
        await self.channel_layer.group_add("users", self.channel_name)
        await self.accept()
        

    # Receive message from WebSocket
    async def receive(self, text_data):
        reject = False # disable timeout if less than activity end time
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        time = '00:00:00'
        if(action!='present' and action!='unpresent'):    
            time = text_data_json['time']
        id = text_data_json['id']

        # incase date will be used
        # date = text_data_json['date'] #
        # date_time_obj = datetime.strptime(f'{date} {time}', "%m/%d/%Y %H:%M:%S")

        activity = await self.getActivity()
        activity_start_time = activity.daily_login_time
        activity_end_time = activity.daily_logout_time
        date_time_obj = datetime.strptime(time, "%H:%M:%S")

        if action == 'present' or action == 'unpresent':
            ip = await self.getIP(id)
            reachable = os.system('ping -n 1 '+ ip)
            
            # os system returns 0 if ip is reachable
            status = "Online" if reachable == 0 else 'Offline'
            await self.updateStatus(status,id)
            value = True if action == 'present' and reachable == 0 else False
            if reachable!=0:
                currentTimeout = await self.getTimeout(id)
                await self.setPrevTimeout(id, currentTimeout)
                
                tz_Manila = pytz.timezone('Asia/Manila')
                datetime_Manila = datetime.now(tz_Manila)
                current_time = datetime_Manila.strftime("%H:%M:%S")
                print("Current Time =", current_time)
                temp = await self.toDatabase(id, current_time, 'timeout')
                print('temp:',temp)
            await self.updatePresent(id,value)
            await self.channel_layer.group_send(
                "users",
                {
                    'type':'socketPresent',
                    'action':action,
                    'id':id
                }
            )


        # Notify user activity is not yet over
        if action == 'timeout':
            timeouttime = str(date_time_obj).split(' ')[1]
            if timeouttime < str(activity_end_time):
                reject = True
                
        if reject == True:
            await self.channel_layer.group_send(
                "users",
                {
                    'type': 'rejectTimeout',
                    'message': "Activity is not yet over",
                    'id': id,
                }
            )
 
        if reject == False:
            if action == 'timein':
                timeintime = str(date_time_obj).split(' ')[1]
                data_timein = await self.toDatabase(id, timeintime, action)
                print('this is data', data_timein)
                time = data_timein['timein']
                timein_status = data_timein['timein_status']
                print('this timein_status false', time, timein_status)
            elif action == 'timeout':
                timeouttime = str(date_time_obj).split(' ')[1]
                data_timeout = await self.toDatabase(id, timeouttime, action)
                print('this is data_timeout', data_timeout)
                time = data_timeout['timeout']
                timeout_status = data_timeout['timeout_status']
                print('this timeout_status', time, timeout_status)


    async def socketPresent(self,event):
        action = event['action']
        id = event['id']

        await self.send(text_data=json.dumps({
            'action':action,
            'id':id
        }))
        
    async def rejectTimeout(self,event):
        message = event['message']
        id = event['id']

        await self.send(text_data=json.dumps({
            'message':message,
            'id':id

        }))

    async def send_to_websocket(self, event):
        time = event['time']
        id = event['id']
        action = event['action']
        activity_start_time = event['activity_start_time']
        activity_end_time = event['activity_end_time']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'action':action,
            'time':time,
            'activity_start_time':activity_start_time,
            'activity_end_time':activity_end_time,
            'id': id,
        }))

    async def disconnect(self,close_code):
        print('disconnected')
        await self.channel_layer.group_discard("users", self.channel_name)

    @database_sync_to_async
    def toDatabase (self,id,time,action):
        if action == 'timein':
            User.objects.filter(user_idnumber=id).update(timein=time)
            data = dict()
            # print('this in consumers', data)
            event = Event.objects.filter(Q(event_active='True'))
            print('this event in todatabase:', event)
            activity = EventDay.objects.filter(event_name=event[0])[0]
            if(str(time)<=str(activity.daily_login_time)):
                timein_status = 'Early'
            else:
                timein_status = 'Late'
            User.objects.filter(user_idnumber=id).update(timein_status=timein_status)
            data['timein'] = User.objects.get(user_idnumber=id).timein
            data['timein_status'] = timein_status
            return data
        elif action == 'timeout':
            data = dict()
            prev_timeout_exist = User.objects.filter(user_idnumber=id).values('prev_timeout')
            timeout = User.objects.filter(user_idnumber=id).values('timeout')
            if timeout is not None and prev_timeout_exist is not None:
                timeout_time = User.objects.filter(user_idnumber=id).values('timeout')
                User.objects.filter(user_idnumber=id).update(prev_timeout=timeout_time)
                User.objects.filter(user_idnumber=id).update(timeout=time)
            else:
                User.objects.filter(user_idnumber=id).update(timeout=time)
            event = Event.objects.filter(Q(event_active='True'))
            activity = EventDay.objects.filter(event_name=event[0])[0]
            if(str(time)>=str(activity.daily_logout_time)):
                timeout_status = 'On Time'
            else:
                timeout_status = 'Early'
            User.objects.filter(user_idnumber=id).update(timeout_status=timeout_status)
            data['timeout'] = User.objects.get(user_idnumber=id).timeout
            data['timeout_status'] = timeout_status
            return data

    @database_sync_to_async
    def getActivity(self):
        # event = Event.objects.filter(event_name='TEST')
        event = Event.objects.filter(event_active='True')
        # print(event[0])
        return EventDay.objects.filter(event_name=event[0])[0]

    @database_sync_to_async
    def updatePresent(self,id,value):
        user = User.objects.filter(user_idnumber=id)
        print('updatepresent')
        return user.update(present=value)

    @database_sync_to_async
    def getIP(self,id):
        user = User.objects.get(user_idnumber=id)
        ip = user.ip
        return ip

    @database_sync_to_async
    def updateStatus (self,status,id):
        User.objects.filter(user_idnumber=id).update(status=status)
        return 0

    @database_sync_to_async
    def setPrevTimeout(self,id,time):
        User.objects.filter(user_idnumber=id).update(prev_timeout=time)
        return 0

    @database_sync_to_async
    def getTimeout(self,id):
        user = User.objects.get(user_idnumber=id)
        timeout = user.timeout
        return timeout
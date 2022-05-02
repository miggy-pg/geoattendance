import json
import os
import threading
import datetime

from asgiref.sync import (
    sync_to_async, 
    async_to_sync
)
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
from datetime import datetime
from django.template.loader import render_to_string

from dashboard.models import (
    EventDay, 
    Event
)
from user.models import (
    User,
    Attendance
)


class NewUserConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        print('connected')
        await self.channel_layer.group_add("users", self.channel_name)
        await self.accept()
        

    # Receive message from WebSocket
    async def receive(self, text_data):
        # disable timeout if less than activity end time
        reject = False
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        time = '00:00:00'
        if(action!='present' and action!='unpresent'):    
            time = text_data_json['time']
        id = text_data_json['id']

        activity = await self.getActivity()
        activity_start_time = activity.daily_login_time
        activity_end_time = activity.daily_logout_time
        date_time_obj = datetime.strptime(time, "%H:%M:%S")


        if action == 'present' or action == 'unpresent':
            ip = await self.getIP(id)
            # ping command
            reachable = os.system('ping -c 1 ' + ip)
            # Windows ping returns 0 on success and 1 on failure
            status = "Online" if reachable == 0 else 'Offline'
            await self.updateStatus(status,id)
            value = True if action == 'present' and reachable == 0 else False
            # value for database action for websocket
            if reachable!=0:
                action = 'unpresent'
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
                time = data_timein['timein']
                timein_status = data_timein['timein_status']
            elif action == 'timeout':
                timeouttime = str(date_time_obj).split(' ')[1]
                data_timeout = await self.toDatabase(id, timeouttime, action)
                time = data_timeout['timeout']
                timeout_status = data_timeout['timeout_status']


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
            'id':id,
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
    def toDatabase(self,id,time,action):
        if action == 'timein':
            User.objects.filter(user_idnumber=id).update(timein=time)
            data = dict()
            event = Event.objects.filter(event_name='TEST')
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
            User.objects.filter(user_idnumber=id).update(timeout=time)
            data = dict()
            event = Event.objects.filter(event_name='TEST')
            activity = EventDay.objects.filter(event_name=event[0])[0]
            if(str(time)>=str(activity.daily_logout_time)):
                timeout_status = 'Early'
            else:
                timeout_status = 'Late'
            User.objects.filter(user_idnumber=id).update(timeout_status=timeout_status)
            data['timeout'] = User.objects.get(user_idnumber=id).timeout
            data['timeout_status'] = timeout_status
            return data


    @database_sync_to_async
    def getActivity(self):
        event = Event.objects.filter(event_name='TEST')
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
    def updateStatus(self,status,id):
        User.objects.filter(user_idnumber=id).update(status=status)
        return 0



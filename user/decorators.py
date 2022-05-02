from django.contrib.auth import decorators
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse, request
from django.shortcuts import redirect

# def unauthenticated_user(view_func):
#     def wrapper_func(request, *args, **kwargs):
#         if request.user.is_authenticated:
#             return redirect('index')
#         else:
#             return view_func(request, *args, **kwargs)
#     return wrapper_func


# def allowed_users(allowed_roles=[]):
#     def decorator(view_func):
#         def wrapper_func(request, *args, **kwargs):
            
#             group = None
#             if request.user.group.exists():
#                 group = request.user.group.all()[0].name
            
#             if group in allowed_roles:
#                 return view_func(request, *args, **kwargs)
#             else:
#                 return HttpResponse("You are not authorized to view this page.")
#         return wrapper_func
#     return decorator

def student_only(view_func):
    def wrapper_function(request, *args, **kwargs):
        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name
        
        if group == 'student':
            return view_func(request, *args, **kwargs)
        elif group == 'admin':
            return redirect('dashboard')
        else:
            return redirect('login')

    return wrapper_function
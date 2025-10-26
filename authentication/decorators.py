from django.shortcuts import redirect
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('authentication:show_login')
        
        if not request.user.is_staff:
            return redirect('main:show_main')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper

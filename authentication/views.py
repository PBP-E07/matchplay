from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.models import User

def show_register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(request, "Your account has been successfully created")

            return redirect("authentication:show_login")

    context = { "form": form }

    return render(request, "register.html", context)

def show_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            if user.is_staff or user.is_superuser:
                response = HttpResponseRedirect(reverse("dashboard:dashboard_home"))
            else:
                response = HttpResponseRedirect(reverse("main:show_main"))

            return response
    
    else:
        form = AuthenticationForm(request)
    
    context = { "form": form }

    return render(request, "login.html", context)

def do_logout(request):
    """
    Logs the user out and redirects to the main page.
    """
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect("main:show_main")

@csrf_exempt
def logout_json(request):
    username = request.user.username

    try:
        logout(request)

        return JsonResponse({
            "username": username,
            "message": "Logged out successfully"
        }, status=200)
    except:
        return JsonResponse({
            "message": "Logout failed"
        }, status=401)

@csrf_exempt
def login_json(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            login(request, user)

            return JsonResponse({
                "username": user.username,
                "message": "Login successful"
            }, status=200)
        
        else:
            return JsonResponse({
                "message": "Login failed, account is disabled"
            }, status=401)

    else:
        return JsonResponse({
            "message": "Login failed, please check your username or password"
        }, status=401)

@csrf_exempt
def register_json(request):
    if request.method == "POST":
        username = request.POST["username"]
        password1 = request.POST["password"]
        password2 = request.POST["password"]

        if password1 != password2:
            return JsonResponse({
                "message": "Passwords do not match"
            }, status=400)
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "message": "Username already exists"
            }, status=400)
        
        user = User.objects.create_user(username=username, password=password1)

        user.save()
        
        return JsonResponse({
            "username": user.username,
            "message": "User created successfully"
        }, status=200)
    
    else:
        return JsonResponse({
            "message": "Invalid request method"
        }, status=400)

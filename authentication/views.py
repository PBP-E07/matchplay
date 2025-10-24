from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.urls import reverse

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

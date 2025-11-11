from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import SimpleSignupForm

# Signup view
def signup_view(request):
    if request.method == 'POST':
        form = SimpleSignupForm(request.POST)
        role = request.POST.get('role')
        if form.is_valid():
            user = form.save()
            # Profile is already created by signal, just update the role
            profile = user.profile
            profile.role = role
            profile.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('home')
    else:
        form = SimpleSignupForm()
    return render(request, 'accounts/signup.html', {'form': form})


# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('home')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm

def login_view(request):
    """Vista para el login de usuarios"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Autenticar usuario
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Login exitoso
                login(request, user)
                messages.success(request, f'¡Bienvenido {username}!')
                # Redirige a /reportes/dashboard/
                return redirect('/reportes/dashboard/')
            else:
                # Login fallido
                messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = LoginForm()
    
    return render(request, 'usuarios/login.html', {'form': form})

def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente')
    return redirect('login')
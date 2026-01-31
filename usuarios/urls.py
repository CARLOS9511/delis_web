from django.urls import path
from . import views

from django.views.generic import RedirectView

urlpatterns = [
    # Redirigir raíz al dashboard
    #path('inicio', RedirectView.as_view(url='/reportes/dashboard/', permanent=False)),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
#    path('home/', views.home_view, name='home'),
]
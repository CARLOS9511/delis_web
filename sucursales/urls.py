from django.urls import path
from . import views

app_name = 'sucursales'

urlpatterns = [
    path('', views.lista_sucursales, name='lista'),
    #path('detalle/<int:pk>/', views.detalle_sucursal, name='detalle'),
    
    # APIs
    #path('api/sucursales/', views.api_sucursales, name='api_sucursales'),
]

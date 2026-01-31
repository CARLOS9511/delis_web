from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.lista_productos, name='lista'),
    path('producto/<int:pk>/', views.detalle_producto, name='detalle'),
    path('categorias/', views.lista_categorias, name='categorias'),
    
    # APIs
    path('api/productos/', views.api_productos, name='api_productos'),
    path('api/producto/<int:pk>/', views.api_producto_detalle, name='api_producto_detalle'),
]   
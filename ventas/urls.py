from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    # Lista y CRUD
    path('', views.venta_lista, name='venta_lista'),
    path('crear/', views.venta_crear, name='venta_crear'),
    path('<int:pk>/', views.venta_detalle, name='venta_detalle'),
    path('<int:pk>/editar/', views.venta_editar, name='venta_editar'),
    path('<int:pk>/eliminar/', views.venta_eliminar, name='venta_eliminar'),
    
    # Acciones
    path('<int:pk>/cancelar/', views.venta_cancelar, name='venta_cancelar'),
    path('<int:pk>/completar/', views.venta_completar, name='venta_completar'),
    
    # PDF
    path('<int:pk>/pdf/', views.venta_pdf, name='venta_pdf'),
    
    # API endpoints
    path('api/producto/<int:producto_id>/precio/', views.obtener_precio_producto_venta, name='obtener_precio_producto_venta'),
    path('api/productos/buscar/', views.buscar_productos_venta, name='buscar_productos_venta'),
    #path('api/despacho/<int:despacho_id>/productos/', views.obtener_productos_por_despacho, name='obtener_productos_por_despacho'),
]
from django.urls import path,include
from . import views

app_name = 'despacho'

urlpatterns = [
    # Lista y CRUD
    path('', views.despacho_lista, name='despacho_lista'),
    path('crear/', views.despacho_crear, name='despacho_crear'),
    path('<int:pk>/', views.despacho_detalle, name='despacho_detalle'),
    #path('detalle/<int:pk>/', views.despacho_detalle, name='detalle'),
    path('<int:pk>/editar/', views.despacho_editar, name='despacho_editar'),
    
    # Acciones
    path('<int:pk>/cancelar/', views.despacho_cancelar, name='despacho_cancelar'),
    path('<int:pk>/completar/', views.despacho_completar, name='despacho_completar'),
    
    # PDF
    path('<int:pk>/pdf/', views.despacho_pdf, name='despacho_pdf'),
    
    # API endpoints
    path('api/producto/<int:producto_id>/precio/', views.obtener_precio_producto, name='obtener_precio_producto'),
    path('api/productos/buscar/', views.buscar_productos, name='buscar_productos'),

       # Pedidos y Saldos

    # URLs para pedidos
    path('pedidos/', views.crear_pedido, name='crear_pedido'),
    path('saldos/', views.crear_saldo, name='crear_saldo'),

    path('pedidos_lista/', views.lista_pedidos_excel, name='lista_pedidos'),
    path('guardar-pedidos/', views.guardar_pedidos, name='guardar_pedidos'),
    #path('guardar-pedidos-excel/', views.guardar_pedidos_excel, name='guardar_pedidos_excel'),

#api saldos
    path('api/', include('despacho.api.url')),
    
    # URLs para Despacho formato Excel
    #path('crear-excel/', views.despacho_crear_excel, name='despacho_crear_excel'),
    #path('editar-excel/<int:despacho_id>/', views.despacho_editar_excel, name='despacho_editar_excel'),
    
    
]
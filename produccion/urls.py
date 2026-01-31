from django.urls import path
from . import views

app_name = 'produccion'

urlpatterns = [
    # Lista y detalles
    path('', views.lista_productos, name='lista'),
    path('producto/<int:pk>/', views.detalle_producto, name='detalle'),
    path('categorias/', views.lista_categorias, name='categorias'),
    
    # CRUD Productos
    path('producto/crear/', views.crear_producto, name='crear'),
    path('producto/<int:pk>/editar/', views.editar_producto, name='editar'),
    path('producto/<int:pk>/eliminar/', views.eliminar_producto, name='eliminar'),
    
    # Acciones
    path('producto/<int:pk>/toggle/', views.toggle_producto, name='toggle'),
    path('producto/<int:pk>/ajustar-stock/', views.ajustar_stock, name='ajustar_stock'),
    
    # APIs
    path('api/productos/', views.api_productos, name='api_productos'),
    path('api/producto/<int:pk>/', views.api_producto_detalle, name='api_producto_detalle'),
    path('api/producto/<int:pk>/precio/', views.api_obtener_precio, name='api_obtener_precio'),
    path('api/buscar/', views.api_buscar_productos, name='api_buscar_productos'),

     # Importar desde Excel
    path('importar-excel/', views.importar_excel_view, name='importar_excel_view'),
    path('importar-excel/procesar/', views.importar_excel, name='importar_excel'),
    path('descargar-plantilla/', views.descargar_plantilla_excel, name='descargar_plantilla'),
    
]
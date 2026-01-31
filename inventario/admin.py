# inventario/admin.py

from django.contrib import admin
from .models import Categoria, Producto_insumo

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['activo']
    ordering = ['nombre']


@admin.register(Producto_insumo)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'categoria', 'precio_compra', 'precio_venta', 'stock', 'stock_minimo', 'activo']
    list_filter = ['categoria', 'activo', 'fecha_creacion']
    search_fields = ['codigo', 'nombre', 'descripcion']
    list_editable = ['precio_venta', 'stock', 'activo']
    list_per_page = 20
    ordering = ['nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion', 'categoria', 'imagen')
        }),
        ('Precios', {
            'fields': ('precio_compra', 'precio_venta')
        }),
        ('Inventario', {
            'fields': ('stock', 'stock_minimo', 'activo')
        }),
    )
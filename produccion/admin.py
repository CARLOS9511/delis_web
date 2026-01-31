from django.contrib import admin
from .models import Categoria, Producto, Producto_venta
from django.utils.html import format_html


# --- Admin para Categorías ---
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo', 'fecha_creacion')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)
    readonly_fields = ('fecha_creacion',)
    list_per_page = 20


# --- Admin para Productos ---
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'precio_venta', 'stock', 'mostrar_imagen', 'estado_stock', 'activo')
    list_filter = ('activo', 'categoria')
    search_fields = ('codigo', 'nombre', 'categoria__nombre')
    ordering = ('nombre',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    list_editable = ('precio_venta', 'stock', 'activo')
    list_per_page = 20

    fieldsets = (
        ('Información general', {
            'fields': ('codigo', 'nombre', 'codigo_producto', 'categoria', 'imagen')
        }),
        ('Precios y stock', {
            'fields': ('precio_compra', 'precio_venta', 'stock', 'stock_minimo')
        }),
        ('Estado y fechas', {
            'fields': ('activo', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )

    # --- Mostrar imagen en el admin ---
    def mostrar_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.imagen.url)
        return "Sin imagen"
    mostrar_imagen.short_description = "Imagen"

    # --- Mostrar estado del stock con color ---
    def estado_stock(self, obj):
        if obj.stock == 0:
            color = 'red'
            texto = 'Sin stock'
        elif obj.stock_bajo:
            color = 'orange'
            texto = 'Stock bajo'
        else:
            color = 'green'
            texto = 'OK'
        return format_html('<span style="color:{}; font-weight:bold;">{}</span>', color, texto)
    estado_stock.short_description = "Estado del stock"


# --- Admin para Producto_venta ---
@admin.register(Producto_venta)
class ProductoVentaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'precio_venta', 'stock', 'mostrar_imagen', 'estado_stock', 'activo')
    list_filter = ('activo', 'categoria')
    search_fields = ('codigo', 'nombre', 'categoria__nombre')
    ordering = ('nombre',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    list_editable = ('precio_venta', 'stock', 'activo')
    list_per_page = 20

    fieldsets = (
        ('Información general', {
            'fields': ('codigo', 'nombre', 'codigo_producto', 'categoria', 'imagen')
        }),
        ('Precios y stock', {
            'fields': ('precio_compra', 'precio_venta', 'stock', 'stock_minimo')
        }),
        ('Estado y fechas', {
            'fields': ('activo', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )

    # --- Reutilizamos funciones ---
    def mostrar_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.imagen.url)
        return "Sin imagen"
    mostrar_imagen.short_description = "Imagen"

    def estado_stock(self, obj):
        if obj.stock == 0:
            color = 'red'
            texto = 'Sin stock'
        elif obj.stock_bajo:
            color = 'orange'
            texto = 'Stock bajo'
        else:
            color = 'green'
            texto = 'OK'
        return format_html('<span style="color:{}; font-weight:bold;">{}</span>', color, texto)
    estado_stock.short_description = "Estado del stock"

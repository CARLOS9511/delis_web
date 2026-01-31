from django.contrib import admin
from .models import Venta, DetalleVenta

# --- Inline para DetalleVenta ---
class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    readonly_fields = ('subtotal',)
    #autocomplete_fields = ('producto_venta',)

# --- Admin principal para Venta ---
@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'despacho', 'usuario', 'estado', 'total', 'fecha_creacion', 'tanda', 'chofer')
    list_filter = ('estado', 'fecha_creacion', 'despacho__sucursal')
    search_fields = ('numero', 'usuario__username', 'despacho__numero', 'tanda', 'chofer')
    readonly_fields = ('fecha_creacion', 'subtotal', 'total')
    ordering = ('-fecha_creacion',)
    inlines = [DetalleVentaInline]
    list_per_page = 20

    fieldsets = (
        ('Información General', {
            'fields': ('numero', 'despacho', 'usuario', 'estado', 'tanda', 'chofer')
        }),
        ('Totales', {
            'fields': ('subtotal', 'descuento', 'total')
        }),
        ('Control', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',),
        }),
    )

# --- Admin opcional para DetalleVenta (si quieres verlo fuera de la venta) ---
@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('venta', 'producto_venta', 'cantidad', 'precio_unitario', 'subtotal')
    search_fields = ('venta__numero', 'producto_venta__nombre')
    list_filter = ('venta__estado', 'producto_venta')
    readonly_fields = ('subtotal',)
    ordering = ('venta',)

from django.contrib import admin
from .models import Sucursales

@admin.register(Sucursales)
class SucursalesAdmin(admin.ModelAdmin):
    list_display = ('nombre_sucursal', 'email', 'telefono', 'ciudad', 'activo', 'fecha_registro')
    list_filter = ('activo', 'nombre_sucursal', 'ciudad')
    search_fields = ('nombre_sucursal', 'email', 'ciudad')
    ordering = ('nombre_sucursal',)
    readonly_fields = ('fecha_registro',)
    list_per_page = 20

    fieldsets = (
        ('Información general', {
            'fields': ('nombre_sucursal', 'email', 'telefono', 'direccion', 'ciudad')
        }),
        ('Estado y registro', {
            'fields': ('activo', 'fecha_registro'),
            'classes': ('collapse',),
        }),
    )

# venta/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
import json
#from .models import Despacho,DetalleDespacho #,Venta, DetalleVenta
#from produccion.models import Producto
from sucursales.models import Sucursales

# ========================================
# VISTAS HTML
# ========================================

def lista_sucursales(request):
    """Lista todas las ventas"""
    #sucursales = Sucursales.objects.all().select_related('nombre_sucursal', 'usuario').order_by('-fecha_creacion')
    sucursales = Sucursales.objects.all()
    
    # Filtros
    activo = request.GET.get('activo')
    buscar = request.GET.get('buscar')
    
   # if activo:
   #     sucursales = sucursales.filter(activo=activo)
    
   # if buscar:
   #     sucursales = sucursales.filter(numero__icontains=buscar) | sucursales.filter(sucursal__nombre__icontains=buscar)
    
    context = {
        'sucursales': sucursales,
    }
    return render(request, 'sucursales/lista_sucursales.html', context)


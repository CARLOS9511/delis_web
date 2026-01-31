from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from datetime import datetime
from collections import defaultdict
from decimal import Decimal
from .models import Despacho, DetalleDespacho, Pedidos, Saldos
from .models import Pedidos
from sucursales.models import Sucursales
from produccion.models import Producto, Producto_venta
from .forms import DespachoForm, DetalleDespachoFormSet
import json
from django.utils import timezone
from django.db import transaction

from django.views.decorators.http import require_http_methods
from datetime import datetime,time


# Importar modelos de Venta
from ventas.models import Venta, DetalleVenta

# ==================== VISTA DE PEDIDOS ====================
@login_required
def despacho_pedido(request):
    """Vista para listar pedidos agrupados por sucursal y producto"""
    # Obtener todos los pedidos
    pedidos = Pedidos.objects.select_related(
        'sucursal', 'producto', 'usuario'
    ).all().order_by('sucursal__nombre_sucursal', 'producto__nombre')
    
    # Filtros
    search = request.GET.get('buscar', '')
    sucursal_id = request.GET.get('sucursal', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    # Aplicar filtros
    if search:
        pedidos = pedidos.filter(
            Q(sucursal__nombre_sucursal__icontains=search) |
            Q(producto__nombre__icontains=search)
        )
    
    if sucursal_id:
        pedidos = pedidos.filter(sucursal_id=sucursal_id)
    
    if fecha_desde:
        fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
        pedidos = pedidos.filter(fecha_creacion__gte=fecha_desde_dt)
    
    if fecha_hasta:
        fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
        from django.utils import timezone
        fecha_hasta_dt = timezone.make_aware(
            datetime.combine(fecha_hasta_dt, datetime.max.time())
        )
        pedidos = pedidos.filter(fecha_creacion__lte=fecha_hasta_dt)
    
    # Agrupar pedidos por sucursal
    pedidos_agrupados = {}
    for pedido in pedidos:
        sucursal_nombre = pedido.sucursal.nombre_sucursal
        if sucursal_nombre not in pedidos_agrupados:
            pedidos_agrupados[sucursal_nombre] = {
                'sucursal': pedido.sucursal,
                'pedidos': [],
                'total_cantidad': 0
            }
        pedidos_agrupados[sucursal_nombre]['pedidos'].append(pedido)
        pedidos_agrupados[sucursal_nombre]['total_cantidad'] += pedido.cantidad
    
    # Estadísticas
    stats = {
        'total_pedidos': pedidos.count(),
        'total_sucursales': len(pedidos_agrupados),
        #'total_cantidad': pedidos.aggregate(Sum('cantidad'))['cantidad__sum'] or 0,
    }
    
    # Obtener todas las sucursales para el filtro
    sucursales = Sucursales.objects.filter(activo=True)
    
    context = {
        'pedidos_agrupados': pedidos_agrupados,
        'sucursales': sucursales,
        'stats': stats,
    }
    
    return render(request, 'despacho/pedidos.html', context)


# ==================== VISTA DE SALDOS ====================
@login_required
def despacho_saldos(request):
    """Vista para listar saldos agrupados por sucursal y producto"""
    # Obtener todos los saldos
    saldos = Saldos.objects.select_related(
        'sucursal', 'producto', 'usuario'
    ).all().order_by('sucursal__nombre_sucursal', 'producto__nombre')
    
    # Filtros
    search = request.GET.get('buscar', '')
    sucursal_id = request.GET.get('sucursal', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    # Aplicar filtros
    if search:
        saldos = saldos.filter(
            Q(sucursal__nombre_sucursal__icontains=search) |
            Q(producto__nombre__icontains=search)
        )
    
    if sucursal_id:
        saldos = saldos.filter(sucursal_id=sucursal_id)
    
    if fecha_desde:
        fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
        saldos = saldos.filter(fecha_creacion__gte=fecha_desde_dt)
    
    if fecha_hasta:
        fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
        from django.utils import timezone
        fecha_hasta_dt = timezone.make_aware(
            datetime.combine(fecha_hasta_dt, datetime.max.time())
        )
        saldos = saldos.filter(fecha_creacion__lte=fecha_hasta_dt)
    
    # Agrupar saldos por sucursal
    saldos_agrupados = {}
    for saldo in saldos:
        sucursal_nombre = saldo.sucursal.nombre_sucursal
        if sucursal_nombre not in saldos_agrupados:
            saldos_agrupados[sucursal_nombre] = {
                'sucursal': saldo.sucursal,
                'saldos': [],
                'total_cantidad': 0
            }
        saldos_agrupados[sucursal_nombre]['saldos'].append(saldo)
        saldos_agrupados[sucursal_nombre]['total_cantidad'] += saldo.cantidad
    
    # Estadísticas
    stats = {
        'total_saldos': saldos.count(),
        'total_sucursales': len(saldos_agrupados),
        #'total_cantidad': saldos.aggregate(Sum('cantidad'))['cantidad__sum'] or 0,
    }
    
    # Obtener todas las sucursales para el filtro
    sucursales = Sucursales.objects.filter(activo=True)
    
    context = {
        'saldos_agrupados': saldos_agrupados,
        'sucursales': sucursales,
        'stats': stats,
    }
    
    return render(request, 'despacho/saldos.html', context)



# ==================== LISTA DE DESPACHOS ====================
@login_required
def despacho_lista(request):
    """Vista para listar despachos con filtros"""
    despachos = Despacho.objects.select_related(
        'sucursal', 'usuario',
    ).all()
    
    # Filtros
    search = request.GET.get('buscar', '')
    estado = request.GET.get('estado', '')
    sucursal_id = request.GET.get('sucursal', '')
    fecha = request.GET.get('fecha', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    # Aplicar filtros
    if search:
        despachos = despachos.filter(
            Q(numero__icontains=search) |
            Q(sucursal__nombre_sucursal__icontains=search) |
            Q(chofer__icontains=search) |
            Q(tanda__icontains=search)
        )
    
    if estado:
        despachos = despachos.filter(estado=estado)
    
    if sucursal_id:
        despachos = despachos.filter(sucursal_id=sucursal_id)
        
    if fecha:
        fecha_hasta_dt = datetime.strptime(fecha, '%Y-%m-%d')
        from django.utils import timezone
        fecha_hasta_dt = timezone.make_aware(
            datetime.combine(fecha_hasta_dt, datetime.max.time())
        )
        despachos = despachos.filter(fecha_creacion__lte=fecha_hasta_dt)
    
    if fecha_desde:
        fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
        despachos = despachos.filter(fecha_creacion__gte=fecha_desde_dt)
    
    if fecha_hasta:
        fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
        from django.utils import timezone
        fecha_hasta_dt = timezone.make_aware(
            datetime.combine(fecha_hasta_dt, datetime.max.time())
        )
        despachos = despachos.filter(fecha_creacion__lte=fecha_hasta_dt)
    
    # Estadísticas
    stats = {
        'pendientes': despachos.filter(estado='pendiente').count(),
        'completadas': despachos.filter(estado='completada').count(),
        'canceladas': despachos.filter(estado='cancelada').count(),
    }
    
    # Paginación
    paginator = Paginator(despachos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener todas las sucursales para el filtro
    sucursales = Sucursales.objects.all()
    
    context = {
        'despachos': page_obj,
        'sucursales': sucursales,
        'stats': stats,
    }
    
    #return render(request, 'despacho/lista_despacho.html', context)
    return render(request, 'despacho/lista_despacho.html', context)

#===================================
def limpiar_numero(valor):
    """
    Convierte strings con formato boliviano a Decimal
    '150,00' → Decimal('150.00')
    '150.00' → Decimal('150.00')
    '150' → Decimal('150.00')
    None → Decimal('0.00')
    """
    if not valor:
        return Decimal('0.00')
    
    if isinstance(valor, Decimal):
        return valor
    
    if isinstance(valor, (int, float)):
        return Decimal(str(valor))
    
    # Convertir string: reemplazar coma por punto
    return Decimal(str(valor).replace(',', '.'))


def crear_producto_venta_desde_despacho(despacho):
    """
    Crea/actualiza Producto_venta automáticamente desde DetalleDespacho
    Registra productos en la sucursal destino del despacho
    """
    try:
        detalles_despacho = despacho.detalles.all()
        productos_creados = 0
        productos_actualizados = 0
        
        for detalle in detalles_despacho:
            producto_origen = detalle.producto
            sucursal_destino = despacho.sucursal
            
            # ⭐ Generar código único con prefijo PV- y sucursal
            codigo_producto_venta = f"PV-{producto_origen.codigo}-{sucursal_destino.id}"
            
            # Buscar si ya existe el producto en esa sucursal
            producto_venta, creado = Producto_venta.objects.get_or_create(
                codigo=codigo_producto_venta,
                sucursal_venta=sucursal_destino,
                defaults={
                    'nombre': producto_origen.nombre,
                    'codigo_producto': producto_origen.codigo_producto,
                    'categoria': producto_origen.categoria,
                    'precio_compra': producto_origen.precio_compra,
                    'precio_venta': producto_origen.precio_venta,
                    'stock': detalle.cantidad,  # ⭐ Stock inicial = cantidad despachada
                    'stock_minimo': 0,  # ⭐ Stock mínimo en 0 por defecto
                    'activo': True
                }
            )
            
            if creado:
                productos_creados += 1
            else:
                # Si ya existe, SUMAR el stock
                producto_venta.stock += detalle.cantidad
                producto_venta.save()
                productos_actualizados += 1
        
        return {
            'creados': productos_creados,
            'actualizados': productos_actualizados,
            'total': productos_creados + productos_actualizados
        }
    
    except Exception as e:
        print(f"Error creando productos de venta desde despacho: {str(e)}")
        raise


# ==================== CREAR DESPACHO ====================
@login_required
def despacho_crear(request):
    productos = Producto.objects.filter(activo=True).order_by('nombre')

    if request.method == "POST":
        form = DespachoForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    despacho = form.save()
                    total = 0
                    cantidad_total_forms = int(request.POST.get("detalles-TOTAL_FORMS", 0))
                    detalles_guardados = 0

                    for i in range(cantidad_total_forms):
                        prod_id = request.POST.get(f"detalles-{i}-producto")
                        cantidad_str = request.POST.get(f"detalles-{i}-cantidad")
                        precio_str = request.POST.get(f"detalles-{i}-precio_unitario")

                        if not prod_id:
                            continue

                        cantidad = int(limpiar_numero(cantidad_str))
                        precio = limpiar_numero(precio_str)

                        if cantidad > 0:
                            # Obtener producto y validar stock
                            producto = Producto.objects.select_for_update().get(id=prod_id)
                            
                            if producto.stock < cantidad:
                                raise Exception(
                                    f"Stock insuficiente para {producto.nombre}. "
                                    f"Disponible: {producto.stock}, Solicitado: {cantidad}"
                                )
                            
                            subtotal = cantidad * precio
                            total += subtotal

                            # Crear detalle
                            DetalleDespacho.objects.create(
                                despacho=despacho,
                                producto=producto,
                                cantidad=cantidad,
                                precio_unitario=precio,
                                subtotal=subtotal
                            )
                            
                            # ⭐ DESCONTAR STOCK
                            producto.stock -= cantidad
                            producto.save()
                            
                            detalles_guardados += 1

                    if detalles_guardados == 0:
                        raise Exception("Debe agregar al menos un producto con cantidad mayor a 0")

                    # Guardar totales del despacho
                    despacho.subtotal = total
                    despacho.descuento = limpiar_numero(despacho.descuento)
                    despacho.total = total - despacho.descuento
                    despacho.save()
                    
                    # ⭐⭐⭐ CREAR/ACTUALIZAR PRODUCTOS EN PRODUCTO_VENTA
                    resultado = crear_producto_venta_desde_despacho(despacho)

                    messages.success(
                        request, 
                        f"✅ Despacho {despacho.numero} creado con {detalles_guardados} productos. "
                        f"Stock actualizado. {resultado['creados']} productos creados y {resultado['actualizados']} actualizados en sucursal."
                    )
                    return redirect("despacho:despacho_lista")

            except Producto.DoesNotExist:
                messages.error(request, "❌ Uno de los productos no existe")
            except Exception as e:
                messages.error(request, f"❌ Error: {str(e)}")
        else:
            messages.error(request, "Por favor corrija los errores en el formulario")

    else:
        form = DespachoForm()
        
    # ⭐ OBTENER Y AGRUPAR PRODUCTOS POR CATEGORÍA
    todos_productos = Producto.objects.filter(activo=True).select_related('categoria').order_by('categoria__nombre', 'nombre')
    
    productos_por_categoria = defaultdict(list)
    indice_global = 0
    
    for producto in todos_productos:
        producto_data = {
            'id': producto.id,
            'nombre': producto.nombre,
            'stock': producto.stock,
            'precio_venta': producto.precio_venta,
            'cantidad_actual': 0,
            'precio_actual': producto.precio_venta,
            'subtotal_actual': 0,
            'indice': indice_global,
        }
        categoria_nombre = producto.categoria.nombre if hasattr(producto, 'categoria') and producto.categoria else 'Sin Categoría'
        productos_por_categoria[categoria_nombre].append(producto_data)
        indice_global += 1

    return render(request, "despacho/crear_despacho.html", {
        "form": form,
        "productos_por_categoria": dict(productos_por_categoria),
        "total_productos_count": indice_global,
        "productos": productos,
        "accion": "Crear",
        "despacho": None,
    })


# ==================== DETALLE DESPACHO ====================
@login_required
def despacho_detalle(request, pk):
    """Ver detalle de un despacho"""
    despacho = get_object_or_404(Despacho, pk=pk)
    detalles = despacho.detalles.all().select_related('producto')
    
    context = {
        'despacho': despacho,
        'detalles': detalles,
    }
    
    return render(request, 'despacho/detalle_despacho.html', context)


# ==================== EDITAR DESPACHO ====================
@login_required
def despacho_editar(request, pk):
    despacho = get_object_or_404(Despacho, pk=pk)

    if request.method == "POST":
        form = DespachoForm(request.POST, instance=despacho)

        if form.is_valid():
            try:
                with transaction.atomic():
                    # Restaurar stock de productos anteriores
                    for detalle in despacho.detalles.all():
                        producto = Producto.objects.select_for_update().get(id=detalle.producto_id)
                        producto.stock += detalle.cantidad
                        producto.save()
                    
                    # Eliminar detalles anteriores
                    despacho.detalles.all().delete()
                    
                    # Actualizar despacho
                    despacho = form.save()
                    total = 0
                    cantidad_total_forms = int(request.POST.get("detalles-TOTAL_FORMS", 0))
                    detalles_guardados = 0

                    for i in range(cantidad_total_forms):
                        prod_id = request.POST.get(f"detalles-{i}-producto")
                        cantidad_str = request.POST.get(f"detalles-{i}-cantidad")
                        precio_str = request.POST.get(f"detalles-{i}-precio_unitario")

                        if not prod_id:
                            continue

                        cantidad = int(limpiar_numero(cantidad_str))
                        precio = limpiar_numero(precio_str)

                        if cantidad > 0:
                            producto = Producto.objects.select_for_update().get(id=prod_id)
                            
                            if producto.stock < cantidad:
                                raise Exception(
                                    f"Stock insuficiente para {producto.nombre}. "
                                    f"Disponible: {producto.stock}, Solicitado: {cantidad}"
                                )
                            
                            subtotal = cantidad * precio
                            total += subtotal

                            DetalleDespacho.objects.create(
                                despacho=despacho,
                                producto=producto,
                                cantidad=cantidad,
                                precio_unitario=precio,
                                subtotal=subtotal
                            )
                            
                            producto.stock -= cantidad
                            producto.save()
                            
                            detalles_guardados += 1

                    if detalles_guardados == 0:
                        raise Exception("Debe agregar al menos un producto")

                    # Actualizar totales del despacho
                    despacho.subtotal = total
                    despacho.descuento = limpiar_numero(despacho.descuento)
                    despacho.total = total - despacho.descuento
                    despacho.save()

                    # ⭐⭐⭐ ACTUALIZAR PRODUCTOS EN PRODUCTO_VENTA
                    resultado = crear_producto_venta_desde_despacho(despacho)

                    messages.success(
                        request, 
                        f"✅ Despacho {despacho.numero} actualizado. "
                        f"{resultado['creados']} productos creados y {resultado['actualizados']} actualizados en sucursal."
                    )
                    return redirect("despacho:despacho_lista")

            except Exception as e:
                messages.error(request, f"❌ Error: {str(e)}")
        else:
            messages.error(request, "Corrija los errores del formulario")

    else:
        form = DespachoForm(instance=despacho)

    # AGRUPAR PRODUCTOS POR CATEGORÍA CON DATOS ACTUALES
    todos_productos = Producto.objects.filter(activo=True).select_related('categoria').order_by('categoria__nombre', 'nombre')
    detalles_dict = {d.producto.id: d for d in despacho.detalles.all()}
    
    productos_por_categoria = defaultdict(list)
    indice_global = 0
    
    for producto in todos_productos:
        detalle = detalles_dict.get(producto.id)
        producto_data = {
            'id': producto.id,
            'nombre': producto.nombre,
            'stock': producto.stock,
            'precio_venta': producto.precio_venta,
            'cantidad_actual': detalle.cantidad if detalle else 0,
            'precio_actual': detalle.precio_unitario if detalle else producto.precio_venta,
            'subtotal_actual': detalle.subtotal if detalle else 0,
            'indice': indice_global,
        }
        categoria_nombre = producto.categoria.nombre if hasattr(producto, 'categoria') and producto.categoria else 'Sin Categoría'
        productos_por_categoria[categoria_nombre].append(producto_data)
        indice_global += 1

    return render(request, "despacho/form_despacho.html", {
        "form": form,
        "productos_por_categoria": dict(productos_por_categoria),
        "total_productos_count": indice_global,
        "despacho": despacho,
        "accion": "Editar",
    })


# ==================== CANCELAR DESPACHO ====================
@login_required
@require_POST
def despacho_cancelar(request, pk):
    """Vista para cancelar un despacho"""
    despacho = get_object_or_404(Despacho, pk=pk)
    
    if despacho.estado != 'pendiente':
        messages.error(request, 'Solo se pueden cancelar despachos pendientes.')
    else:
        despacho.estado = 'cancelada'
        despacho.save()
        messages.success(request, f'Despacho {despacho.numero} cancelado.')
    
    return redirect('despacho:despacho_lista')


# ==================== COMPLETAR DESPACHO ====================
@login_required
@require_POST
def despacho_completar(request, pk):
    """Vista para marcar un despacho como completado"""
    despacho = get_object_or_404(Despacho, pk=pk)
    
    if despacho.estado != 'pendiente':
        messages.error(request, 'Solo se pueden completar despachos pendientes.')
    else:
        despacho.estado = 'completada'
        despacho.save()
        messages.success(request, f'Despacho {despacho.numero} completado.')
    
    return redirect('despacho:despacho_detalle', pk=despacho.id)


# ==================== GENERAR PDF ====================
@login_required
def despacho_pdf(request, pk):
    """Vista para generar PDF del despacho"""
    from django.template.loader import get_template
    from weasyprint import HTML
    
    despacho = get_object_or_404(
        Despacho.objects.select_related('sucursal', 'usuario')
        .prefetch_related('detalles__producto'),
        pk=pk
    )
    
    template = get_template('despacho/pdf_despacho.html')
    context = {'despacho': despacho}
    html_string = template.render(context)
    
    # Generar PDF
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()
    
    # Retornar PDF
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="despacho_{despacho.numero}.pdf"'
    
    return response


# ==================== API: OBTENER PRECIO PRODUCTO ====================
@login_required
def obtener_precio_producto(request, producto_id):
    """API para obtener el precio de un producto"""
    try:
        producto = Producto.objects.get(id=producto_id)
        return JsonResponse({
            'success': True,
            'precio': float(producto.precio_venta),
            'nombre': producto.nombre,
            'stock': producto.stock if hasattr(producto, 'stock') else None
        })
    except Producto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Producto no encontrado'
        }, status=404)


# ==================== API: BUSCAR PRODUCTOS ====================
@login_required
def buscar_productos(request):
    """API para buscar productos por nombre o código"""
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'productos': []})
    
    productos = Producto.objects.filter(
        Q(nombre__icontains=query) | Q(codigo__icontains=query),
        activo=True
    )[:10]
    
    resultados = [{
        'id': p.id,
        'nombre': p.nombre,
        'codigo': p.codigo if hasattr(p, 'codigo') else '',
        'precio': float(p.precio_venta),
    } for p in productos]
    
    return JsonResponse({'productos': resultados})


# ==================== ELIMINAR DESPACHO ====================
@login_required
def despacho_eliminar(request, pk):
    despacho = get_object_or_404(Despacho, pk=pk)

    if request.method == "POST":
        try:
            with transaction.atomic():
                # ⭐ RESTAURAR STOCK ANTES DE ELIMINAR
                for detalle in DetalleDespacho.objects.filter(despacho=despacho):
                    producto = Producto.objects.select_for_update().get(id=detalle.producto_id)
                    producto.stock += detalle.cantidad
                    producto.save()
                
                numero = despacho.numero
                despacho.delete()
                
                messages.success(request, f"✅ Despacho {numero} eliminado. Stock restaurado.")
        except Exception as e:
            messages.error(request, f"❌ Error al eliminar: {str(e)}")
        
        return redirect("despacho:despacho_lista")

    return render(request, "despacho/despacho_eliminar.html", {
        "despacho": despacho
    })

#-----PEDIDOS Y SALDOS

@login_required
def crear_pedido(request):
    """Vista para crear un nuevo pedido tipo Excel - MANTIENE DATOS SIEMPRE"""
    
    # Obtener la sucursal del usuario usando first_name
    user_sucursal = None
    user_sucursal_id = None
    
    if request.user.first_name:
        try:
            # Buscar la sucursal que coincida con el first_name del usuario
            user_sucursal = Sucursales.objects.get(nombre_sucursal=request.user.first_name)
            user_sucursal_id = user_sucursal.id
        except Sucursales.DoesNotExist:
            messages.warning(
                request, 
                f'No se encontró la sucursal "{request.user.first_name}". Por favor, contacte al administrador.'
            )
    
    # Variables para mantener los datos en el formulario
    cantidades_productos = {}
    
    if request.method == 'POST':
        accion = request.POST.get('accion', 'guardar')
        
        # Si presionó EDITAR, redirige para limpiar
        if accion == 'editar':
            messages.info(request, 'Formulario limpiado correctamente')
            return redirect('despacho:crear_pedido')
        
        # Usar la sucursal del usuario automáticamente
        if not user_sucursal_id:
            messages.error(
                request, 
                'No tiene una sucursal asignada. Contacte al administrador para configurar su cuenta.'
            )
            return redirect('despacho:crear_pedido')
        
        sucursal = user_sucursal
        
        # Obtener todos los productos y sus cantidades
        hoy = timezone.localdate()

        inicio = timezone.make_aware(datetime.combine(hoy, time.min))
        fin = timezone.make_aware(datetime.combine(hoy, time.max))

        productos = Producto.objects.filter(
            fecha_creacion__range=(inicio, fin)
        )
        #productos = Producto.objects.all()
        pedidos_creados = 0
        tiene_productos = False
        
        # Recolectar TODAS las cantidades para mantenerlas después de guardar
        for producto in productos:
            cantidad_key = f'cantidad_{producto.id}'
            cantidad = request.POST.get(cantidad_key, 0)
            
            try:
                cantidad = int(cantidad)
            except (ValueError, TypeError):
                cantidad = 0
            
            # Guardar TODAS las cantidades (incluso las que son 0)
            cantidades_productos[producto.id] = cantidad
            
            # Solo crear pedido si cantidad > 0
            if cantidad > 0:
                tiene_productos = True
                Pedidos.objects.create(
                    sucursal=sucursal,
                    producto=producto,
                    cantidad=cantidad,
                    usuario=request.user
                )
                pedidos_creados += 1
        
        # Validar que haya al menos un producto
        if not tiene_productos:
            messages.warning(request, 'Debe ingresar al menos un producto con cantidad mayor a 0')
            # MANTENER TODOS LOS DATOS
            context = {
                'productos': productos,
                'fecha_actual': timezone.now().strftime('%d/%m/%Y'),
                'cantidades_productos': cantidades_productos,
                'user_sucursal_id': user_sucursal_id,
            }
            return render(request, 'despacho/pedidos_nuevos.html', context)
        
        # ✅ GUARDADO EXITOSO - MANTENER TODOS LOS DATOS
        messages.success(
            request, 
            f'✓ Se guardaron {pedidos_creados} pedidos para {sucursal.nombre_sucursal}'
        )
        
        # Renderizar el mismo formulario CON LOS DATOS MANTENIDOS
        hoy = timezone.localdate()
        inicio = timezone.make_aware(datetime.combine(hoy, time.min))
        fin = timezone.make_aware(datetime.combine(hoy, time.max))
        productos = Producto.objects.filter(
            fecha_creacion__range=(inicio, fin)
        ).order_by('nombre')

        #productos = Producto.objects.all().order_by('nombre')
        
        context = {
            'productos': productos,
            'fecha_actual': timezone.now().strftime('%d/%m/%Y'),
            'cantidades_productos': cantidades_productos,  # ← MANTIENE LAS CANTIDADES
            'user_sucursal_id': user_sucursal_id,
        }
        
        return render(request, 'despacho/pedidos_nuevos.html', context)
    
    # GET request - Formulario limpio
    hoy = timezone.localdate()
    inicio = timezone.make_aware(datetime.combine(hoy, time.min))
    fin = timezone.make_aware(datetime.combine(hoy, time.max))
    productos = Producto.objects.filter(
        fecha_creacion__range=(inicio, fin)
    ).order_by('nombre')
    #productos = Producto.objects.all().order_by('nombre')
    
    print(f"🔍 Total productos: {productos.count()}")
    print(f"🔍 Usuario: {request.user.username}")
    print(f"🔍 First name (Sucursal): {request.user.first_name}")
    print(f"🔍 Sucursal ID: {user_sucursal_id}")
    
    context = {
        'productos': productos,
        'fecha_actual': timezone.now().strftime('%d/%m/%Y'),
        'cantidades_productos': {},
        'user_sucursal_id': user_sucursal_id,
    }
    
    return render(request, 'despacho/pedidos_nuevos.html', context)

##saldos


@login_required
def crear_saldo(request):
    """Vista para crear un nuevo saldo con saldo_hoy y saldo_ayer"""
    
    # Obtener la sucursal del usuario usando first_name
    user_sucursal = None
    user_sucursal_id = None
    
    if request.user.first_name:
        try:
            user_sucursal = Sucursales.objects.get(nombre_sucursal=request.user.first_name)
            user_sucursal_id = user_sucursal.id
        except Sucursales.DoesNotExist:
            messages.warning(
                request, 
                f'No se encontró la sucursal "{request.user.first_name}". Contacte al administrador.'
            )
    
    # Variables para mantener los datos en el formulario
    saldos_hoy_productos = {}
    saldos_ayer_productos = {}
    
    if request.method == 'POST':
        accion = request.POST.get('accion', 'guardar')
        
        # Si presionó LIMPIAR, redirige
        if accion == 'editar':
            messages.info(request, 'Formulario limpiado correctamente')
            return redirect('despacho:crear_saldo')
        
        # Validar sucursal
        if not user_sucursal_id:
            messages.error(request, 'No tiene una sucursal asignada.')
            return redirect('despacho:crear_saldo')
        
        sucursal = user_sucursal
        
        # Obtener lista de productos del modelo
        productos = Saldos.PRODUCTOS_SALDOS
        saldos_creados = 0
        tiene_productos = False
        
        # Iterar sobre cada producto
        for idx, (producto_nombre, _) in enumerate(productos):
            saldo_hoy_key = f'saldo_hoy_{idx}'
            saldo_ayer_key = f'saldo_ayer_{idx}'
            
            saldo_hoy = request.POST.get(saldo_hoy_key, 0)
            saldo_ayer = request.POST.get(saldo_ayer_key, 0)
            
            try:
                saldo_hoy = int(saldo_hoy)
            except (ValueError, TypeError):
                saldo_hoy = 0
            
            try:
                saldo_ayer = int(saldo_ayer)
            except (ValueError, TypeError):
                saldo_ayer = 0
            
            # Guardar valores para mantenerlos en el formulario
            saldos_hoy_productos[idx] = saldo_hoy
            saldos_ayer_productos[idx] = saldo_ayer
            
            # Crear saldo si al menos uno de los valores es mayor a 0
            if saldo_hoy > 0 or saldo_ayer > 0:
                tiene_productos = True
                Saldos.objects.create(
                    sucursal=sucursal,
                    producto=producto_nombre,
                    saldo_hoy=saldo_hoy,
                    saldo_ayer=saldo_ayer,
                    usuario=request.user
                )
                saldos_creados += 1
        
        # Validar que haya al menos un producto
        if not tiene_productos:
            messages.warning(request, 'Debe ingresar al menos un valor en saldo hoy o saldo ayer')
            context = {
                'productos': productos,
                'fecha_actual': timezone.now().strftime('%d/%m/%Y'),
                'saldos_hoy_productos': saldos_hoy_productos,
                'saldos_ayer_productos': saldos_ayer_productos,
                'user_sucursal_id': user_sucursal_id,
            }
            return render(request, 'despacho/saldos_nuevos.html', context)
        
        # ✅ GUARDADO EXITOSO - MANTENER DATOS
        messages.success(
            request, 
            f'✓ Se guardaron {saldos_creados} saldos para {sucursal.nombre_sucursal}'
        )
        
        context = {
            'productos': productos,
            'fecha_actual': timezone.now().strftime('%d/%m/%Y'),
            'saldos_hoy_productos': saldos_hoy_productos,
            'saldos_ayer_productos': saldos_ayer_productos,
            'user_sucursal_id': user_sucursal_id,
        }
        
        return render(request, 'despacho/saldos_nuevos.html', context)
    
    # GET request - Formulario limpio
    productos = Saldos.PRODUCTOS_SALDOS
    
    print("="*60)
    print("🔍 PRODUCTOS PARA SALDOS")
    print("="*60)
    print(f"Total productos: {len(productos)}")
    print(f"Usuario: {request.user.username}")
    print(f"Sucursal: {request.user.first_name}")
    print("\nPrimeros 10 productos:")
    for idx, (nombre, _) in enumerate(productos[:10]):
        print(f"  {idx}. {nombre}")
    print("="*60)
    
    context = {
        'productos': productos,
        'fecha_actual': timezone.now().strftime('%d/%m/%Y'),
        'saldos_hoy_productos': {},
        'saldos_ayer_productos': {},
        'user_sucursal_id': user_sucursal_id,
    }
    
    return render(request, 'despacho/saldos_nuevos.html', context)

##########################   lista de pedidos de excel===============================

@login_required

def lista_pedidos_excel(request):
    hoy = timezone.localdate()

    inicio = timezone.make_aware(datetime.combine(hoy, time.min))
    fin = timezone.make_aware(datetime.combine(hoy, time.max))

    productos = Producto.objects.filter(
        fecha_creacion__range=(inicio, fin)
    )


    #productos = Producto.objects.all()
    sucursales = Sucursales.objects.all().order_by('id')

    # matriz[producto_id][sucursal_id] = cantidad
    matriz = defaultdict(dict)

    detalles = Pedidos.objects.all()

    for d in detalles:
        matriz[d.producto_id][d.sucursal_id] = d.cantidad

    context = {
        'productos': productos,
        'sucursales': sucursales,
        'matriz': matriz,
    }

    return render(request, 'despacho/lista_pedidos.html', context)


def guardar_pedidos(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        usuario = request.user if request.user.is_authenticated else None

        for item in data:
            Pedidos.objects.create(
                producto_id=item['producto'],
                sucursal_id=item['sucursal'],
                cantidad=item['cantidad'],
                usuario=usuario
            )

        return JsonResponse({'status': 'ok'})
    
   
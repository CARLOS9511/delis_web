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
from .models import Venta, DetalleVenta
from despacho.models import Despacho
from produccion.models import Producto_venta, Categoria
from .forms import VentaForm, DetalleVentaFormSet
import json
from django.db import transaction


# ==================== FUNCIONES AUXILIARES ====================
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


# ==================== LISTA DE VENTAS ====================
@login_required
def venta_lista(request):
    """Vista para listar ventas con filtros"""
    ventas = Venta.objects.select_related(
        'despacho__sucursal', 'usuario',
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
        ventas = ventas.filter(
            Q(numero__icontains=search) |
            Q(despacho__sucursal__nombre_sucursal__icontains=search) |
            Q(chofer__icontains=search) |
            Q(tanda__icontains=search)
        )
    
    if estado:
        ventas = ventas.filter(estado=estado)
    
    if sucursal_id:
        ventas = ventas.filter(despacho__sucursal_id=sucursal_id)
        
    if fecha:
        fecha_hasta_dt = datetime.strptime(fecha, '%Y-%m-%d')
        from django.utils import timezone
        fecha_hasta_dt = timezone.make_aware(
            datetime.combine(fecha_hasta_dt, datetime.max.time())
        )
        ventas = ventas.filter(fecha_creacion__lte=fecha_hasta_dt)
    
    if fecha_desde:
        fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
        ventas = ventas.filter(fecha_creacion__gte=fecha_desde_dt)
    
    if fecha_hasta:
        fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
        from django.utils import timezone
        fecha_hasta_dt = timezone.make_aware(
            datetime.combine(fecha_hasta_dt, datetime.max.time())
        )
        ventas = ventas.filter(fecha_creacion__lte=fecha_hasta_dt)
    
    # Estadísticas
    stats = {
        'pendientes': ventas.filter(estado='pendiente').count(),
        'completadas': ventas.filter(estado='completada').count(),
        'canceladas': ventas.filter(estado='cancelada').count(),
    }
    
    # Paginación
    paginator = Paginator(ventas, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener todos los despachos para el filtro
    from sucursales.models import Sucursales
    sucursales = Sucursales.objects.all()
    
    context = {
        'ventas': page_obj,
        'sucursales': sucursales,
        'stats': stats,
    }
    
    return render(request, 'ventas/lista_venta.html', context)


# ==================== CREAR VENTA ====================
@login_required
def venta_crear(request):
    """Vista para crear una nueva venta"""
    
    # Obtener despacho_id si se pasa por parámetro
    despacho_id = request.GET.get('despacho_id')
    despacho_seleccionado = None
    
    if despacho_id:
        try:
            despacho_seleccionado = Despacho.objects.get(pk=despacho_id, estado='completada')
        except Despacho.DoesNotExist:
            messages.warning(request, "Despacho no encontrado o no está completado")
            despacho_id = None
    
    if request.method == "POST":
        form = VentaForm(request.POST)
        
        # Asignar el usuario actual
        if form.is_valid():
            form.instance.usuario = request.user

        if form.is_valid():
            try:
                with transaction.atomic():
                    venta = form.save()
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
                            producto_venta = Producto_venta.objects.select_for_update().get(id=prod_id)
                            
                            if producto_venta.stock < cantidad:
                                raise Exception(
                                    f"Stock insuficiente para {producto_venta.nombre}. "
                                    f"Disponible: {producto_venta.stock}, Solicitado: {cantidad}"
                                )
                            
                            subtotal = cantidad * precio
                            total += subtotal

                            # Crear detalle
                            DetalleVenta.objects.create(
                                venta=venta,
                                producto_venta=producto_venta,
                                cantidad=cantidad,
                                precio_unitario=precio,
                                subtotal=subtotal
                            )
                            
                            # ⭐ DESCONTAR STOCK
                            producto_venta.stock -= cantidad
                            producto_venta.save()
                            
                            detalles_guardados += 1

                    if detalles_guardados == 0:
                        raise Exception("Debe agregar al menos un producto con cantidad mayor a 0")

                    # Guardar totales de la venta
                    venta.subtotal = total
                    venta.descuento = limpiar_numero(venta.descuento)
                    venta.total = total - venta.descuento
                    venta.save()

                    messages.success(
                        request, 
                        f"✅ Venta {venta.numero} creada con {detalles_guardados} productos. "
                        f"Stock actualizado."
                    )
                    return redirect("ventas:venta_lista")

            except Producto_venta.DoesNotExist:
                messages.error(request, "❌ Uno de los productos no existe")
            except Exception as e:
                messages.error(request, f"❌ Error: {str(e)}")
        else:
            messages.error(request, "Por favor corrija los errores en el formulario")

    else:
        form = VentaForm()
        # Si hay un despacho seleccionado, establecerlo como inicial
        if despacho_seleccionado:
            form.fields['despacho'].initial = despacho_seleccionado.id
    
    # ⭐ OBTENER TODOS LOS DESPACHOS COMPLETADOS para el select
    despachos_disponibles = Despacho.objects.filter(estado='completada').select_related('sucursal').order_by('-fecha_creacion')
    
    # ⭐ OBTENER PRODUCTOS DE LA SUCURSAL DEL DESPACHO
    if despacho_seleccionado:
        sucursal = despacho_seleccionado.sucursal
        todos_productos = Producto_venta.objects.filter(
            activo=True, 
            sucursal_venta=sucursal
        ).select_related('categoria').order_by('categoria__nombre', 'nombre')
    else:
        todos_productos = Producto_venta.objects.none()
    
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

    return render(request, "ventas/form_venta.html", {
        "form": form,
        "productos_por_categoria": dict(productos_por_categoria),
        "total_productos_count": indice_global,
        "accion": "Crear",
        "venta": None,
        "despacho_seleccionado": despacho_seleccionado,
        "despachos_disponibles": despachos_disponibles,
    })


# ==================== DETALLE VENTA ====================
@login_required
def venta_detalle(request, pk):
    """Ver detalle de una venta"""
    venta = get_object_or_404(Venta, pk=pk)
    detalles = venta.detalles.all().select_related('producto_venta')
    
    context = {
        'venta': venta,
        'detalles': detalles,
    }
    
    return render(request, 'ventas/detalle_venta.html', context)


# ==================== EDITAR VENTA ====================
@login_required
def venta_editar(request, pk):
    """Vista para editar una venta existente"""
    venta = get_object_or_404(Venta, pk=pk)

    if request.method == "POST":
        form = VentaForm(request.POST, instance=venta)

        if form.is_valid():
            try:
                with transaction.atomic():
                    # Restaurar stock de productos anteriores
                    for detalle in venta.detalles.all():
                        producto_venta = Producto_venta.objects.select_for_update().get(id=detalle.producto_venta_id)
                        producto_venta.stock += detalle.cantidad
                        producto_venta.save()
                    
                    # Eliminar detalles anteriores
                    venta.detalles.all().delete()
                    
                    # Actualizar venta
                    venta = form.save()
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
                            producto_venta = Producto_venta.objects.select_for_update().get(id=prod_id)
                            
                            if producto_venta.stock < cantidad:
                                raise Exception(
                                    f"Stock insuficiente para {producto_venta.nombre}. "
                                    f"Disponible: {producto_venta.stock}, Solicitado: {cantidad}"
                                )
                            
                            subtotal = cantidad * precio
                            total += subtotal

                            DetalleVenta.objects.create(
                                venta=venta,
                                producto_venta=producto_venta,
                                cantidad=cantidad,
                                precio_unitario=precio,
                                subtotal=subtotal
                            )
                            
                            producto_venta.stock -= cantidad
                            producto_venta.save()
                            
                            detalles_guardados += 1

                    if detalles_guardados == 0:
                        raise Exception("Debe agregar al menos un producto")

                    # Actualizar totales de la venta
                    venta.subtotal = total
                    venta.descuento = limpiar_numero(venta.descuento)
                    venta.total = total - venta.descuento
                    venta.save()

                    messages.success(
                        request, 
                        f"✅ Venta {venta.numero} actualizada correctamente."
                    )
                    return redirect("ventas:venta_lista")

            except Exception as e:
                messages.error(request, f"❌ Error: {str(e)}")
        else:
            messages.error(request, "Corrija los errores del formulario")

    else:
        form = VentaForm(instance=venta)

    # AGRUPAR PRODUCTOS POR CATEGORÍA CON DATOS ACTUALES
    sucursal = venta.despacho.sucursal
    todos_productos = Producto_venta.objects.filter(
        activo=True,
        sucursal_venta=sucursal
    ).select_related('categoria').order_by('categoria__nombre', 'nombre')
    
    detalles_dict = {d.producto_venta.id: d for d in venta.detalles.all()}
    
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

    return render(request, "ventas/form_venta.html", {
        "form": form,
        "productos_por_categoria": dict(productos_por_categoria),
        "total_productos_count": indice_global,
        "venta": venta,
        "accion": "Editar",
        "despacho_seleccionado": venta.despacho,
    })


# ==================== CANCELAR VENTA ====================
@login_required
@require_POST
def venta_cancelar(request, pk):
    """Vista para cancelar una venta"""
    venta = get_object_or_404(Venta, pk=pk)
    
    if venta.estado != 'pendiente':
        messages.error(request, 'Solo se pueden cancelar ventas pendientes.')
    else:
        try:
            with transaction.atomic():
                # Restaurar stock al cancelar
                for detalle in venta.detalles.all():
                    producto_venta = Producto_venta.objects.select_for_update().get(id=detalle.producto_venta_id)
                    producto_venta.stock += detalle.cantidad
                    producto_venta.save()
                
                venta.estado = 'cancelada'
                venta.save()
                messages.success(request, f'Venta {venta.numero} cancelada. Stock restaurado.')
        except Exception as e:
            messages.error(request, f'Error al cancelar: {str(e)}')
    
    return redirect('ventas:venta_lista')


# ==================== COMPLETAR VENTA ====================
@login_required
@require_POST
def venta_completar(request, pk):
    """Vista para marcar una venta como completada"""
    venta = get_object_or_404(Venta, pk=pk)
    
    if venta.estado != 'pendiente':
        messages.error(request, 'Solo se pueden completar ventas pendientes.')
    else:
        venta.estado = 'completada'
        venta.save()
        messages.success(request, f'Venta {venta.numero} completada.')
    
    return redirect('ventas:venta_detalle', pk=venta.id)


# ==================== GENERAR PDF ====================
@login_required
def venta_pdf(request, pk):
    """Vista para generar PDF de la venta"""
    from django.template.loader import get_template
    from weasyprint import HTML
    
    venta = get_object_or_404(
        Venta.objects.select_related('despacho__sucursal', 'usuario')
        .prefetch_related('detalles__producto_venta'),
        pk=pk
    )
    
    template = get_template('ventas/pdf_venta.html')
    context = {'venta': venta}
    html_string = template.render(context)
    
    # Generar PDF
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()
    
    # Retornar PDF
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="venta_{venta.numero}.pdf"'
    
    return response


# ==================== API: OBTENER PRECIO PRODUCTO VENTA ====================
@login_required
def obtener_precio_producto_venta(request, producto_id):
    """API para obtener el precio de un producto de venta"""
    try:
        producto = Producto_venta.objects.get(id=producto_id)
        return JsonResponse({
            'success': True,
            'precio': float(producto.precio_venta),
            'nombre': producto.nombre,
            'stock': producto.stock
        })
    except Producto_venta.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Producto no encontrado'
        }, status=404)


# ==================== API: BUSCAR PRODUCTOS DE VENTA ====================
@login_required
def buscar_productos_venta(request):
    """API para buscar productos de venta por nombre o código"""
    query = request.GET.get('q', '')
    despacho_id = request.GET.get('despacho_id', '')
    
    if len(query) < 2:
        return JsonResponse({'productos': []})
    
    # Filtrar por sucursal si hay despacho
    productos = Producto_venta.objects.filter(
        Q(nombre__icontains=query) | Q(codigo__icontains=query),
        activo=True
    )
    
    if despacho_id:
        try:
            despacho = Despacho.objects.get(id=despacho_id)
            productos = productos.filter(sucursal_venta=despacho.sucursal)
        except Despacho.DoesNotExist:
            pass
    
    productos = productos[:10]
    
    resultados = [{
        'id': p.id,
        'nombre': p.nombre,
        'codigo': p.codigo,
        'precio': float(p.precio_venta),
        'stock': p.stock,
    } for p in productos]
    
    return JsonResponse({'productos': resultados})


# ==================== API: OBTENER PRODUCTOS POR DESPACHO ====================
@login_required
def obtener_productos_por_despacho(request, despacho_id):
    """API para obtener productos de venta de la sucursal del despacho"""
    try:
        despacho = Despacho.objects.get(id=despacho_id)
        productos = Producto_venta.objects.filter(
            activo=True,
            sucursal_venta=despacho.sucursal
        ).select_related('categoria').order_by('categoria__nombre', 'nombre')
        
        productos_por_categoria = defaultdict(list)
        
        for producto in productos:
            producto_data = {
                'id': producto.id,
                'nombre': producto.nombre,
                'codigo': producto.codigo,
                'stock': producto.stock,
                'precio_venta': float(producto.precio_venta),
            }
            categoria_nombre = producto.categoria.nombre if producto.categoria else 'Sin Categoría'
            productos_por_categoria[categoria_nombre].append(producto_data)
        
        return JsonResponse({
            'success': True,
            'productos_por_categoria': dict(productos_por_categoria),
            'sucursal': despacho.sucursal.nombre_sucursal
        })
    except Despacho.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Despacho no encontrado'
        }, status=404)


# ==================== ELIMINAR VENTA ====================
@login_required
def venta_eliminar(request, pk):
    """Vista para eliminar una venta"""
    venta = get_object_or_404(Venta, pk=pk)

    if request.method == "POST":
        try:
            with transaction.atomic():
                # ⭐ RESTAURAR STOCK ANTES DE ELIMINAR
                for detalle in DetalleVenta.objects.filter(venta=venta):
                    producto_venta = Producto_venta.objects.select_for_update().get(id=detalle.producto_venta_id)
                    producto_venta.stock += detalle.cantidad
                    producto_venta.save()
                
                numero = venta.numero
                venta.delete()
                
                messages.success(request, f"✅ Venta {numero} eliminada. Stock restaurado.")
        except Exception as e:
            messages.error(request, f"❌ Error al eliminar: {str(e)}")
        
        return redirect("ventas:venta_lista")

    return render(request, "ventas/venta_eliminar.html", {
        "venta": venta
    })
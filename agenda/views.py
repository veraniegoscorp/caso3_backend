import csv
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import ContactoForm
from .models import contacto

def mostrar_agenda(request):
    """
    Vista principal de la agenda: listado con búsqueda, paginación,
    validación de formulario de creación y feedback con mensajes.
    """
    q = request.GET.get('q', '').strip()
    
    # Filtrado según término de búsqueda
    if q:
        contactos_qs = contacto.objects.filter(
            Q(nombre__icontains=q) | 
            Q(correo__icontains=q) |
            Q(telefono__icontains=q) |
            Q(direccion__icontains=q)
        ).order_by('-id')
    else:
        contactos_qs = contacto.objects.all().order_by('-id')

    # Manejo del formulario de creación
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            try:
                nuevo_contacto = form.save()
                messages.success(
                    request, 
                    f'✨ ¡Contacto "{nuevo_contacto.nombre}" registrado exitosamente!'
                )
                return redirect('mostrar_agenda')
            except Exception as e:
                messages.error(
                    request, 
                    f'Ocurrió un error al intentar guardar el contacto: {str(e)}'
                )
        else:
            messages.error(
                request, 
                '⚠️ No se pudo guardar el contacto. Revisa los campos resaltados.'
            )
    else:
        form = ContactoForm()

    # Paginación (6 contactos por página)
    paginator = Paginator(contactos_qs, 6)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    total_contactos = contacto.objects.count()

    context = {
        'page_obj': page_obj,
        'contactos': page_obj,
        'form': form,
        'q': q,
        'total_contactos': total_contactos,
        'total_filtrados': contactos_qs.count(),
    }
    return render(request, 'contactos/contactos.html', context)


def eliminar_contacto(request, pk):
    """
    Permite eliminar un contacto con confirmación y mensaje de feedback.
    """
    contacto_obj = get_object_or_404(contacto, pk=pk)
    nombre = contacto_obj.nombre
    try:
        contacto_obj.delete()
        messages.warning(request, f'🗑️ El contacto "{nombre}" fue eliminado del sistema.')
    except Exception as e:
        messages.error(request, f'Error al eliminar el contacto: {str(e)}')
    return redirect('mostrar_agenda')


def exportar_contactos_csv(request):
    """
    Exporta el listado completo o filtrado de contactos a un archivo CSV en casillas individuales con UTF-8 BOM.
    """
    q = request.GET.get('q', '').strip()
    if q:
        contactos_qs = contacto.objects.filter(
            Q(nombre__icontains=q) | 
            Q(correo__icontains=q) |
            Q(telefono__icontains=q) |
            Q(direccion__icontains=q)
        ).order_by('-id')
    else:
        contactos_qs = contacto.objects.all().order_by('-id')

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="contactos_agenda.csv"'

    # Escribir BOM para correcta apertura en Excel en columnas separadas
    response.write('\ufeff'.encode('utf-8'))
    writer = csv.writer(response, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['ID', 'Nombre Completo', 'Teléfono', 'Correo Electrónico', 'Dirección'])

    for c in contactos_qs:
        writer.writerow([
            c.id, 
            str(c.nombre).strip(), 
            str(c.telefono).strip(), 
            str(c.correo).strip(), 
            str(c.direccion).strip()
        ])

    return response

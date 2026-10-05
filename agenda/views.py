import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
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

    if q:
        contactos_qs = contacto.objects.filter(
            Q(nombre__icontains=q) |
            Q(correo__icontains=q) |
            Q(telefono__icontains=q) |
            Q(direccion__icontains=q)
        ).order_by('-id')
    else:
        contactos_qs = contacto.objects.all().order_by('-id')

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
    Genera un archivo .xlsx real de Excel con cada campo en su propia casilla,
    encabezados estilizados y columnas auto-ajustadas.
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

    wb = Workbook()
    ws = wb.active
    ws.title = "Contactos"

    # Estilos para encabezados
    header_font = Font(name='Calibri', bold=True, color='FFFFFF', size=11)
    header_fill = PatternFill(start_color='1E293B', end_color='1E293B', fill_type='solid')
    header_align = Alignment(horizontal='center', vertical='center')
    thin_border = Border(
        left=Side(style='thin', color='D4AF37'),
        right=Side(style='thin', color='D4AF37'),
        top=Side(style='thin', color='D4AF37'),
        bottom=Side(style='thin', color='D4AF37'),
    )

    # Encabezados
    headers = ['ID', 'Nombre Completo', 'Teléfono', 'Correo Electrónico', 'Dirección']
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align
        cell.border = thin_border

    # Datos
    data_font = Font(name='Calibri', size=10)
    data_align = Alignment(vertical='center')
    for row_num, c in enumerate(contactos_qs, 2):
        values = [c.id, c.nombre, c.telefono, c.correo, c.direccion]
        for col_num, value in enumerate(values, 1):
            cell = ws.cell(row=row_num, column=col_num, value=value)
            cell.font = data_font
            cell.alignment = data_align
            cell.border = thin_border

    # Auto-ajustar anchos de columna
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter
        for cell in col:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        ws.column_dimensions[col_letter].width = max_length + 4

    # Escribir a bytes
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="contactos_agenda.xlsx"'
    return response

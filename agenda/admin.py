import csv
from django.contrib import admin, messages
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from .models import contacto
from .forms import ContactoForm

# Personalización del encabezado y títulos del Admin
admin.site.site_header = "💼 Panel de Control Corporativo"
admin.site.site_title = "Agenda VIP Admin"
admin.site.index_title = "Panel de Gestión y Contactos"
admin.site.index_template = "admin/agenda_index.html"


@admin.action(description="📥 Exportar contactos seleccionados a archivo CSV")
def exportar_contactos_a_csv(modeladmin, request, queryset):
    """
    Acción de Django Admin para exportar registros seleccionados a CSV con soporte Excel (UTF-8 BOM).
    """
    try:
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="contactos_exportados_admin.csv"'
        response.write('\ufeff'.encode('utf-8')) # BOM UTF-8

        writer = csv.writer(response, delimiter=';')
        writer.writerow(['ID', 'Nombre Completo', 'Teléfono', 'Correo Electrónico', 'Dirección'])

        count = 0
        for obj in queryset:
            writer.writerow([obj.id, obj.nombre, obj.telefono, obj.correo, obj.direccion])
            count += 1

        messages.success(request, f'✅ ¡Exportación exitosa! Se han exportado {count} contacto(s) a CSV.')
        return response
    except Exception as ex:
        messages.error(request, f'❌ Error al generar la exportación CSV: {str(ex)}')
        return None


@admin.register(contacto)
class ContactoAdmin(admin.ModelAdmin):
    form = ContactoForm
    
    # Columnas mostradas en el listado
    list_display = ('id', 'nombre', 'telefono', 'correo', 'direccion')
    list_display_links = ('id', 'nombre')
    
    # Edición rápida desde la tabla
    list_editable = ('telefono', 'correo', 'direccion')
    
    # Barra de búsqueda universal
    search_fields = ('nombre', 'correo', 'telefono', 'direccion')
    
    # Filtros laterales
    list_filter = ('nombre',)
    
    # Paginación para cumplir con el requisito de interfaz
    list_per_page = 10
    list_max_show_all = 100
    
    # Orden predeterminado
    ordering = ('-id',)
    
    # Acciones personalizadas
    actions = [exportar_contactos_a_csv]

    # Inyección de CSS personalizado centrado y moderno
    class Media:
        css = {
            'all': ('admin/css/custom.css',)
        }

    def save_model(self, request, obj, form, change):
        """
        Manejo de errores y validación al guardar registros en el Admin.
        """
        try:
            super().save_model(request, obj, form, change)
            accion = "actualizado" if change else "creado"
            messages.success(request, f'✨ Contacto "{obj.nombre}" {accion} con éxito en el sistema.')
        except ValidationError as ve:
            messages.error(request, f'⚠️ Error de validación: {ve}')
            raise ve
        except Exception as e:
            messages.error(request, f'❌ Error inesperado al guardar contacto: {str(e)}')
            raise e

    def delete_model(self, request, obj):
        """
        Feedback al eliminar un contacto individual desde el Admin.
        """
        nombre = obj.nombre
        try:
            super().delete_model(request, obj)
            messages.warning(request, f'🗑️ El contacto "{nombre}" fue eliminado del panel administrativo.')
        except Exception as e:
            messages.error(request, f'❌ Error al eliminar el contacto: {str(e)}')
            raise e

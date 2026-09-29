from django.contrib import admin
from .models import contacto

# Personalización del sitio admin
admin.site.site_header = "📇 Panel de Administración – Agenda"
admin.site.site_title = "Agenda Admin"
admin.site.index_title = "Gestión de Contactos"
admin.site.index_template = "admin/agenda_index.html"

@admin.register(contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'correo', 'direccion')
    list_editable = ('telefono', 'correo', 'direccion')
    search_fields = ('nombre', 'correo')
    list_filter = ('nombre',)
    list_per_page = 25
    ordering = ('-id',)

    class Media:
        css = {
            'all': ('admin/css/custom.css',)
        }

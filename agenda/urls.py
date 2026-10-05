from django.urls import path
from . import views

urlpatterns = [
    path('', views.mostrar_agenda, name='mostrar_agenda'),
    path('eliminar/<int:pk>/', views.eliminar_contacto, name='eliminar_contacto'),
    path('exportar-csv/', views.exportar_contactos_csv, name='exportar_contactos_csv'),
]
from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from agenda.api import router

urlpatterns = [
    path('', views.mostrar_agenda, name='mostrar_agenda'),
    path('eliminar/<int:pk>/', views.eliminar_contacto, name='eliminar_contacto'),
    path('exportar-csv/', views.exportar_contactos_csv, name='exportar_contactos_csv'),
    path("api-auth/", include("rest_framework.urls")),
    path("api/", include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
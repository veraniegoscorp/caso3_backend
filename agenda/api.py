from rest_framework import routers, viewsets

from .models import contacto
from .serializers import ContactoSerializer

class ContactoViewset(viewsets.ModelViewSet):
    queryset = contacto.objects.all()
    serializer_class = ContactoSerializer

router = routers.DefaultRouter()
router.register(r'Contactos', ContactoViewset)

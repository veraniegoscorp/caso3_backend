from types import SimpleNamespace
from django.urls import reverse
from rest_framework.settings import api_settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from .models import contacto
from .serializers import ContactoSerializer


class ContactoSerializerTests(SimpleTestCase):
	def test_rejects_invalid_contact_data(self):
		serializer = ContactoSerializer(data={
			'nombre': 'Ana1',
			'telefono': 1234567,
			'correo': 'ana@example.com',
			'direccion': 'Calle 123',
		})

		self.assertFalse(serializer.is_valid())
		self.assertIn('nombre', serializer.errors)

	def test_normalizes_contact_data(self):
		serializer = ContactoSerializer(data={
			'nombre': '  Ana Pérez  ',
			'telefono': 1234567,
			'correo': ' ANA@EXAMPLE.COM ',
			'direccion': '  Calle 123  ',
		})

		self.assertTrue(serializer.is_valid(), serializer.errors)
		self.assertEqual(serializer.validated_data['nombre'], 'Ana Pérez')
		self.assertEqual(serializer.validated_data['correo'], 'ana@example.com')
		self.assertEqual(serializer.validated_data['direccion'], 'Calle 123')

	def test_validates_partial_update_against_existing_instance(self):
		instance = contacto(
			nombre='Ana Pérez',
			telefono=1234567,
			correo='ana@example.com',
			direccion='Calle 123',
		)
		serializer = ContactoSerializer(
			instance,
			data={'direccion': 'X'},
			partial=True,
		)

		self.assertFalse(serializer.is_valid())
		self.assertIn('direccion', serializer.errors)


class ContactoApiRoutesTests(SimpleTestCase):
	def test_contact_collection_and_detail_routes(self):
		self.assertEqual(reverse('contacto-list'), '/api/contactos/')
		self.assertEqual(reverse('contacto-detail', args=[42]), '/api/contactos/42/')

	def test_jwt_routes_use_trailing_slashes(self):
		self.assertEqual(reverse('token_obtain_pair'), '/api/token/')
		self.assertEqual(reverse('token_refresh'), '/api/token/refresh/')


class JwtApiTests(SimpleTestCase):
	def setUp(self):
		self.client = APIClient(HTTP_HOST='127.0.0.1')

	def test_api_defaults_to_jwt_and_authenticated_access(self):
		self.assertEqual(list(api_settings.DEFAULT_AUTHENTICATION_CLASSES), [JWTAuthentication])
		self.assertEqual(list(api_settings.DEFAULT_PERMISSION_CLASSES), [IsAuthenticated])

	def test_contact_endpoints_reject_unauthenticated_requests(self):
		response = self.client.get(reverse('contacto-list'))

		self.assertEqual(response.status_code, 401)

	def test_token_obtain_endpoint_is_public(self):
		response = self.client.post(reverse('token_obtain_pair'), {}, format='json')

		self.assertEqual(response.status_code, 400)

	def test_refresh_endpoint_returns_new_access_token(self):
		refresh_token = str(RefreshToken())
		response = self.client.post(
			reverse('token_refresh'),
			{'refresh': refresh_token},
			format='json',
		)

		self.assertEqual(response.status_code, 200)
		self.assertIn('access', response.data)

from django.contrib.auth.models import AnonymousUser
from django.test import Client, RequestFactory, SimpleTestCase, override_settings
from django.urls import reverse

from . import views


class AccessControlTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_anonymous_users_are_redirected_to_admin_login(self):
        endpoints = (
            (reverse('mostrar_agenda'), views.mostrar_agenda, {}),
            (reverse('exportar_contactos_csv'), views.exportar_contactos_csv, {}),
            (
                reverse('eliminar_contacto', args=(1,)),
                views.eliminar_contacto,
                {'pk': 1},
            ),
        )

        for path, view, kwargs in endpoints:
            with self.subTest(path=path):
                request = self.factory.get(path)
                request.user = AnonymousUser()

                response = view(request, **kwargs)

                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.url.startswith('/admin/login/?next='))

    def test_export_only_accepts_get(self):
        request = self.factory.post(reverse('exportar_contactos_csv'))
        request.user = SimpleNamespace(is_authenticated=True)

        response = views.exportar_contactos_csv(request)

        self.assertEqual(response.status_code, 405)

    def test_delete_only_accepts_post(self):
        request = self.factory.get(reverse('eliminar_contacto', args=(1,)))
        request.user = SimpleNamespace(is_authenticated=True)

        response = views.eliminar_contacto(request, pk=1)

        self.assertEqual(response.status_code, 405)


class CorsConfigurationTests(SimpleTestCase):
    @override_settings(CORS_ALLOWED_ORIGINS=['https://client.example.com'])
    def test_allowed_origin_receives_cors_headers_and_credentials_support(self):
        response = Client().get(
            reverse('mostrar_agenda'),
            HTTP_ORIGIN='https://client.example.com',
        )

        self.assertEqual(
            response['Access-Control-Allow-Origin'],
            'https://client.example.com',
        )
        self.assertEqual(response['Access-Control-Allow-Credentials'], 'true')

    @override_settings(CORS_ALLOWED_ORIGINS=['https://client.example.com'])
    def test_unlisted_origin_does_not_receive_cors_headers(self):
        response = Client().get(
            reverse('mostrar_agenda'),
            HTTP_ORIGIN='https://untrusted.example.com',
        )

        self.assertNotIn('Access-Control-Allow-Origin', response)

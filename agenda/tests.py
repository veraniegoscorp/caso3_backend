from types import SimpleNamespace

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

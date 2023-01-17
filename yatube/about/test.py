from http import HTTPStatus

from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_url_get_correct_template(self):
        """Проверка шаблонов для адресов /about/*."""
        templates_urls = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for url, template in templates_urls.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)

    def test_about_urls_exists_at_desired_location(self):
        """Проверка доступности адресов /about/*."""
        urls = {
            '/about/author/',
            '/about/tech/',
        }
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

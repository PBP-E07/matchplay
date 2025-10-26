from django.http import JsonResponse
from django.test import TestCase, Client
from django.template.loader import render_to_string
from django.urls import reverse
from fields.models import Field, Facility
from fields.forms import FieldForm
import json

class DashboardViewTests(TestCase):
    def setUp(self):
        # Buat dummy facility
        self.facility_wifi = Facility.objects.create(name='WiFi')
        self.facility_parkir = Facility.objects.create(name='Parkir')

        # Buat data field
        self.client = Client()
        self.field = Field.objects.create(
            name="Lapangan Futsal A",
            image="http://example.com/image.jpg",
            price=50000,
            rating="4.5",
            location="Jakarta",
            sport="futsal",
            url="http://example.com"
        )
        self.field.facilities.set([self.facility_wifi, self.facility_parkir])

    # === DASHBOARD_HOME TESTS ===
    def test_dashboard_home_renders(self):
        """Halaman dashboard utama dapat diakses"""
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/home.html')
        self.assertIn('total_fields', response.context)
        self.assertIn('avg_price', response.context)
        self.assertIn('page_obj', response.context)

    def test_dashboard_home_filter_category(self):
        """Filter kategori bekerja dengan benar"""
        Field.objects.create(
            name="Lapangan Badminton B",
            image="http://example.com/img2.jpg",
            price=70000,
            rating="4.0",
            location="Bandung",
            sport="badminton",
            url="http://example.com/2"
        )
        response = self.client.get(reverse('dashboard_home'), {'category': 'futsal'})
        self.assertContains(response, "Lapangan Futsal A")
        self.assertNotContains(response, "Lapangan Badminton B")

    def test_dashboard_home_filter_max_price(self):
        """Filter berdasarkan rentang harga"""
        Field.objects.create(
            name="Lapangan Golf",
            image="http://example.com/img3.jpg",
            price=300000,
            rating="4.8",
            location="Bali",
            sport="golf",
            url="http://example.com/3"
        )
        response = self.client.get(reverse('dashboard_home'), {'min_price': 300000})
        self.assertContains(response, "Lapangan Golf")
        self.assertNotContains(response, "Lapangan Futsal A")

    def test_dashboard_home_filter_min_price(self):
        """Filter berdasarkan rentang harga"""
        Field.objects.create(
            name="Lapangan Golf",
            image="http://example.com/img3.jpg",
            price=300000,
            rating="4.8",
            location="Bali",
            sport="golf",
            url="http://example.com/3"
        )
        response = self.client.get(reverse('dashboard_home'), {'max_price': 100000})
        self.assertContains(response, "Lapangan Futsal A")
        self.assertNotContains(response, "Lapangan Golf")

    def test_dashboard_home_ajax_request(self):
        """AJAX request harus mengembalikan JSON dengan table_html"""
        response = self.client.get(
            reverse('dashboard_home'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('table_html', data)
        self.assertIn('pagination_html', data)
        self.assertIn('avg_price', data)

    # === ADD FIELD ===
    def test_add_field_valid(self):
        """Tambah field baru via AJAX"""
        data = {
            'name': 'Lapangan Basket',
            'image': 'http://example.com/img.jpg',
            'price': 100000,
            'rating': '4.0',
            'location': 'Surabaya',
            'sport': 'basketball',
            'url': 'http://example.com/basket',
        }
        response = self.client.post(reverse('add_field_ajax'), data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        self.assertTrue(Field.objects.filter(name='Lapangan Basket').exists())

    def test_add_field_invalid(self):
        """Tambah field gagal jika data tidak valid"""
        data = {'name': '', 'price': 'abc'}
        response = self.client.post(reverse('add_field_ajax'), data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertFalse(content['success'])
        self.assertIn('form_html', content)

    def test_add_field_get_method(self):
        """Pastikan GET ke add_field_ajax mengembalikan JSON dengan form_html"""
        url = reverse('add_field_ajax')
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('form_html', data)
        form = FieldForm()
        for field_name in form.fields:
            self.assertIn(field_name, data['form_html'])
            
    # === EDIT FIELD ===
    def test_edit_field_valid(self):
        """Edit existing field"""
        url = reverse('edit_field_ajax', args=[self.field.pk])
        data = {
            'name': 'Lapangan Futsal Edited',
            'image': self.field.image,
            'price': 60000,
            'rating': self.field.rating,
            'location': self.field.location,
            'sport': self.field.sport,
            'url': self.field.url,
        }
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.field.refresh_from_db()
        self.assertEqual(self.field.name, 'Lapangan Futsal Edited')

    def test_edit_field_invalid(self):
        """Edit field gagal dengan data tidak valid"""
        url = reverse('edit_field_ajax', args=[self.field.pk])
        response = self.client.post(url, {'name': ''}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        content = json.loads(response.content)
        self.assertFalse(content['success'])
        self.assertIn('form_html', content)


    def test_edit_field_get_method(self):
        """Pastikan GET ke edit_field_ajax mengembalikan JSON dengan form_html"""
        url = reverse('edit_field_ajax', args=[self.field.pk])
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('form_html', data)
        form = FieldForm()
        for field_name in form.fields:
            self.assertIn(field_name, data['form_html'])

    # === DELETE FIELD ===
    def test_delete_field(self):
        """Hapus field via AJAX"""
        url = reverse('delete_field_ajax', args=[self.field.pk])
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Field.objects.filter(pk=self.field.pk).exists())

    # === FILTER PANEL ===
    def test_filter_panel_returns_html(self):
        """Filter panel harus mengembalikan HTML"""
        response = self.client.get(reverse('filter_panel'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('html', data)

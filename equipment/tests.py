from django.test import TestCase
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import Equipment, Rental

# --- Data Setup ---
class EquipmentTests(TestCase):
    def setUp(self):
        # 1. Setup User (Admin & Regular)
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin', 
            password='password123', 
            email='admin@test.com'
        )
        self.regular_user = User.objects.create_user(
            username='user', 
            password='password123', 
            email='user@test.com'
        )
        
        # 2. Setup Equipment Object
        self.equipment = Equipment.objects.create(
            name='Kamera A6000',
            quantity=5,
            price_per_hour=Decimal('15.00'),
            description='Kamera mirrorless',
        )
        
        # 3. Setup Rental Object
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(hours=4) # Durasi 4 jam
        self.rental = Rental.objects.create(
            equipment=self.equipment,
            renter_name='Budi',
            start_time=self.start_time,
            end_time=self.end_time,
            # total_cost dihitung otomatis oleh method save()
        )
        
        # 4. Setup URLs
        self.list_url = reverse('equipment:equipment_list')
        self.add_url = reverse('equipment:add_equipment')
        self.detail_url = reverse('equipment:equipment_detail_json', args=[self.equipment.id])
        self.edit_url = reverse('equipment:edit_equipment', args=[self.equipment.id])
        self.delete_url = reverse('equipment:delete_equipment', args=[self.equipment.id])

# ----------------------------------------------------
# 1. PENGUJIAN MODEL (models.py)
# ----------------------------------------------------

class ModelTest(EquipmentTests):
    
    def test_equipment_string_representation(self):
        """Test 1.1: Memastikan representasi string Equipment benar."""
        self.assertEqual(str(self.equipment), 'Kamera A6000')

    def test_rental_total_cost_calculation(self):
        """Test 1.2: Memastikan total_cost dihitung otomatis dan akurat."""
        # Harga per jam = 15.00, Durasi = 4 jam. Harusnya 60.00
        expected_cost = Decimal('4.00') * self.equipment.price_per_hour
        self.assertEqual(self.rental.total_cost, expected_cost)

    def test_rental_string_representation(self):
        """Test 1.3: Memastikan representasi string Rental benar."""
        self.assertEqual(str(self.rental), 'Budi - Kamera A6000')


# ----------------------------------------------------
# 2. PENGUJIAN KEAMANAN (views.py Decorators)
# ----------------------------------------------------

class SecurityTest(EquipmentTests):

    def test_list_view_redirects_for_anonymous_user(self):
        """Test 2.1: Pengguna anonim harus diredirect ke login untuk melihat list."""
        response = self.client.get(self.list_url)
        # 302 adalah kode status untuk Redirect
        self.assertEqual(response.status_code, 302) 
        # Memastikan diarahkan ke halaman login
        self.assertTrue('login' in response.url) 

    def test_admin_functions_fail_for_regular_user(self):
        """Test 2.2, 2.3, 2.4: Pengguna biasa tidak boleh mengakses endpoint admin (add, edit, delete)."""
        self.client.login(username='user', password='password123')
        
        # Try to Add Equipment
        response_add = self.client.post(self.add_url, {'name': 'Tes', 'quantity': 1})
        # 403 Forbidden adalah respons dari @user_passes_test
        self.assertEqual(response_add.status_code, 403) 
        
        # Try to Edit Equipment
        response_edit = self.client.post(self.edit_url, {'name': 'Tes Update'})
        self.assertEqual(response_edit.status_code, 403)
        
        # Try to Delete Equipment
        response_delete = self.client.post(self.delete_url)
        self.assertEqual(response_delete.status_code, 403)

# ----------------------------------------------------
# 3. PENGUJIAN FUNGSI CRUD ADMIN (views.py)
# ----------------------------------------------------

class CRUDTest(EquipmentTests):

    def test_equipment_list_success(self):
        """Memastikan Admin/Staff berhasil melihat list alat."""
        self.client.login(username='admin', password='password123')
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/list.html')
        # Memastikan equipment yang dibuat di setUp muncul di konteks
        self.assertEqual(len(response.context['equipments']), 1)

    def test_add_equipment_success(self):
        """Test 3.1: Admin berhasil menambah alat dengan data lengkap."""
        self.client.login(username='admin', password='password123')
        
        # Buat file gambar dummy untuk diunggah
        image_content = b'image_data'
        uploaded_file = SimpleUploadedFile(
            "test_image.jpg", 
            image_content, 
            content_type="image/jpeg"
        )
        
        new_data = {
            'name': 'Tripod Manfrotto',
            'quantity': 10,
            'price_per_hour': 20.50,
            'description': 'Tripod standar',
            'image': uploaded_file
        }
        
        response = self.client.post(self.add_url, new_data)
        
        self.assertEqual(response.status_code, 200)
        
        # Memastikan respons adalah JSON
        json_response = json.loads(response.content)
        self.assertEqual(json_response['name'], 'Tripod Manfrotto')
        
        # Memastikan objek baru benar-benar dibuat di database
        self.assertEqual(Equipment.objects.count(), 2) 

    def test_add_equipment_fail_incomplete_data(self):
        """Test 3.2: Gagal menambah alat jika data tidak lengkap."""
        self.client.login(username='admin', password='password123')
        
        # Data tanpa 'image'
        incomplete_data = {
            'name': 'Tripod Manfrotto',
            'quantity': 10,
            'price_per_hour': 20.50,
        }
        
        response = self.client.post(self.add_url, incomplete_data)
        
        # Memastikan kode status 400 Bad Request
        self.assertEqual(response.status_code, 400) 
        json_response = json.loads(response.content)
        self.assertIn('error', json_response)
        
        # Memastikan tidak ada penambahan objek di database
        self.assertEqual(Equipment.objects.count(), 1) 

    def test_detail_json_view(self):
        """Test 3.3: Berhasil mendapatkan detail alat dalam format JSON."""
        self.client.login(username='admin', password='password123')
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertEqual(json_response['name'], 'Kamera A6000')
        self.assertEqual(json_response['quantity'], 5)

    def test_edit_equipment_success(self):
        """Test 3.4: Admin berhasil mengedit data alat."""
        self.client.login(username='admin', password='password123')
        
        updated_data = {
            'name': 'Kamera A6000 (UPDATE)',
            'quantity': 1, # Kuantitas diubah dari 5 menjadi 1
            'price_per_hour': 20.00,
        }
        
        response = self.client.post(self.edit_url, updated_data)
        
        self.assertEqual(response.status_code, 200)
        
        # Memuat ulang objek dari database untuk memverifikasi perubahan
        updated_equipment = Equipment.objects.get(id=self.equipment.id)
        self.assertEqual(updated_equipment.name, 'Kamera A6000 (UPDATE)')
        self.assertEqual(updated_equipment.quantity, 1)

    def test_delete_equipment_success(self):
        """Test 3.5: Admin berhasil menghapus alat."""
        self.client.login(username='admin', password='password123')
        
        # Sebelum hapus, ada 1 objek equipment
        self.assertEqual(Equipment.objects.count(), 1)
        
        response = self.client.post(self.delete_url)
        
        self.assertEqual(response.status_code, 200)
        
        # Memastikan objek sudah terhapus dari database
        self.assertEqual(Equipment.objects.count(), 0)
        # Memastikan objek Rental yang terkait juga terhapus (CASCADE)
        self.assertEqual(Rental.objects.count(), 0)

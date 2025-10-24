from django.test import SimpleTestCase
from dashboard.templatetags import currency

class CurrencyFilterTests(SimpleTestCase):
    def test_currency_valid_integer(self):
        """Harus mengubah integer ke format rupiah dengan titik pemisah ribuan"""
        result = currency.currency(1200000)
        self.assertEqual(result, "Rp 1.200.000")

    def test_currency_valid_string_integer(self):
        """Harus bisa meng-handle string angka"""
        result = currency.currency("50000")
        self.assertEqual(result, "Rp 50.000")

    def test_currency_zero(self):
        """0 harus dikembalikan sebagai Rp 0"""
        result = currency.currency(0)
        self.assertEqual(result, "Rp 0")

    def test_currency_invalid_string(self):
        """Jika value bukan angka, harus mengembalikan value aslinya"""
        result = currency.currency("abc")
        self.assertEqual(result, "abc")

    def test_currency_none(self):
        """Jika value None, harus mengembalikan value aslinya (None)"""
        result = currency.currency(None)
        self.assertIsNone(result)

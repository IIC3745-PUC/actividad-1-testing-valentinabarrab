import unittest
from unittest.mock import Mock

from src.models import CartItem, Order
from src.pricing import PricingService, PricingError


class TestPricingService(unittest.TestCase):

    def setUp(self):
        self.pricing = PricingService()

    def test_subtotal_qty_negativa(self):
        items = [CartItem("A", 1000, 0)]
        with self.assertRaises(PricingError):
            self.pricing.subtotal_cents(items)

    def test_subtotal_precio_negativo(self):
        items = [CartItem("A", -100, 1)]
        with self.assertRaises(PricingError):
            self.pricing.subtotal_cents(items)

    def test_apply_coupon_none(self):
        self.assertEqual(self.pricing.apply_coupon(10000, None), 10000)

    def test_apply_coupon_save10(self):
        self.assertEqual(self.pricing.apply_coupon(10000, "SAVE10"), 9000)

    def test_apply_coupon_clp2000(self):
        self.assertEqual(self.pricing.apply_coupon(3000, "CLP2000"), 1000)

    def test_apply_coupon_otro(self):
        with self.assertRaises(PricingError):
            self.pricing.apply_coupon(10000, "error")

    def test_cents_cl(self):
        self.assertEqual(self.pricing.tax_cents(10000, "CL"), 1900)

    def test_cents_eu(self):
        self.assertEqual(self.pricing.tax_cents(10000, "EU"), 2100)

    def test_cents_us(self):
        self.assertEqual(self.pricing.tax_cents(10000, "US"), 0)

    def test_tax_pais_invalido(self):
        with self.assertRaises(PricingError):
            self.pricing.tax_cents(10000, "unsupported country")

    def test_shipping_cents_cl(self):
        self.assertEqual(self.pricing.shipping_cents(20000, "CL"), 0)

    def test_shipping_cents_us(self):
        self.assertEqual(self.pricing.shipping_cents(10000, "US"), 5000)

    def test_shipping_cents_eu(self):
        self.assertEqual(self.pricing.shipping_cents(10000, "EU"), 5000)

    def test_shipping_pais_invalido(self):
        with self.assertRaises(PricingError):
            self.pricing.shipping_cents(10000, "unsupported country")

    def test_total_cents(self):
        items = [CartItem("A", 1000, 2)]
        self.assertEqual(self.pricing.total_cents(items, None, "CL"), 4880)
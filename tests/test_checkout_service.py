import unittest
from unittest.mock import Mock, patch

from src.models import CartItem
from src.pricing import PricingError
from src.checkout import CheckoutService, ChargeResult


class TestCheckoutService(unittest.TestCase):

    def setUp(self):
        self.payments = Mock()
        self.email = Mock()
        self.fraud = Mock()
        self.repo = Mock()
        self.pricing = Mock()
        self.token = "token"
        self.country = "country"

        self.service = CheckoutService(self.payments, self.email, self.fraud, self.repo, self.pricing)

        self.items = [CartItem("A1", 1000, 1)]

    def test_invalid_user(self):
        self.assertEqual(self.service.checkout(" ", self.items, self.token, self.country), "INVALID_USER")

    def test_invalid_cart(self):
        self.pricing.total_cents.side_effect = PricingError("BAD_CART")
        self.assertEqual(self.service.checkout("user", self.items, self.token, self.country), "INVALID_CART:BAD_CART")

    def test_rejected_fraud(self):
        self.pricing.total_cents.return_value = 1000
        self.fraud.score.return_value = 90
        self.assertEqual(self.service.checkout("user", self.items, self.token, self.country), "REJECTED_FRAUD")

    def test_payment_failed(self):
        self.pricing.total_cents.return_value = 1000
        self.fraud.score.return_value = 10
        self.payments.charge.return_value = ChargeResult(False, None, "DECLINED")
        self.assertEqual(self.service.checkout("user", self.items, self.token, self.country), "PAYMENT_FAILED:DECLINED")

    @patch("src.checkout.uuid.uuid4", return_value="1234")
    def test_checkout_success(self, mock_uuid):
        self.pricing.total_cents.return_value = 1000
        self.fraud.score.return_value = 10
        self.payments.charge.return_value = ChargeResult(True, "ch", None)

        self.assertEqual(self.service.checkout("user", self.items, self.token, self.country), "OK:1234")

        self.repo.save.assert_called_once()
        self.email.send_receipt.assert_called_once()



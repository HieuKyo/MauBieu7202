"""
Tests for payroll_statistics app
"""
from django.test import TestCase
from .models import PayingUnit, BeneficiaryAccount
from .views import is_collection_transaction


class PayrollStatisticsTestCase(TestCase):
    """Test cases for Payroll Statistics"""

    def setUp(self):
        """Set up test data"""
        self.unit1 = PayingUnit.objects.create(
            account_number='7202201001',
            name='Đơn vị A'
        )
        self.unit2 = PayingUnit.objects.create(
            account_number='7202201002',
            name='Đơn vị B'
        )

    def test_paying_unit_creation(self):
        """Test creating PayingUnit"""
        self.assertEqual(PayingUnit.objects.count(), 2)
        self.assertEqual(str(self.unit1), '7202201001 - Đơn vị A')

    def test_beneficiary_account_creation(self):
        """Test creating BeneficiaryAccount"""
        ben = BeneficiaryAccount.objects.create(
            unit=self.unit1,
            account_number='7202215001',
            remark_ref='CHI LUONG THANG 11'
        )
        self.assertEqual(BeneficiaryAccount.objects.count(), 1)
        self.assertEqual(ben.unit, self.unit1)

    def test_is_collection_transaction_with_negative_rsltremark(self):
        """Test is_collection_transaction with negative rsltremark"""
        result = is_collection_transaction(
            facno='7202215001',
            tacno='7202201001',
            remark='Tien dien',
            rsltremark='-50000'
        )
        self.assertTrue(result)

    def test_is_collection_transaction_with_thu_ho_keyword(self):
        """Test is_collection_transaction with THU HO keyword"""
        result = is_collection_transaction(
            facno='7202215001',
            tacno='7202201001',
            remark='THU HO tien nuoc',
            rsltremark='50000'
        )
        self.assertTrue(result)

    def test_is_collection_transaction_with_khoan_tru_keyword(self):
        """Test is_collection_transaction with KHOAN TRU keyword"""
        result = is_collection_transaction(
            facno='7202215001',
            tacno='7202201001',
            remark='KHOAN TRU bhxh',
            rsltremark='100000'
        )
        self.assertTrue(result)

    def test_is_payroll_transaction(self):
        """Test normal payroll transaction (should return False)"""
        result = is_collection_transaction(
            facno='7202201001',
            tacno='7202215001',
            remark='CHI LUONG THANG 11',
            rsltremark='5000000'
        )
        self.assertFalse(result)

    def test_unique_together_constraint(self):
        """Test unique_together constraint on BeneficiaryAccount"""
        BeneficiaryAccount.objects.create(
            unit=self.unit1,
            account_number='7202215001',
            remark_ref='CHI LUONG'
        )
        # Tạo duplicate sẽ raise exception
        with self.assertRaises(Exception):
            BeneficiaryAccount.objects.create(
                unit=self.unit1,
                account_number='7202215001',
                remark_ref='CHI LUONG 2'
            )

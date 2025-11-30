"""
Tests for payroll_statistics app
"""
from django.test import TestCase
from .models import PayingUnit, BeneficiaryAccount, Transaction
from .views import determine_transaction_type, is_unit_account, is_employee_account


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

    def test_account_patterns(self):
        """Test account pattern detection"""
        # Unit accounts
        self.assertTrue(is_unit_account('7202201001'))
        self.assertTrue(is_unit_account('7202000123'))
        self.assertFalse(is_unit_account('7202215001'))

        # Employee accounts
        self.assertTrue(is_employee_account('7202215001'))
        self.assertTrue(is_employee_account('7202205001'))
        self.assertFalse(is_employee_account('7202201001'))

    def test_collection_with_negative_rsltremark(self):
        """Test Thu hộ với rsltremark âm (ưu tiên cao nhất)"""
        is_collection, unit_acc, emp_acc = determine_transaction_type(
            facno='7202215001',  # Nhân viên
            tacno='7202201001',  # Đơn vị
            remark='Tien dien',
            rsltremark='-50000'
        )
        self.assertTrue(is_collection)
        self.assertEqual(unit_acc, '7202201001')  # tacno là đơn vị
        self.assertEqual(emp_acc, '7202215001')   # facno là nhân viên

    def test_collection_with_thu_ho_keyword(self):
        """Test Thu hộ với từ khóa THU HO"""
        is_collection, unit_acc, emp_acc = determine_transaction_type(
            facno='7202215001',
            tacno='7202201001',
            remark='THU HO tien nuoc',
            rsltremark='50000'  # Dương nhưng có từ khóa
        )
        self.assertTrue(is_collection)
        self.assertEqual(unit_acc, '7202201001')
        self.assertEqual(emp_acc, '7202215001')

    def test_payroll_by_account_pattern(self):
        """Test Chi lương dựa vào pattern tài khoản"""
        is_collection, unit_acc, emp_acc = determine_transaction_type(
            facno='7202201001',  # Đơn vị (pattern)
            tacno='7202215001',  # Nhân viên (pattern)
            remark='CHI LUONG THANG 11',
            rsltremark='5000000'
        )
        self.assertFalse(is_collection)
        self.assertEqual(unit_acc, '7202201001')  # facno là đơn vị
        self.assertEqual(emp_acc, '7202215001')   # tacno là nhân viên

    def test_collection_by_account_pattern(self):
        """Test Thu hộ dựa vào pattern tài khoản"""
        is_collection, unit_acc, emp_acc = determine_transaction_type(
            facno='7202215001',  # Nhân viên (pattern)
            tacno='7202201001',  # Đơn vị (pattern)
            remark='Tien bao hiem',  # Không có từ khóa
            rsltremark='100000'  # Dương
        )
        self.assertTrue(is_collection)  # Vì tacno là pattern đơn vị, facno là nhân viên
        self.assertEqual(unit_acc, '7202201001')
        self.assertEqual(emp_acc, '7202215001')

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

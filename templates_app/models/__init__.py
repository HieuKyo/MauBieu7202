"""
Model của templates_app, chia theo nhóm nghiệp vụ.

Mọi model được import lại ở đây nên code cũ dùng "from .models import X" vẫn chạy.
Thêm model mới: tạo trong file nhóm tương ứng rồi import vào đây.
"""
# Mẫu biểu
from .template import Category, Variable, Template, TemplateVariable
# Khách hàng, doanh nghiệp
from .customer import Customer, Business
# Hệ thống: cấu hình, hồ sơ người dùng, tin tức
from .system import GlobalConfig, BranchConfig, AppProgram, UserProfile, Promotion
# Số đẹp
from .beautiful_number import DetailedFeeTier, OnRequestFeeTier, BeautifulNumber
# E-Learning
from .elearning import Course, CourseEnrollment
# Phân tích sao kê
from .bank_statement import BankStatement, AccountName, Transaction
# ATM
from .atm import ATM, ATMManagementBoard, Vehicle, Person, ATMReplenishment, VehicleDutySchedule, ATMDiscrepancy
# Báo cáo
from .report import MailEnvelopeTracking, ReportConfiguration, DongMoTaiKhoanHistory, ATMReportUpload, ATMTransactionReport
# Tín dụng
from .credit import FTPConfig, TDSnapshot
# Đăng ký HĐV / QR
from .registration import HDVRegistration, HDVImportRecord, QRRegistration
# Kế toán Ngân quỹ
from .cash import CanDoiUpload, BiaChungTu, BiaThuTuIn, CASH_DENOMINATIONS, CashDrawerBalance, CashDrawerStatement, CashPrintConfigBase, CashPrintConfig, CashPrintConfigNopTien, CashPrintConfigChungTuBase, CashPrintConfigBangKeThu, CashPrintConfigBangKeChi, CashPrintConfigDeNghi
# Chỉ tiêu SPDV
from .spdv_kpi import SPDVKpiRecord, SPDVKpiTarget, SPDVKpiDetail
# Hàm xử lý chữ tiếng Việt
from .text_utils import remove_vietnamese_diacritics, num_to_vietnamese_words


# Alias để backward compatibility
#BranchConfig = GlobalConfig

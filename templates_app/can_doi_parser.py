"""
Module đọc file Cân đối tài khoản (Excel) và tính các chỉ tiêu doanh thu phí dịch vụ
theo hướng dẫn Mẫu DV/KHCL (Đăng ký kế hoạch thu dịch vụ).

Số liệu mỗi tài khoản lấy theo "net cuối kỳ" = afterbal_cr - afterbal_dr,
tương đương số dư Có cuối kỳ đối với các tài khoản Thu nhập (nhóm 7),
đồng thời tính đúng cho các tài khoản có số dư Nợ (VD: TK82 - Chi phí KD ngoại hối).
"""
import pandas as pd

REQUIRED_COLUMNS = ['acctcd', 'afterbal_dr', 'afterbal_cr']

# Các nhóm chỉ tiêu theo Mẫu DV/KHCL: (STT, Tên chỉ tiêu, Diễn giải tài khoản dùng để tính)
CATEGORIES = [
    ('1.1', 'Thanh toán trong nước', '711001, 711035, 711041, 711042, 711043, 711044, 711098, 711099'),
    ('1.2', 'Thanh toán quốc tế (bao gồm dịch vụ TT UPAS L/C)', '711002 ~ 711014, 711096, 711097, 711045'),
    ('1.3', 'Dịch vụ kiều hối', '711034'),
    ('1.4', 'Dịch vụ thẻ', '711015 ~ 711033, 711051, 711052, 711059'),
    ('1.5', 'E-Banking', '711036, 711037, 711038, 711039'),
    ('1.6', 'Ủy thác và đại lý', '714, 716'),
    ('1.7', 'Bảo lãnh', '704'),
    ('1.8', 'Ngân quỹ', '713, 718'),
    ('1.9', 'Thu khác', '715, 717, 719'),
    ('1.10', 'Thu ròng từ KD ngoại hối', '72 → 82 ± Kết chuyển chênh lệch tỷ giá KDNT (63)'),
]

MUC_III_DIEN_GIAI = 'Cộng (+) 749005 – Trừ (-) 849005'
MUC_IV_DIEN_GIAI = '= (1.1 → 1.10) + (III)'


def _normalize_code(raw):
    """
    Chuẩn hoá mã tài khoản: bỏ khoảng trắng và đuôi '.0' phát sinh khi
    Excel lưu cột acctcd dạng số (pandas đọc '714' thành '714.0').
    """
    code = str(raw).strip()
    if code.endswith('.0') and code[:-2].isdigit():
        code = code[:-2]
    return code


def _to_number(value):
    """Chuyển giá trị số trong file (kể cả dạng khoa học 1.75185E+12) sang float."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(',', '')
    if not text:
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


class CanDoiParser:
    """Đọc file Cân đối tài khoản (.xls/.xlsx) và tính số liệu cốt yếu"""

    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.balances = {}  # acctcd (str, đã strip) -> net cuối kỳ (float)

    def validate_file(self):
        """
        Đọc và kiểm tra file có đúng định dạng Cân đối tài khoản không.

        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            file_lower = self.file_path.lower()
            if file_lower.endswith('.xls') and not file_lower.endswith('.xlsx'):
                self.df = pd.read_excel(self.file_path, engine='xlrd', dtype=str)
            elif file_lower.endswith('.xlsx'):
                self.df = pd.read_excel(self.file_path, engine='openpyxl', dtype=str)
            else:
                return False, "File phải có định dạng .xls hoặc .xlsx"

            self.df.columns = self.df.columns.str.strip()
            col_lower_map = {c.lower(): c for c in self.df.columns}
            rename_map = {}
            missing_cols = []
            for req in REQUIRED_COLUMNS:
                if req in self.df.columns:
                    pass
                elif req.lower() in col_lower_map:
                    rename_map[col_lower_map[req.lower()]] = req
                else:
                    missing_cols.append(req)
            if rename_map:
                self.df.rename(columns=rename_map, inplace=True)
            if missing_cols:
                return False, f"File thiếu các cột bắt buộc: {', '.join(missing_cols)}"

            if len(self.df) == 0:
                return False, "File không có dữ liệu"

            return True, ""
        except Exception as e:
            return False, f"Không đọc được file: {str(e)}"

    def process(self):
        """
        Tính net cuối kỳ (afterbal_cr - afterbal_dr) cho từng tài khoản
        và trả về dict các chỉ tiêu doanh thu phí dịch vụ.
        """
        for _, row in self.df.iterrows():
            code = _normalize_code(row.get('acctcd', ''))
            if not code:
                continue
            net = _to_number(row.get('afterbal_cr')) - _to_number(row.get('afterbal_dr'))
            self.balances[code] = net

        results = {
            '1.1': self._sum_leaf_codes({'711001', '711035', '711041', '711042', '711043', '711044', '711098', '711099'}),
            '1.2': self._sum_leaf_range(711002, 711014) + self._sum_leaf_codes({'711096', '711097', '711045'}),
            '1.3': self._sum_leaf_codes({'711034'}),
            '1.4': self._sum_leaf_range(711015, 711033) + self._sum_leaf_codes({'711051', '711052', '711059'}),
            '1.5': self._sum_leaf_codes({'711036', '711037', '711038', '711039'}),
            '1.6': self._sum_parent_codes({'714', '716'}),
            '1.7': self._sum_parent_codes({'704'}),
            '1.8': self._sum_parent_codes({'713', '718'}),
            '1.9': self._sum_parent_codes({'715', '717', '719'}),
            '1.10': self._forex_net(),
        }
        # 849005 là tài khoản chi (dư Nợ) nên net đã âm sẵn -> cộng trực tiếp là trừ đi
        muc_III = self._get('749005') + self._get('849005')
        tong_doanh_thu = sum(results.values()) + muc_III

        return {
            'chi_tieu': results,
            'muc_III': muc_III,
            'tong_doanh_thu': tong_doanh_thu,
        }

    def _get(self, code):
        return self.balances.get(code, 0.0)

    def _sum_leaf_codes(self, codes):
        return sum(self._get(c) for c in codes)

    def _sum_leaf_range(self, low, high):
        total = 0.0
        for code, net in self.balances.items():
            if code.isdigit() and low <= int(code) <= high:
                total += net
        return total

    def _sum_parent_codes(self, codes):
        return sum(self._get(c) for c in codes)

    def _forex_net(self):
        """Thu ròng KD ngoại hối = tổng TK72..TK82 (net) ± TK63 (Chênh lệch tỷ giá)"""
        total = sum(self._get(str(i)) for i in range(72, 83))
        total += self._get('63')
        return total

"""
Data Processor Module for KPI Dashboard
========================================
Module xử lý dữ liệu từ các file Card, SMS, E-Mobile cho KPI Dashboard
Tích hợp vào Django - Agribank
"""

import pandas as pd
import calendar


# Mapping từ Mã GDV (dùng chung) → CUSER trong file Thẻ
# File thẻ dùng định dạng khác: mã chi nhánh + tên viết tắt
CARD_CUSER_MAP = {
    'GRANTHAO': '7202CTHAOTN',
    'GRALTHUC': '7202cthuclt',
    'GRATHIEU': '7202chieutt',
    'GRANSINH': '7202CSINHNT',
    'GRATTHAO': '7202CTHAOTLT',
    'GRASHANH': '7202canhsh',
    'GRACACHI': '7202CCHICA',
    'GRATNNHI': '7202cnhitn',
}


class DataProcessor:
    """
    Class xử lý dữ liệu từ các file nguồn
    """

    def __init__(self, user_id, month, year):
        """
        Khởi tạo DataProcessor

        Args:
            user_id: Mã GDV cần lọc
            month: Tháng báo cáo
            year: Năm báo cáo
        """
        self.user_id = user_id
        self.month = month
        self.year = year
        self.days_in_month = calendar.monthrange(year, month)[1]

    def _read_file(self, file_obj, header=0):
        """
        Đọc file Excel hoặc CSV

        Args:
            file_obj: File object từ Django request.FILES
            header  : Chỉ số dòng header (0-indexed). Mặc định = 0.

        Returns:
            DataFrame
        """
        # Reset file pointer
        file_obj.seek(0)

        # Đọc file dựa vào extension
        filename = file_obj.name.lower()
        if filename.endswith('.csv'):
            df = pd.read_csv(file_obj, header=header)
        else:
            df = pd.read_excel(file_obj, header=header)

        return df

    def _filter_by_date_range(self, df, date_column):
        """
        Lọc DataFrame theo khoảng thời gian tháng/năm

        Args:
            df: DataFrame cần lọc
            date_column: Tên cột chứa ngày

        Returns:
            DataFrame đã được lọc
        """
        # Chuyển đổi cột ngày sang datetime
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')

        # Lọc theo tháng và năm
        mask = (
            (df[date_column].dt.month == self.month) &
            (df[date_column].dt.year == self.year)
        )
        return df[mask].copy()

    def process_card_file(self, file_obj):
        """
        Xử lý file dữ liệu Thẻ.

        Cấu trúc file:
        - CUSER : Mã GDV phát hành (dùng để lọc)
        - CDATE : Ngày phát hành (dd/mm/yyyy HH:MM:SS)
        - ISSUE_TYPE: Loại phát hành
            CSP_New     → Phát hành mới
            CSP_Reissue → Phát hành lại

        Tất cả các dòng (New + Reissue) đều được tính vào chỉ tiêu Phát hành Thẻ.

        Returns:
            dict {ngày: số_lượng}
        """
        df = self._read_file(file_obj)

        required_cols = ['CUSER', 'CDATE']
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            raise ValueError(f"File Thẻ thiếu các cột: {', '.join(missing_cols)}")

        # Chuyển Mã GDV sang CUSER tương ứng trong file thẻ
        card_cuser = CARD_CUSER_MAP.get(self.user_id)
        if not card_cuser:
            raise ValueError(
                f"Không tìm thấy CUSER cho GDV '{self.user_id}' trong file thẻ. "
                f"Các GDV hỗ trợ: {', '.join(CARD_CUSER_MAP.keys())}"
            )

        # Lọc theo CUSER (case-sensitive theo đúng mapping)
        df = df[df['CUSER'] == card_cuser].copy()

        # Chuyển đổi ngày — định dạng "dd/mm/yyyy HH:MM:SS"
        df['CDATE'] = pd.to_datetime(df['CDATE'], dayfirst=True, errors='coerce')

        # Lọc theo tháng/năm
        df = self._filter_by_date_range(df, 'CDATE')

        if df.empty:
            return {}

        df['day'] = df['CDATE'].dt.day
        counts = df.groupby('day').size()
        return {int(day): int(cnt) for day, cnt in counts.items()}

    def _process_sms_emobile(self, file_obj, file_label):
        """
        Xử lý chung cho file SMS và E-Mobile (cùng cấu trúc).

        Cấu trúc file:
        - entydt  : Ngày đăng ký (dd/mm/yyyy)
        - crtusr  : Mã GDV phát sinh giao dịch (dùng để lọc)
        - uptdtm  : Ngày cập nhật — nếu có giá trị → bản cập nhật,
                    KHÔNG tính vào chỉ tiêu (chỉ tính đăng ký mới)

        Lưu ý: chỉ những dòng có uptdtm rỗng/null mới được đếm.

        Returns:
            dict {ngày: số_lượng}
        """
        df = self._read_file(file_obj)

        required_cols = ['entydt', 'crtusr']
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            raise ValueError(f"File {file_label} thiếu các cột: {', '.join(missing_cols)}")

        # Lọc theo GDV
        df = df[df['crtusr'] == self.user_id].copy()

        # Loại bỏ các dòng cập nhật: uptdtm có giá trị = không phải đăng ký mới
        if 'uptdtm' in df.columns:
            df = df[df['uptdtm'].isna() | (df['uptdtm'].astype(str).str.strip() == '')].copy()

        # Chuyển đổi ngày (định dạng dd/mm/yyyy)
        df['entydt'] = pd.to_datetime(df['entydt'], dayfirst=True, errors='coerce')

        # Lọc theo tháng/năm
        df = self._filter_by_date_range(df, 'entydt')

        if df.empty:
            return {}

        df['day'] = df['entydt'].dt.day
        counts = df.groupby('day').size()
        return {int(day): int(cnt) for day, cnt in counts.items()}

    def process_sms_file(self, file_obj):
        """
        Xử lý file SMS Banking.

        Cấu trúc file: entydt, crtusr, uptdtm (xem _process_sms_emobile)

        Returns:
            dict {ngày: số_lượng}
        """
        return self._process_sms_emobile(file_obj, "SMS")

    def process_emobile_file(self, file_obj):
        """
        Xử lý file E-Mobile Banking.

        Cấu trúc file: entydt, crtusr, uptdtm (xem _process_sms_emobile)

        Returns:
            dict {ngày: số_lượng}
        """
        return self._process_sms_emobile(file_obj, "E-Mobile")

    def process_billpayment_file(self, file_obj):
        """
        Xử lý file Bảng kê chứng từ giao dịch chi tiết (Hạch toán Billpayment TM, CK).

        Cấu trúc file:
        - 8 dòng đầu là tiêu đề/metadata của báo cáo
        - Dòng 9 (index 8): header cột — STT, Mã GD, Tình trạng GD, Ngày GD, ...
        - Dòng 10 trở đi: dữ liệu thực
        - Cột 'Ngày GD': định dạng yyyymmddHHMMSS (vd: 20260327154258)
        - Không lọc theo user — file đã được GDV lọc sẵn trước khi upload

        Returns:
            dict {ngày: số_lượng}
        """
        # Dòng B10 trong Excel = STT header ở row 10 (1-based) = index 9 (0-based)
        df = self._read_file(file_obj, header=9)

        # Tìm cột "Ngày GD" (strip tên phòng khi đọc)
        df.columns = [str(c).strip() for c in df.columns]

        date_col = 'Ngày GD'
        if date_col not in df.columns:
            raise ValueError(
                f"File Billpayment thiếu cột '{date_col}'. "
                f"Các cột tìm thấy: {', '.join(df.columns.tolist())}"
            )

        # Bỏ dòng trống (STT rỗng)
        df = df.dropna(subset=[date_col]).copy()

        # Parse ngày từ định dạng yyyymmddHHMMSS hoặc yyyymmdd
        def parse_ngayGD(val):
            s = str(val).strip().split('.')[0]   # bỏ phần thập phân nếu có
            s = s.replace(' ', '')
            if len(s) >= 8:
                return pd.to_datetime(s[:8], format='%Y%m%d', errors='coerce')
            return pd.NaT

        df['_date'] = df[date_col].apply(parse_ngayGD)

        # Lọc theo tháng/năm
        df = self._filter_by_date_range(df, '_date')

        if df.empty:
            return {}

        df['day'] = df['_date'].dt.day
        counts = df.groupby('day').size()
        return {int(day): int(cnt) for day, cnt in counts.items()}

    def get_count_for_day(self, data_df, day):
        """
        Lấy số lượng cho một ngày cụ thể từ DataFrame

        Args:
            data_df: DataFrame chứa dữ liệu (cần có cột 'day' và 'count')
            day: Ngày cần lấy (1-31)

        Returns:
            int: Số lượng (0 nếu không có dữ liệu)
        """
        if data_df is None or data_df.empty:
            return 0

        day_data = data_df[data_df['day'] == day]
        if day_data.empty:
            return 0

        return int(day_data['count'].iloc[0])

    def process_cif_file(self, file_obj):
        """
        Xử lý file CIF (dữ liệu mở tài khoản).

        Cấu trúc file:
        - opndt    : Ngày mở tài khoản (dd/mm/yyyy)
        - tellernm : Mã GDV (dùng để lọc)
        - locdpnm  : Loại tài khoản (phân biệt cá nhân / tổ chức)

        Loại cá nhân:
            "Tiền gửi thanh toán cá nhân"
            "TG KKH CB lương Ngân sách"
            "TG KKH Cá nhân (Số đẹp)"
            "TG thanh toán cá nhân eKYC"

        Loại tổ chức:
            "TG KKH TCKT"
            "Tg KKH TCKT (Số đẹp)"

        Returns:
            tuple(dict, dict): (cif_personal_by_day, cif_corporate_by_day)
            mỗi dict có dạng {ngày: số_lượng}
        """
        INDIVIDUAL_TYPES = {
            "tiền gửi thanh toán cá nhân",
            "tg kkh cb lương ngân sách",
            "tg kkh cá nhân (số đẹp)",
            "tg thanh toán cá nhân ekyc",
        }

        df = self._read_file(file_obj)

        required_cols = ['opndt', 'tellernm', 'locdpnm']
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            raise ValueError(f"File CIF thiếu các cột: {', '.join(missing_cols)}")

        # Lọc theo GDV
        df = df[df['tellernm'] == self.user_id].copy()

        # Chuyển đổi ngày (định dạng dd/mm/yyyy)
        df['opndt'] = pd.to_datetime(df['opndt'], dayfirst=True, errors='coerce')

        # Lọc theo tháng/năm
        df = self._filter_by_date_range(df, 'opndt')

        personal_by_day  = {}
        corporate_by_day = {}

        if df.empty:
            return personal_by_day, corporate_by_day

        df['day'] = df['opndt'].dt.day
        df['locdpnm_lower'] = df['locdpnm'].str.strip().str.lower()

        for day in range(1, self.days_in_month + 1):
            day_df = df[df['day'] == day]
            if day_df.empty:
                continue

            personal_count  = day_df['locdpnm_lower'].isin(INDIVIDUAL_TYPES).sum()
            corporate_count = len(day_df) - personal_count

            if personal_count > 0:
                personal_by_day[day] = int(personal_count)
            if corporate_count > 0:
                corporate_by_day[day] = int(corporate_count)

        return personal_by_day, corporate_by_day

    def get_new_issue_count_for_day(self, card_data, day):
        """
        Lấy số lượng thẻ mới (New Issue) cho một ngày cụ thể

        Args:
            card_data: DataFrame dữ liệu thẻ
            day: Ngày cần lấy

        Returns:
            int: Số lượng thẻ mới
        """
        if card_data is None or card_data.empty:
            return 0

        day_data = card_data[card_data['day'] == day]
        if day_data.empty:
            return 0

        return int(day_data['new_issue_count'].iloc[0])

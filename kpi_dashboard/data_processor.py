"""
Data Processor Module
=====================
Module xử lý dữ liệu từ các file Card, SMS, E-Mobile
"""

import pandas as pd
from io import BytesIO
from datetime import datetime
import calendar


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

    def _read_file(self, file_obj):
        """
        Đọc file Excel hoặc CSV

        Args:
            file_obj: File object từ Streamlit uploader

        Returns:
            DataFrame
        """
        # Reset file pointer
        file_obj.seek(0)

        # Đọc file dựa vào extension
        if file_obj.name.endswith('.csv'):
            df = pd.read_csv(file_obj)
        else:
            df = pd.read_excel(file_obj)

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
        Xử lý file dữ liệu Thẻ

        File structure:
        - dlvrydt: Ngày phát hành (dd/mm/yyyy)
        - dlvryusrid: User ID
        - isutycd: Loại phát hành ("New Issue" hoặc khác)

        Args:
            file_obj: File object

        Returns:
            DataFrame với columns: [day, count, new_issue_count]
        """
        df = self._read_file(file_obj)

        # Kiểm tra columns cần thiết
        required_cols = ['dlvrydt', 'dlvryusrid']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"File Thẻ thiếu các cột: {', '.join(missing_cols)}")

        # Lọc theo User ID
        df = df[df['dlvryusrid'] == self.user_id].copy()

        # Chuyển đổi ngày (định dạng dd/mm/yyyy)
        df['dlvrydt'] = pd.to_datetime(df['dlvrydt'], format='%d/%m/%Y', errors='coerce')

        # Lọc theo tháng/năm
        df = self._filter_by_date_range(df, 'dlvrydt')

        if df.empty:
            # Trả về DataFrame rỗng với cấu trúc đúng
            return pd.DataFrame(columns=['day', 'count', 'new_issue_count'])

        # Tạo cột day (ngày trong tháng)
        df['day'] = df['dlvrydt'].dt.day

        # Tính toán số lượng
        result = []

        for day in range(1, self.days_in_month + 1):
            day_data = df[df['day'] == day]
            total_count = len(day_data)

            # Đếm số "New Issue" nếu có cột isutycd
            new_issue_count = 0
            if 'isutycd' in df.columns:
                new_issue_count = len(day_data[day_data['isutycd'] == 'New Issue'])

            if total_count > 0 or new_issue_count > 0:
                result.append({
                    'day': day,
                    'count': total_count,
                    'new_issue_count': new_issue_count
                })

        return pd.DataFrame(result)

    def process_sms_file(self, file_obj):
        """
        Xử lý file dữ liệu SMS

        File structure:
        - entydt: Ngày đăng ký (yyyy-mm-dd)
        - crtusr: User ID

        Args:
            file_obj: File object

        Returns:
            DataFrame với columns: [day, count]
        """
        df = self._read_file(file_obj)

        # Kiểm tra columns cần thiết
        required_cols = ['entydt', 'crtusr']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"File SMS thiếu các cột: {', '.join(missing_cols)}")

        # Lọc theo User ID
        df = df[df['crtusr'] == self.user_id].copy()

        # Chuyển đổi ngày (định dạng yyyy-mm-dd)
        df['entydt'] = pd.to_datetime(df['entydt'], format='%Y-%m-%d', errors='coerce')

        # Lọc theo tháng/năm
        df = self._filter_by_date_range(df, 'entydt')

        if df.empty:
            return pd.DataFrame(columns=['day', 'count'])

        # Tạo cột day
        df['day'] = df['entydt'].dt.day

        # Đếm số lượng theo ngày
        result = df.groupby('day').size().reset_index(name='count')

        return result

    def process_emobile_file(self, file_obj):
        """
        Xử lý file dữ liệu E-Mobile Banking

        File structure:
        - entydt: Ngày đăng ký
        - crtusr: User ID

        Args:
            file_obj: File object

        Returns:
            DataFrame với columns: [day, count]
        """
        df = self._read_file(file_obj)

        # Kiểm tra columns cần thiết
        required_cols = ['entydt', 'crtusr']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"File E-Mobile thiếu các cột: {', '.join(missing_cols)}")

        # Lọc theo User ID
        df = df[df['crtusr'] == self.user_id].copy()

        # Chuyển đổi ngày
        df['entydt'] = pd.to_datetime(df['entydt'], errors='coerce')

        # Lọc theo tháng/năm
        df = self._filter_by_date_range(df, 'entydt')

        if df.empty:
            return pd.DataFrame(columns=['day', 'count'])

        # Tạo cột day
        df['day'] = df['entydt'].dt.day

        # Đếm số lượng theo ngày
        result = df.groupby('day').size().reset_index(name='count')

        return result

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

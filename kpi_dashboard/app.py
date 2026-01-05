"""
Công cụ Tính KPI Tự động - Agribank
====================================
Ứng dụng web Streamlit để tự động hóa tính điểm KPI hàng ngày cho Giao dịch viên (GDV)
"""

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import calendar

from data_processor import DataProcessor
from kpi_calculator import KPICalculator


# Cấu hình trang
st.set_page_config(
    page_title="Công cụ Tính KPI - Agribank",
    page_icon="📊",
    layout="wide"
)


def main():
    """Hàm chính của ứng dụng"""

    # Tiêu đề
    st.title("📊 Công cụ Tính KPI Tự động - Agribank")
    st.markdown("---")

    # Sidebar - Cấu hình
    with st.sidebar:
        st.header("⚙️ Cấu hình")

        # Chọn tháng/năm
        st.subheader("📅 Chọn Tháng/Năm")
        col1, col2 = st.columns(2)
        with col1:
            selected_month = st.selectbox(
                "Tháng",
                range(1, 13),
                index=datetime.now().month - 1,
                format_func=lambda x: f"Tháng {x}"
            )
        with col2:
            selected_year = st.selectbox(
                "Năm",
                range(2020, 2031),
                index=datetime.now().year - 2020
            )

        # Tính số ngày trong tháng
        days_in_month = calendar.monthrange(selected_year, selected_month)[1]
        st.info(f"Tháng {selected_month}/{selected_year} có {days_in_month} ngày")

        # Chọn Mã GDV
        st.subheader("👤 Chọn Mã GDV")
        user_id = st.selectbox(
            "User ID",
            [
                'GRATHIEU',
                'GRATNNHI',
                'GRACACHI',
                'GRANSINH',
                'GRALTHUC',
                'GRATTHAO',
                'GRANTHAO',
                'GRASHANH'
            ]
        )

        st.markdown("---")

        # Hệ số KPI (có thể cấu hình)
        with st.expander("🔧 Hệ số KPI", expanded=False):
            st.write("Cấu hình hệ số quy đổi:")
            coef_card = st.number_input("Phát hành thẻ", value=3.0, step=0.1)
            coef_signature = st.number_input("Quét chữ ký", value=3.0, step=0.1)
            coef_sms = st.number_input("Đăng ký SMS", value=4.0, step=0.1)
            coef_archive = st.number_input("Lưu trữ hồ sơ", value=0.5, step=0.1)
            coef_cif = st.number_input("CIF mới", value=3.0, step=0.1)

    # Main content area
    st.header("📂 Upload File Dữ liệu")

    # Upload files
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1️⃣ File KPI Mẫu")
        template_file = st.file_uploader(
            "Upload file Excel KPI mẫu (giữ nguyên định dạng)",
            type=['xlsx', 'xls'],
            key="template"
        )

        st.subheader("2️⃣ File Dữ liệu Thẻ")
        card_file = st.file_uploader(
            "Upload file dữ liệu thẻ (Excel/CSV)",
            type=['xlsx', 'xls', 'csv'],
            key="card"
        )

    with col2:
        st.subheader("3️⃣ File Dữ liệu SMS")
        sms_file = st.file_uploader(
            "Upload file dữ liệu SMS (Excel/CSV)",
            type=['xlsx', 'xls', 'csv'],
            key="sms"
        )

        st.subheader("4️⃣ File Dữ liệu E-Mobile Banking")
        emobile_file = st.file_uploader(
            "Upload file dữ liệu E-Mobile (Excel/CSV)",
            type=['xlsx', 'xls', 'csv'],
            key="emobile"
        )

    st.markdown("---")

    # Nút phân tích
    if st.button("🚀 Phân tích & Xuất Báo cáo", type="primary", width="stretch"):
        # Kiểm tra file template bắt buộc
        if template_file is None:
            st.error("⚠️ Vui lòng upload file KPI mẫu!")
            return

        # Kiểm tra ít nhất một file dữ liệu
        if card_file is None and sms_file is None and emobile_file is None:
            st.warning("⚠️ Vui lòng upload ít nhất một file dữ liệu (Thẻ, SMS hoặc E-Mobile)!")
            return

        try:
            with st.spinner("🔄 Đang xử lý dữ liệu..."):
                # Khởi tạo processors
                coefficients = {
                    'card': coef_card,
                    'signature': coef_signature,
                    'sms': coef_sms,
                    'archive': coef_archive,
                    'cif': coef_cif
                }

                data_processor = DataProcessor(user_id, selected_month, selected_year)
                kpi_calculator = KPICalculator(coefficients)

                # Đọc và xử lý dữ liệu
                st.info("📖 Đang đọc file dữ liệu...")

                # Xử lý file thẻ
                card_data = None
                if card_file is not None:
                    card_data = data_processor.process_card_file(card_file)
                    st.success(f"✅ Xử lý file Thẻ: {len(card_data)} bản ghi")

                # Xử lý file SMS
                sms_data = None
                if sms_file is not None:
                    sms_data = data_processor.process_sms_file(sms_file)
                    st.success(f"✅ Xử lý file SMS: {len(sms_data)} bản ghi")

                # Xử lý file E-Mobile
                emobile_data = None
                if emobile_file is not None:
                    emobile_data = data_processor.process_emobile_file(emobile_file)
                    st.success(f"✅ Xử lý file E-Mobile: {len(emobile_data)} bản ghi")

                # Tính toán KPI và cập nhật Excel
                st.info("📊 Đang tính toán KPI và cập nhật file Excel...")
                output_buffer = kpi_calculator.calculate_and_update_template(
                    template_file=template_file,
                    card_data=card_data,
                    sms_data=sms_data,
                    emobile_data=emobile_data,
                    days_in_month=days_in_month
                )

                st.success("✅ Hoàn thành tính toán KPI!")

                # Hiển thị thống kê
                st.subheader("📈 Thống kê tổng hợp")

                # Tạo summary DataFrame
                summary_data = []

                if card_data is not None:
                    total_cards = card_data['count'].sum()
                    new_issues = card_data['new_issue_count'].sum()
                    summary_data.append({
                        'Loại': 'Phát hành thẻ',
                        'Tổng số': total_cards,
                        'Chi tiết': f"{new_issues} thẻ mới, {total_cards - new_issues} thẻ phát hành lại"
                    })

                if sms_data is not None:
                    total_sms = sms_data['count'].sum()
                    summary_data.append({
                        'Loại': 'Đăng ký SMS',
                        'Tổng số': total_sms,
                        'Chi tiết': f"{total_sms} đăng ký"
                    })

                if emobile_data is not None:
                    total_emobile = emobile_data['count'].sum()
                    summary_data.append({
                        'Loại': 'E-Mobile Banking',
                        'Tổng số': total_emobile,
                        'Chi tiết': f"{total_emobile} đăng ký"
                    })

                if summary_data:
                    summary_df = pd.DataFrame(summary_data)
                    st.dataframe(summary_df, width="stretch", hide_index=True)

                # Nút download
                st.markdown("---")
                filename = f"KPI_{user_id}_{selected_month:02d}_{selected_year}.xlsx"
                st.download_button(
                    label="⬇️ Tải xuống báo cáo KPI",
                    data=output_buffer.getvalue(),
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    width="stretch"
                )

        except Exception as e:
            st.error(f"❌ Lỗi xảy ra: {str(e)}")
            st.exception(e)

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
        <p>Công cụ Tính KPI Tự động - Agribank | Phiên bản 1.0</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

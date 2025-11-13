"""
Script test để verify dữ liệu Customer
Chạy: python test_customer_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wordgen.settings')
django.setup()

from templates_app.models import Customer
from datetime import date

# Test với customer ID 3 (hoặc thay bằng ID khác)
customer_id = 3

try:
    customer = Customer.objects.get(id=customer_id)
    data = customer.get_data_dict()

    print("="*60)
    print(f"CUSTOMER DATA TEST - ID: {customer_id}")
    print("="*60)

    print(f"\n📋 Thông tin cơ bản:")
    print(f"  - Họ tên: {customer.ho_ten}")
    print(f"  - CMND/CCCD: {customer.so_cmnd} ({len(customer.so_cmnd)} chữ số)")
    print(f"  - Ngày cấp: {customer.ngay_cap_cmnd}")
    print(f"  - Nghề nghiệp: {customer.nghe_nghiep}")
    print(f"  - Loại tài khoản: {customer.loai_tai_khoan}")
    print(f"  - Số TK yêu cầu: {customer.so_tai_khoan_yc}")

    print(f"\n✅ Checkbox CMND/CCCD/Căn cước:")
    print(f"  - cmnd: {data['cmnd']}")
    print(f"  - cccd: {data['cccd']}")
    print(f"  - cancuoc: {data['cancuoc']}")

    print(f"\n✅ Checkbox nghề nghiệp:")
    print(f"  - nghe_nghiep_cong_chuc: {data['nghe_nghiep_cong_chuc']}")
    print(f"  - nghe_nghiep_nong_dan: {data['nghe_nghiep_nong_dan']}")
    print(f"  - nghe_nghiep_giao_vien_bac_si: {data['nghe_nghiep_giao_vien_bac_si']}")
    print(f"  - nghe_nghiep_cong_nhan: {data['nghe_nghiep_cong_nhan']}")
    print(f"  - nghe_nghiep_kinh_doanh: {data['nghe_nghiep_kinh_doanh']}")
    print(f"  - nghe_nghiep_hoc_sinh_sinh_vien: {data['nghe_nghiep_hoc_sinh_sinh_vien']}")
    print(f"  - nghe_nghiep_noi_tro: {data['nghe_nghiep_noi_tro']}")
    print(f"  - nghe_nghiep_cong_an_bo_doi: {data['nghe_nghiep_cong_an_bo_doi']}")
    print(f"  - nghe_nghiep_ky_su: {data['nghe_nghiep_ky_su']}")
    print(f"  - nghe_nghiep_khac: {data['nghe_nghiep_khac']}")

    print(f"\n✅ Biến so_tai_khoan_yc:")
    print(f"  - so_tai_khoan_yc: '{data['so_tai_khoan_yc']}'")
    print(f"  - stk_theo_yeu_cau: '{data['stk_theo_yeu_cau']}'")
    print(f"  - tk_theo_yeu_cau: '{data['tk_theo_yeu_cau']}'")

    print(f"\n✅ Checkbox dịch vụ:")
    print(f"  - dv_e_mobile: {data['dv_e_mobile']}")
    print(f"  - dv_vidientu: {data['dv_vidientu']}")
    print(f"  - dv_bankplus: {data['dv_bankplus']}")
    print(f"  - dv_abic: {data['dv_abic']}")

    print(f"\n✅ Biến ngày trả thẻ:")
    print(f"  - ngay_tra_the: '{data['ngay_tra_the']}'")

    print(f"\n✅ Biến tên thẻ:")
    print(f"  - ten_the_1: '{data['ten_the_1']}'")
    print(f"  - ten_tieng_anh: '{data['ten_tieng_anh']}'")

    print("\n" + "="*60)
    print("✅ TEST HOÀN TẤT")
    print("="*60)

except Customer.DoesNotExist:
    print(f"❌ Không tìm thấy Customer với ID: {customer_id}")
    print("Hãy thay đổi customer_id trong file test_customer_data.py")
except Exception as e:
    print(f"❌ LỖI: {e}")
    import traceback
    traceback.print_exc()

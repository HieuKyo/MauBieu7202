# tax_payment/utils.py

def doc_so_thanh_chu(number):
    """
    Hàm đọc số tiền thành chữ tiếng Việt (Đơn giản, hiệu quả, không cần thư viện ngoài)
    """
    if not number:
        return ""
    
    try:
        number = int(number)
    except:
        return ""

    if number == 0:
        return "Không đồng"

    def doc_3_so(n):
        chu_so = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
        tram = n // 100
        chuc = (n // 10) % 10
        don_vi = n % 10
        ket_qua = ""

        if tram == 0 and chuc == 0 and don_vi == 0: return ""
        
        # Đọc hàng trăm
        ket_qua += chu_so[tram] + " trăm "
        
        # Đọc hàng chục
        if chuc == 0 and don_vi != 0:
            ket_qua += "linh "
        elif chuc == 1:
            ket_qua += "mười "
        elif chuc > 1:
            ket_qua += chu_so[chuc] + " mươi "
            
        # Đọc hàng đơn vị
        if chuc > 0 and don_vi == 1:
            ket_qua += "mốt "
        elif chuc > 0 and don_vi == 5:
            ket_qua += "lăm "
        elif don_vi != 0:
            ket_qua += chu_so[don_vi] + " "
            
        return ket_qua

    trieu = 1000000
    ty = 1000000000
    
    # Xử lý các lớp (Tỷ, Triệu, Nghìn, Đồng)
    so_ty = number // ty
    number %= ty
    
    so_trieu = number // trieu
    number %= trieu
    
    so_nghin = number // 1000
    so_dong = number % 1000
    
    result = ""
    
    if so_ty > 0:
        result += doc_3_so(so_ty) + "tỷ "
    if so_trieu > 0:
        result += doc_3_so(so_trieu) + "triệu "
    if so_nghin > 0:
        result += doc_3_so(so_nghin) + "nghìn "
    if so_dong > 0:
        result += doc_3_so(so_dong)
        
    # Xử lý format văn bản
    result = result.strip()
    
    # Viết hoa chữ cái đầu
    result = result[0].upper() + result[1:]
    
    return result + " đồng."
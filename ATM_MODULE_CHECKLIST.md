# ATM Module - Checklist Triển Khai Offline

## ✅ 1. Models (templates_app/models.py)

### Đã tạo 6 models:
- [x] `ATM` - Quản lý máy ATM (lines 1590-1617)
- [x] `ATMManagementBoard` - Ban quản lý ATM (lines 1620-1651)
- [x] `Vehicle` - Phương tiện vận chuyển (lines 1654-1673)
- [x] `Person` - Nhân viên (tài xế, bảo vệ) (lines 1676-1718)
- [x] `ATMReplenishment` - Phiếu tiếp quỹ (lines 1721-1960)
- [x] `ATMDiscrepancy` - Giao dịch thừa/thiếu quỹ (lines 1963-2117)

### Helper function:
- [x] `num_to_vietnamese_words()` - Chuyển số thành chữ (line 2120)

### Dependencies:
```python
from django.db import models
from django.contrib.auth.models import Group, User
from django.core.validators import FileExtensionValidator
import unicodedata
```

## ✅ 2. Admin (templates_app/admin.py)

### Đã đăng ký 6 admin classes:
- [x] `ATMAdmin` (lines 750-766)
- [x] `ATMManagementBoardAdmin` (lines 769-784)
- [x] `VehicleAdmin` (lines 787-803)
- [x] `PersonAdmin` (lines 806-825)
- [x] `ATMReplenishmentAdmin` (lines 828-864)
- [x] `ATMDiscrepancyAdmin` (lines 867-927)

### Import statement (line 11):
```python
ATM, ATMManagementBoard, Vehicle, Person, ATMReplenishment, ATMDiscrepancy
```

## ✅ 3. Forms (templates_app/forms.py)

### Đã tạo 2 forms:
- [x] `ATMReplenishmentForm` (lines 286-311)
- [x] `ATMDiscrepancyForm` (lines 314-356)

### Import statement (line 283):
```python
from .models import ATM, ATMManagementBoard, Vehicle, Person, ATMReplenishment, ATMDiscrepancy
```

## ✅ 4. Views (templates_app/views.py)

### Đã tạo 9 views:
- [x] `atm_dashboard` (lines 4307-4350)
- [x] `atm_replenishment_create` (lines 4353-4383)
- [x] `atm_load_replenishment_data` (lines 4386-4430) - **Tải file trực tiếp**
- [x] `atm_replenishment_list` (lines 4433-4463)
- [x] `atm_discrepancy_list` (lines 4474-4504)
- [x] `atm_discrepancy_create` (lines 4507-4530)
- [x] `atm_discrepancy_edit` (lines 4533-4556)
- [x] `atm_discrepancy_delete` (lines 4559-4576)
- [x] `atm_load_discrepancy_data` (lines 4579-4622) - **Tải file trực tiếp**

### Import statements:
```python
from .models import ATM, ATMManagementBoard, Vehicle, Person, ATMReplenishment, ATMDiscrepancy
from .forms import ATMReplenishmentForm, ATMDiscrepancyForm
from .utils import render_word_template
from .models import GlobalConfig
```

### Variable Library (lines 1148-1301):
- [x] 93 biến ATM replenishment
- [x] 48 biến ATM discrepancy

## ✅ 5. URLs (templates_app/urls.py)

### Đã tạo 9 URL patterns (lines 83-94):
```python
# ATM Management
path('atm/', views.atm_dashboard, name='atm_dashboard'),
path('atm/replenishment/create/', views.atm_replenishment_create, name='atm_replenishment_create'),
path('atm/replenishment/list/', views.atm_replenishment_list, name='atm_replenishment_list'),
path('atm/replenishment/<int:replenishment_id>/template/<int:template_id>/', views.atm_load_replenishment_data, name='atm_load_replenishment_data'),

# ATM Discrepancy Management
path('atm/discrepancy/list/', views.atm_discrepancy_list, name='atm_discrepancy_list'),
path('atm/discrepancy/create/', views.atm_discrepancy_create, name='atm_discrepancy_create'),
path('atm/discrepancy/<int:discrepancy_id>/edit/', views.atm_discrepancy_edit, name='atm_discrepancy_edit'),
path('atm/discrepancy/<int:discrepancy_id>/delete/', views.atm_discrepancy_delete, name='atm_discrepancy_delete'),
path('atm/discrepancy/<int:discrepancy_id>/template/<int:template_id>/', views.atm_load_discrepancy_data, name='atm_load_discrepancy_data'),
```

## ✅ 6. Templates

### Đã tạo 6 template files:
- [x] `dashboard.html` - Dashboard tổng quan
- [x] `replenishment_form.html` - Form tạo phiếu tiếp quỹ
- [x] `replenishment_list.html` - Danh sách phiếu tiếp quỹ
- [x] `discrepancy_form.html` - Form tạo/sửa giao dịch thừa/thiếu
- [x] `discrepancy_list.html` - Danh sách giao dịch thừa/thiếu
- [x] `discrepancy_confirm_delete.html` - Xác nhận xóa

### Template location:
```
templates_app/templates/templates_app/atm/
```

## ✅ 7. Navigation (base.html)

### Đã thêm tab ATM (lines 68-74):
```html
{% if user.is_superuser %}
<li class="nav-item">
    <a class="nav-link" href="{% url 'atm_dashboard' %}">
        <i class="bi bi-credit-card-2-front"></i> ATM
    </a>
</li>
{% endif %}
```

## ⚠️ 8. Cần Thực Hiện Khi Triển Khai Offline

### Bước 1: Tạo migrations
```bash
python manage.py makemigrations
```

### Bước 2: Chạy migrations
```bash
python manage.py migrate
```

### Bước 3: Tạo dữ liệu ban đầu (qua Django Admin)

#### 3.1. Tạo 3 máy ATM:
- Vào `/admin/templates_app/atm/`
- Thêm 3 máy ATM với thông tin:
  - ID máy (primary key)
  - Số Serial
  - Địa chỉ
  - Loại máy
  - Dòng máy
  - Ngày lắp đặt

#### 3.2. Tạo Ban quản lý ATM:
- Vào `/admin/templates_app/atmmanagementboard/`
- Thêm 3 người:
  - Trưởng Ban (position: team_leader)
  - Trưởng phòng KTNQ (position: treasury_head)
  - Cán bộ phụ trách ATM (position: atm_officer)

#### 3.3. Tạo 2 phương tiện:
- Vào `/admin/templates_app/vehicle/`
- Thêm 2 xe:
  - Biển số: 94A - 021.46
  - Biển số: 94A - 059.88

#### 3.4. Tạo nhân viên (Tài xế và Bảo vệ):
- Vào `/admin/templates_app/person/`
- Thêm tài xế và bảo vệ với:
  - Loại (person_type): driver hoặc guard
  - Họ tên
  - Số CCCD
  - Ngày cấp, Nơi cấp

### Bước 4: Tạo mẫu Word template
- Upload các mẫu Word với tên chứa "ATM"
- Ví dụ: "ATM - Phiếu tiếp quỹ", "ATM - Báo cáo thừa thiếu"
- Sử dụng các biến từ Variable Library

## 📋 9. Dependencies Cần Thiết

### Python packages (đã có sẵn):
```
Django >= 3.2
python-docx-template (cho render_word_template)
```

### Frontend (đã có sẵn):
```
Bootstrap 5
Bootstrap Icons
```

## 🔍 10. Kiểm Tra Hoạt Động

### Test checklist sau khi triển khai:

#### Dashboard:
- [ ] Truy cập `/atm/` hiển thị dashboard
- [ ] Thống kê hiển thị đúng (số máy ATM, phiếu tiếp quỹ, thừa/thiếu quỹ)
- [ ] Quick actions hoạt động
- [ ] Bảng gần đây hiển thị

#### Phiếu tiếp quỹ:
- [ ] Tạo phiếu mới `/atm/replenishment/create/`
- [ ] Tự động tính tổng tiền
- [ ] Chuyển số thành chữ hoạt động
- [ ] Danh sách phiếu `/atm/replenishment/list/`
- [ ] Chọn template → tải file Word thành công

#### Giao dịch thừa/thiếu quỹ:
- [ ] Tạo giao dịch mới `/atm/discrepancy/create/`
- [ ] Validation ngày hoạt động (end > start)
- [ ] Sửa giao dịch
- [ ] Xóa giao dịch (hiển thị confirm)
- [ ] Danh sách hiển thị đầy đủ 12 cột
- [ ] Chọn template → tải file Word thành công

#### Word Templates:
- [ ] File tải về có tên đúng format
- [ ] Dữ liệu merge vào Word đúng
- [ ] Biến toàn cục (chi nhánh, custom) được thêm
- [ ] Số tiền bằng chữ hiển thị chính xác

## 🚨 11. Các Vấn Đề Tiềm Ẩn

### Đã xử lý:
- ✅ Template filtering - chỉ hiển thị templates có "ATM" trong tên
- ✅ Direct download - không qua preview page
- ✅ Permissions - chỉ superuser truy cập
- ✅ Date validation - chu kỳ kiểm quỹ
- ✅ Vietnamese number conversion
- ✅ Session data cleanup

### Cần lưu ý:
- ⚠️ Đảm bảo `render_word_template()` trong `utils.py` hoạt động
- ⚠️ Đảm bảo `GlobalConfig.get_instance()` không lỗi
- ⚠️ Kiểm tra file permissions cho uploads
- ⚠️ Backup database trước khi migrate

## 📝 12. Tóm Tắt Files Đã Thay Đổi

```
templates_app/
├── models.py (Added 6 models + helper function)
├── admin.py (Added 6 admin classes)
├── forms.py (Added 2 forms)
├── views.py (Added 9 views + 141 variables to library)
├── urls.py (Added 9 URL patterns)
└── templates/
    └── templates_app/
        ├── base.html (Added ATM tab)
        ├── variable_library.html (Added 2 sections)
        └── atm/
            ├── dashboard.html
            ├── replenishment_form.html
            ├── replenishment_list.html
            ├── discrepancy_form.html
            ├── discrepancy_list.html
            └── discrepancy_confirm_delete.html
```

## ✅ 13. Kết Luận

Module ATM đã được implement đầy đủ và sẵn sàng triển khai offline với:
- ✅ **Models**: 6 models với full validation và methods
- ✅ **Admin**: Complete CRUD interface
- ✅ **Forms**: User-friendly với validation
- ✅ **Views**: 9 views với proper error handling
- ✅ **Templates**: 6 templates responsive với Bootstrap 5
- ✅ **URLs**: RESTful routing
- ✅ **Variables**: 141 biến cho Word templates
- ✅ **Permissions**: Superuser only access
- ✅ **Direct Download**: No preview page needed

**Chỉ cần chạy migrations và tạo dữ liệu ban đầu là có thể sử dụng ngay!**

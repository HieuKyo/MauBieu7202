# Module Chi Luong (Salary)

Module quan ly chi luong va thu ho cho he thong MauBieu7202

## Chuc nang chinh

### 1. Upload va xu ly file Excel/CSV
- Upload file Excel/CSV chua thong tin chi tra
- Chuyen doi sang dinh dang CSV chuan cho Agribank
- Xu ly 2 loai giao dich: Chi tra luong (PAYROLL) va Thu ho (COLLECTION)
- Tu dong nhan dien ma ngan hang
- Phat hien va canh bao STK trung lap

### 2. Quan ly du lieu
- Quan ly danh sach nguoi thu huong (Beneficiary)
- Quan ly tai khoan don vi chi tra (CompanyAccount)
- Luu lich su xu ly file (ProcessingHistory)
- Quan ly danh sach ngan hang (Bank)

### 3. Phan quyen
- Nhom Admins: Truy cap day du Dashboard, quan ly du lieu, xem lich su
- Nhom GiaoDichViens: Chi truy cap chuc nang upload va xu ly file
- Redirect tu dong theo quyen sau khi dang nhap

### 4. Dashboard thong ke
- Thong ke theo tuan/thang/quy/nam
- Tong so tien da chi tra
- So luong giao dich
- So file da xu ly

## Cau truc thu muc

```
salary/
├── models.py              # 4 models: Bank, CompanyAccount, ProcessingHistory, Beneficiary
├── views.py               # Cac views xu ly
├── forms.py               # Forms cho Beneficiary va CompanyAccount
├── services.py            # Logic xu ly file Excel/CSV
├── decorators.py          # Decorator phan quyen group_required
├── resources.py           # Resources cho import/export
├── admin.py               # Cau hinh admin voi import/export
├── urls.py                # URL routing
├── templates/salary/      # Cac template HTML
├── templatetags/          # Custom template tags cho phan quyen
└── fixtures/              # Du lieu mau (banks.csv)
```

## URL Endpoints

- `/salary/` - Dashboard (Admins only)
- `/salary/upload/` - Upload file (Admins, GiaoDichViens)
- `/salary/history/` - Lich su xu ly (Admins only)
- `/salary/history/<id>/` - Chi tiet xu ly
- `/salary/history/<id>/download/` - Tai file CSV ket qua
- `/salary/beneficiaries/` - Danh sach nguoi thu huong (Admins only)
- `/salary/accounts/` - Danh sach tai khoan cong ty (Admins only)

## Dinh dang file import

File Excel/CSV can co cac cot:
- `full_name` - Ho va ten (bat buoc)
- `account_number` - So tai khoan (bat buoc)
- `amount` - So tien (bat buoc)
- `description` - Noi dung (bat buoc)
- `bank_name` hoac `bank_code` - Ngan hang (tuy chon)

## Cai dat

1. Them vao INSTALLED_APPS trong settings.py:
```python
INSTALLED_APPS = [
    ...
    'import_export',
    'salary',
]
```

2. Them vao urls.py:
```python
path('salary/', include('salary.urls')),
```

3. Chay migrations:
```bash
python manage.py makemigrations salary
python manage.py migrate
```

4. Tao groups:
```python
from django.contrib.auth.models import Group
Group.objects.create(name='Admins')
Group.objects.create(name='GiaoDichViens')
```

5. Import ngan hang:
```bash
python manage.py shell
>>> from salary.models import Bank
>>> import csv
>>> with open('salary/fixtures/banks.csv', 'r', encoding='utf-8') as f:
...     reader = csv.DictReader(f)
...     for row in reader:
...         Bank.objects.get_or_create(code=row['code'], defaults={'name': row['name']})
```

## Luu y

- Module xu ly so tien voi kieu Decimal de dam bao do chinh xac
- Su dung unidecode de xu ly tieng Viet co dau
- CSV output co encoding UTF-8 BOM cho Excel
- Dependencies: django-import-export, pandas, unidecode, openpyxl

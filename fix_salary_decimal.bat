@echo off
echo === Fix Salary Decimal Error ===
echo.

REM Chuyen den thu muc project - chinh lai duong dan neu can
cd /d D:\MauBieu7202

echo [1/3] Kiem tra Python...
python --version
if errorlevel 1 (
    echo LOI: Khong tim thay Python
    pause
    exit /b 1
)

echo.
echo [2/3] Fix gia tri decimal trong database...
python -c "
import sqlite3
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

try:
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()

    c.execute('SELECT id, total_amount FROM salary_processinghistory')
    rows = c.fetchall()

    fixed = 0
    errors = 0
    for row_id, amount in rows:
        if amount is None:
            continue
        try:
            # Convert sang string truoc de tranh loi float -> Decimal
            fixed_val = str(Decimal(str(float(amount))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            c.execute('UPDATE salary_processinghistory SET total_amount = ? WHERE id = ?', (fixed_val, row_id))
            fixed += 1
        except (InvalidOperation, ValueError) as e:
            print(f'  Khong fix duoc id={row_id}, amount={amount}: {e}')
            errors += 1

    conn.commit()
    conn.close()
    print(f'Da fix {fixed} records, {errors} loi')
    print('Database OK!')
except Exception as e:
    print(f'LOI: {e}')
    import traceback
    traceback.print_exc()
"

echo.
echo [3/3] Patch model salary/models.py (them null=True cho total_amount)...
python -c "
import re

filepath = 'salary/models.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=\"Tong so tien\"
    )'''

new = '''    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        null=True,
        blank=True,
        verbose_name=\"Tong so tien\"
    )'''

# Tim va thay the voi regex linh hoat hon
pattern = r'(total_amount = models\.DecimalField\([^)]*\))'
match = re.search(r'total_amount = models\.DecimalField\(.*?verbose_name=.*?\)', content, re.DOTALL)
if match:
    old_text = match.group(0)
    if 'null=True' not in old_text:
        # Chen null=True truoc verbose_name
        new_text = old_text.replace(
            'verbose_name=',
            'null=True,\n        blank=True,\n        verbose_name='
        )
        content = content.replace(old_text, new_text)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print('Da them null=True vao total_amount trong models.py')
    else:
        print('models.py da co null=True, bo qua')
else:
    print('Khong tim thay field total_amount trong models.py, kiem tra lai')
"

echo.
echo === Hoan thanh! Khoi dong lai server Django ===
pause

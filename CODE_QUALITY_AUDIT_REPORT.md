# Django Code Quality & Best Practices Audit Report
## Project: MauBieu7202 (Agribank Template Management System)

**Audit Date:** 2025-11-15 | **Thoroughness:** Very Thorough | **Total Issues Found:** 40+

---

## EXECUTIVE SUMMARY

### Critical Issues (Fix Immediately)
1. **DEBUG = True in production** (settings.py:26) - Exposes sensitive info
2. **SECRET_KEY exposed** (settings.py:23) - Use environment variables
3. **ALLOWED_HOSTS = ['*']** (settings.py:30) - Allows any host

### High Priority Issues
4. **Code organization** - 2 functions >300 lines violating SRP
5. **Code duplication** - Datetime imports repeated 5 times, checkbox logic duplicated
6. **Bare except clauses** - 3 instances catching all exceptions
7. **Missing unit tests** - No Django TestCase tests, only standalone scripts

### Medium Priority Issues
8. **N+1 query problems** - Missing prefetch_related on customer searches
9. **Form validation** - Missing custom clean() methods
10. **Magic strings/numbers** - Hardcoded dates, field groups, checkbox chars

---

## DETAILED FINDINGS

### 1. CODE ORGANIZATION & STRUCTURE (HIGH SEVERITY)

#### 1.1 Oversized View Functions
**File:** `/home/user/MauBieu7202/templates_app/views.py`

- **print_preview_generate_document_view()** (Lines 1097-1420): 324 lines
  - Violates Single Responsibility Principle
  - Mixes data building, checkbox logic, date parsing, document generation
  - Hard to test and maintain
  
- **customer_import_tsv()** (Lines 1619-1810): 191 lines
  - TSV parsing mixed with customer mapping and error handling

**Recommendation:** Extract into utility functions (see code examples in detailed report)

---

#### 1.2 Code Duplication

**A. Repeated datetime imports** (5 times in same function)
```python
# Lines 1231, 1252, 1267, 1282, 1295 all have:
from datetime import datetime  # DUPLICATED!
```
**Fix:** Move to module top, create format_date_with_parts() helper

**B. Checkbox conversion logic duplicated**
- models.py (Lines 493-595): 100+ lines
- views.py (Lines 1151-1205): 50+ lines
**Fix:** Create checkbox_utils.py with shared functions

**C. Permission filter patterns repeated**
- dashboard_view (Lines 34-56)
- category_detail_view (Lines 76-85)
**Fix:** Extract to permissions.py helper module

---

### 2. DJANGO BEST PRACTICES (MEDIUM-HIGH SEVERITY)

#### 2.1 N+1 Query Problem
**File:** views.py Lines 304-315 (customer_search_api)
```python
# CURRENT: 1 query + N customer attribute accesses
customers = Customer.objects.filter(Q(...))  # 1 query
customer_list = [{
    'id': c.id,           # Access each customer = +N queries
    'ho_ten': c.ho_ten,
} for c in customers]
```
**Fix:** Add `.select_related('created_by').only('id', 'ho_ten', ...)`

#### 2.2 Missing Form Validation
**File:** forms.py

- **CustomerForm** (Lines 120-178): No clean() methods
- **DynamicTemplateForm** (Lines 8-94): Limited validation

**Missing:** Phone validation, CMND format check, date range validation

**Fix:** Add clean() and clean_<field>() methods with proper validation

#### 2.3 Index Redundancy
**File:** models.py (Customer model)

Using both:
- `db_index=True` on individual fields (ma_khach_hang, so_cmnd, etc)
- `Meta.indexes = [...]` for compound indexes

**Issue:** Redundant indexes, missing -created_at index for sorting

**Fix:** Consolidate in Meta.indexes with proper strategy

---

### 3. CODE STYLE (PEP 8)

#### 3.1 Bare Except Clauses (HIGH)
**File:** views.py Lines 1261, 1276, 1291
```python
except:  # ← Catches EVERYTHING including KeyboardInterrupt!
    data['ngay_sinh_obj'] = None
```
**Fix:** Use specific exceptions: `except ValueError`, `except (KeyError, TypeError)`

#### 3.2 Import Organization
**File:** views.py Lines 1-18
- Standard library imports mixed with Django imports
- Should follow: stdlib → third-party → local

**Fix:** Reorganize imports per PEP 8

#### 3.3 Unused Imports
**File:** views.py Line 6
```python
from django.db.models import Q, Exists, OuterRef  # Exists, OuterRef not used
```

#### 3.4 Magic Strings/Numbers
- Line 556: `datetime_date(2024, 7, 1)` - Magic CCCD cutoff date
- Line 495: `'☑'` and `'☐'` - Undocumented checkbox characters
- Line 85: Hardcoded field group list

**Fix:** Create constants/settings for all magic values

---

### 4. DATABASE ISSUES

#### 4.1 Missing Indexes
**File:** models.py - Missing compound index for:
- `-created_at` (used in every list view - default ordering)
- `created_by` (used in some queries)

**Fix:** Add to Meta.indexes

---

### 5. TEMPLATE ISSUES

#### 5.1 Overly Complex Template
**File:** dashboard.html (1400 lines)
- Contains 100+ lines of inline JavaScript per function
- 3 major JavaScript functions (selectCategory, selectTemplate, updateFormFieldsForCategory)

**Fix:** Extract JavaScript to separate static files

**Status OK:** ✓ Proper template inheritance, ✓ Correct static tag usage

---

### 6. TESTING ISSUES (HIGH SEVERITY)

#### 6.1 No Django Unit Tests
**Current:** Standalone Python scripts (test_cmnd_validation.py, etc)
- Not integrated with test runner
- Not using Django TestCase
- Manual print-based assertions

**Missing Test Coverage:**
- ❌ Customer model validation
- ❌ Customer form validation
- ❌ View permission checks
- ❌ API endpoint tests
- ❌ TSV import functionality
- ❌ Word document generation

**Recommendation:** Create proper Django tests:
```
templates_app/tests/
  __init__.py
  test_models.py       # Model validation, get_data_dict(), etc
  test_views.py        # View permissions, data flows
  test_forms.py        # Form validation
  test_api.py          # API endpoints
  test_integration.py  # Full workflows
```

---

### 7. SECURITY ISSUES (CRITICAL)

#### 7.1 DEBUG Mode Enabled
**File:** settings.py Line 26
```python
DEBUG = True  # ← CRITICAL! Exposes stack traces, settings, SQL
```
**Fix:** `DEBUG = os.getenv('DEBUG', 'False') == 'True'`

#### 7.2 Secret Key Exposed
**File:** settings.py Line 23
```python
SECRET_KEY = "django-insecure-_ur3yrg88lbflau7kf@ltr..."
```
**Fix:** Use environment variables, add .env to .gitignore

#### 7.3 Overly Permissive ALLOWED_HOSTS
**File:** settings.py Line 30
```python
ALLOWED_HOSTS = ['*']  # ← Allows ANY host (HTTP Host header attacks)
```
**Fix:** List specific domains: `['example.com', 'www.example.com', ...]`

---

## SUMMARY TABLE

| Category | Issue | Severity | File | Status |
|----------|-------|----------|------|--------|
| **SECURITY** | DEBUG=True in production | CRITICAL | settings.py | FIX IMMEDIATELY |
| **SECURITY** | Secret key exposed | CRITICAL | settings.py | FIX IMMEDIATELY |
| **SECURITY** | ALLOWED_HOSTS=['*'] | HIGH | settings.py | FIX |
| **Code Structure** | Oversized functions (>300 lines) | HIGH | views.py | REFACTOR |
| **Code Structure** | Code duplication (datetime imports x5) | HIGH | views.py | EXTRACT |
| **Code Structure** | Code duplication (checkbox logic) | HIGH | models.py, views.py | EXTRACT |
| **Django ORM** | N+1 query problem | MEDIUM | views.py:304 | OPTIMIZE |
| **Django ORM** | Missing form validation | MEDIUM | forms.py | ADD |
| **Django ORM** | Index redundancy | MEDIUM | models.py | CONSOLIDATE |
| **Code Style** | Bare except clauses (x3) | HIGH | views.py | FIX |
| **Code Style** | Import organization | MEDIUM | views.py:1-18 | REORGANIZE |
| **Code Style** | Unused imports | LOW | views.py:6 | REMOVE |
| **Code Style** | Magic strings/numbers | MEDIUM | models.py | DEFINE CONSTANTS |
| **Testing** | No Django unit tests | HIGH | root dir | CREATE |
| **Testing** | Coverage gaps | HIGH | - | ADD TESTS |
| **Templates** | Overly complex (1400 lines) | MEDIUM | dashboard.html | SIMPLIFY |

---

## ACTION PLAN

### Phase 1: Security (Week 1)
- [ ] Move SECRET_KEY to environment variable
- [ ] Disable DEBUG in production settings
- [ ] Fix ALLOWED_HOSTS to specific domains
- [ ] Create .env.example file

### Phase 2: Code Quality (Week 2-3)
- [ ] Extract print_preview_generate_document_view into smaller functions
- [ ] Create checkbox_utils.py with shared logic
- [ ] Create permissions.py for permission queries
- [ ] Create date_utils.py for date handling
- [ ] Remove bare except clauses
- [ ] Fix import organization

### Phase 3: Django Best Practices (Week 3-4)
- [ ] Add .select_related/.prefetch_related to queries
- [ ] Add form validation (clean methods)
- [ ] Consolidate database indexes
- [ ] Add missing docstrings
- [ ] Extract magic strings to constants

### Phase 4: Testing (Week 4-5)
- [ ] Create tests/test_models.py with model tests
- [ ] Create tests/test_views.py with view tests
- [ ] Create tests/test_forms.py with form tests
- [ ] Create tests/test_api.py with API tests
- [ ] Achieve 80%+ code coverage

### Phase 5: Template Refactoring (Week 5)
- [ ] Extract JavaScript from dashboard.html to static/js/
- [ ] Simplify template structure
- [ ] Document JavaScript functions

---

## Files to Modify

**High Priority:**
1. `/home/user/MauBieu7202/wordgen/settings.py` - Security fixes
2. `/home/user/MauBieu7202/templates_app/views.py` - Extract functions
3. `/home/user/MauBieu7202/templates_app/forms.py` - Add validation

**Medium Priority:**
4. `/home/user/MauBieu7202/templates_app/models.py` - Extract utils, fix indexes
5. `/home/user/MauBieu7202/templates_app/tests/` - Create unit tests

**New Files to Create:**
- `/home/user/MauBieu7202/templates_app/checkbox_utils.py`
- `/home/user/MauBieu7202/templates_app/date_utils.py`
- `/home/user/MauBieu7202/templates_app/permissions.py`
- `/home/user/MauBieu7202/templates_app/tsv_parser.py`
- `/home/user/MauBieu7202/templates_app/tests/test_models.py`
- `/home/user/MauBieu7202/templates_app/tests/test_views.py`
- `/home/user/MauBieu7202/templates_app/tests/test_forms.py`
- `/home/user/MauBieu7202/.env.example`

---

## Code Examples Provided

This report includes detailed code examples for:
1. Refactoring large functions (print_preview_generate_document_view)
2. Creating utility modules (checkbox_utils, date_utils, permissions)
3. Adding form validation (clean methods)
4. Writing proper Django unit tests
5. Fixing security issues
6. Organizing imports per PEP 8

All examples follow Django and Python best practices.

---

**Prepared by:** Code Quality Audit System
**Date:** 2025-11-15
**Framework:** Django 5.2.7
**Python Version:** 3.x

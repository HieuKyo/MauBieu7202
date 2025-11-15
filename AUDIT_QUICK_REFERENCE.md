# Code Quality Audit - Quick Reference Guide

## Critical Issues (MUST FIX)

### Security Issues
| Issue | File | Line(s) | Fix |
|-------|------|---------|-----|
| DEBUG = True | `wordgen/settings.py` | 26 | Use `DEBUG = os.getenv('DEBUG', 'False') == 'True'` |
| Secret key exposed | `wordgen/settings.py` | 23 | Move to .env file |
| ALLOWED_HOSTS = '*' | `wordgen/settings.py` | 30 | List specific domains |

### Code Structure Issues  
| Issue | File | Line(s) | Lines | Fix |
|-------|------|---------|-------|-----|
| Function too large | `templates_app/views.py` | 1097-1420 | 324 | Extract into smaller functions |
| Function too large | `templates_app/views.py` | 1619-1810 | 191 | Extract into tsv_parser.py |
| Datetime import duplicated | `templates_app/views.py` | 1231, 1252, 1267, 1282, 1295 | 5x | Move to top, create utility |
| Checkbox logic duplicated | `models.py` + `views.py` | Multiple | 150+ | Create checkbox_utils.py |
| Permission filter duplicated | `views.py` | 34-56, 76-85 | 2x | Create permissions.py |
| Bare except (ValueError) | `views.py` | 1261 | - | Change to `except ValueError:` |
| Bare except (ValueError) | `views.py` | 1276 | - | Change to `except ValueError:` |
| Bare except (ValueError) | `views.py` | 1291 | - | Change to `except ValueError:` |

---

## High Priority Issues

| Issue | File | Line(s) | Fix |
|-------|------|---------|-----|
| N+1 query problem | `views.py:304-315` | customer_search_api | Add .select_related().only() |
| Missing form validation | `forms.py:120-178` | CustomerForm | Add clean() method |
| Missing form validation | `forms.py:8-94` | DynamicTemplateForm | Add field validators |
| Unused imports | `views.py:6` | `Exists, OuterRef` | Remove from import |
| Import organization | `views.py:1-18` | All | Reorganize: stdlib → third-party → local |
| Magic date (CCCD cutoff) | `models.py:556` | `datetime_date(2024, 7, 1)` | Define constant |
| Magic checkbox chars | `models.py:495` | `'☑'`, `'☐'` | Define constants |
| Hardcoded field groups | `models.py:85` | Default field groups | Move to settings.FIELD_GROUPS |

---

## Medium Priority Issues

| Issue | File | Line(s) | Fix |
|-------|------|---------|-----|
| Index redundancy | `models.py:216-260, 355-358` | db_index + Meta.indexes | Consolidate indexes |
| Missing -created_at index | `models.py:354` | Meta.ordering | Add to Meta.indexes |
| Complex template | `templates_app/templates/dashboard.html` | Lines 1400 | Extract JS to static files |
| No unit tests | `root dir (test_*.py)` | All | Convert to Django TestCase |

---

## Files Summary

### models.py (905 lines)
- **Strengths:** ✓ Good Meta classes, ✓ All __str__ methods, ✓ Validation in clean()
- **Issues:** 
  - Line 85: Hardcoded default field groups
  - Line 495: Magic checkbox strings  
  - Line 556: Magic CCCD cutoff date
  - Line 493-595: Checkbox logic (duplicated in views.py)
  - Index redundancy (db_index=True mixed with Meta.indexes)

### views.py (1924 lines) ← BIGGEST FILE
- **Issues:**
  - Lines 1097-1420: Function too large (324 lines)
  - Lines 1619-1810: Function too large (191 lines)
  - Lines 1231, 1252, 1267, 1282, 1295: Repeated datetime imports
  - Lines 1261, 1276, 1291: Bare except clauses
  - Lines 304-315: N+1 query problem
  - Lines 34-56, 76-85: Repeated permission filters
  - Lines 1-18: Import organization issues
  - Line 6: Unused imports (Exists, OuterRef)

### forms.py (239 lines)
- **Strengths:** ✓ Good widget configuration
- **Issues:**
  - Line 120-178: CustomerForm missing clean() method
  - Line 8-94: DynamicTemplateForm missing field validation

### settings.py (147 lines)
- **Critical Issues:**
  - Line 23: SECRET_KEY exposed ← MUST FIX
  - Line 26: DEBUG = True ← MUST FIX
  - Line 30: ALLOWED_HOSTS = ['*'] ← FIX
  
### templates/dashboard.html (1400 lines)
- **Issues:**
  - Overly complex, 300+ lines of inline JavaScript
  - Should extract to static/js/

---

## Test Coverage Status

| Test Area | Status | Notes |
|-----------|--------|-------|
| Model validation | ❌ Missing | Only standalone test script |
| Form validation | ❌ Missing | No tests |
| View permissions | ❌ Missing | No tests |
| API endpoints | ❌ Missing | No tests |
| TSV import | ❌ Missing | No tests |
| Document generation | ❌ Missing | No tests |

---

## Action Items (Priority Order)

### IMMEDIATE (Next 24 hours)
- [ ] Line 23 (settings.py): Move SECRET_KEY to .env
- [ ] Line 26 (settings.py): Make DEBUG configurable  
- [ ] Line 30 (settings.py): Fix ALLOWED_HOSTS

### THIS WEEK
- [ ] Create checkbox_utils.py with shared functions
- [ ] Create permissions.py with permission helpers
- [ ] Create date_utils.py with date formatting
- [ ] Create tsv_parser.py with TSV utilities
- [ ] Fix 3x bare except clauses (views.py:1261, 1276, 1291)
- [ ] Remove unused imports (views.py:6)
- [ ] Fix import organization (views.py:1-18)

### NEXT WEEK  
- [ ] Extract print_preview_generate_document_view (324 lines)
- [ ] Extract customer_import_tsv (191 lines)
- [ ] Add .select_related() to customer_search_api
- [ ] Add clean() methods to forms
- [ ] Consolidate database indexes
- [ ] Create Django tests directory and basic tests

### FOLLOWING WEEK
- [ ] Create comprehensive test suite
- [ ] Extract dashboard.html JavaScript
- [ ] Define constants for magic strings/numbers
- [ ] Add docstrings to all functions

---

## Statistics

- **Total Python files audited:** 5 main files + admin.py
- **Total lines of code analyzed:** ~3000+
- **Critical issues found:** 3
- **High priority issues:** 18
- **Medium priority issues:** 8
- **Functions > 100 lines:** 2 (views.py)
- **Code duplication instances:** 3 major, multiple minor
- **Test coverage:** 0% (no Django unit tests)


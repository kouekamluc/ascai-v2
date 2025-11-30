# Template Error Prevention Guide

This document outlines common Django template errors and how they've been prevented in this project.

## Common Errors Fixed

### 1. Python-style Function Calls in Templates ❌

**Error**: `user.has_perm('governance.view_member')`  
**Fix**: Use Django's `perms` object: `perms.governance.view_member`

**Files Fixed**:
- `templates/includes/navbar.html`
- `templates/dashboard/partials/sidebar_nav.html`

### 2. Queryset Methods in Templates ❌

**Error**: `profile_user.executive_positions.filter.status='active'`  
**Fix**: Move filtering logic to views, pass filtered data to templates

**Files Fixed**:
- `templates/dashboard/profile/view.html` - Now uses `active_positions` from view
- `apps/dashboard/views.py` - Added `get_context_data()` to filter positions

### 3. Queryset Property Access in Templates ⚠️

**Issue**: `approval.signer.executive_positions.exists` and `.first()`  
**Fix**: Pre-fetch and attach to objects in view

**Files Fixed**:
- `templates/governance/finances/expense_approval.html` - Now uses `approval.signer_position`
- `apps/governance/views.py` - Pre-fetches positions in `get_context_data()`

### 4. Optional Relationship Access ❌

**Error**: Accessing `.user` on optional ForeignKeys without checking  
**Fix**: Always check if relationship exists before accessing

**Files Fixed**:
- `templates/governance/finances/dues.html` - Checks `due.member` and `due.member.user`
- `templates/governance/members/list.html` - Checks `member.user`
- `templates/governance/members/detail.html` - Checks `member.user`
- `templates/governance/assemblies/detail.html` - Checks `attendance.user`

### 5. Database Attribute Access on Non-DB Objects ❌

**Error**: `EmailConfirmationHMAC` object has no attribute `pk`  
**Fix**: Use `hasattr()` to check for attribute existence

**Files Fixed**:
- `apps/accounts/adapters.py` - Checks `hasattr(emailconfirmation, 'pk')` before accessing

## Best Practices Implemented

### Template Best Practices

1. **Never use Python-style function calls**:
   - ❌ `user.has_perm('app.permission')`
   - ✅ `perms.app.permission`

2. **Never use queryset methods in templates**:
   - ❌ `objects.filter(status='active')`
   - ✅ Filter in view, pass to template

3. **Always check optional relationships**:
   - ❌ `{{ object.related.user.name }}`
   - ✅ `{% if object.related and object.related.user %}{{ object.related.user.name }}{% endif %}`

4. **Use `hasattr()` for dynamic attributes**:
   - ❌ `if object.pk:`
   - ✅ `if hasattr(object, 'pk') and object.pk:`

### View Best Practices

1. **Pre-fetch related data**:
   ```python
   queryset = Model.objects.select_related('user').prefetch_related('positions')
   ```

2. **Annotate counts for performance**:
   ```python
   queryset = Model.objects.annotate(member_count=Count('members'))
   ```

3. **Filter data in views, not templates**:
   ```python
   context['active_positions'] = user.executive_positions.filter(status='active')
   ```

4. **Handle optional relationships safely**:
   ```python
   try:
       if hasattr(obj, 'related_field'):
           context['data'] = obj.related_field.all()
   except Exception:
       context['data'] = []
   ```

## Checklist for New Templates

When creating new templates, ensure:

- [ ] No Python-style function calls (use `perms.*` instead of `has_perm()`)
- [ ] No queryset methods (`.filter()`, `.exists()`, `.first()`, etc.)
- [ ] Optional relationships checked with `{% if %}`
- [ ] Dynamic attributes checked with `hasattr()` in views
- [ ] Counts annotated in views when possible
- [ ] Related data pre-fetched in views

## Files Monitored

Key files to check when adding new features:

- All files in `templates/governance/`
- `templates/dashboard/`
- `templates/includes/`
- `apps/governance/views.py`
- `apps/dashboard/views.py`
- `apps/accounts/adapters.py`


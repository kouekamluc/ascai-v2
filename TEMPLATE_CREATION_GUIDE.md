# Governance Templates Creation Guide

This document lists all templates that need to be created for the governance module. The templates follow a consistent design pattern using Tailwind CSS and the ASCAI design system.

## Template Structure

All templates extend `governance/base.html` and use:
- Tailwind CSS classes
- Cameroon color scheme (cameroon-green, etc.)
- Consistent card layouts (`governance-card` class)
- Responsive grid layouts
- Form styling with `form-input`, `form-textarea`, etc.
- Button classes: `btn-primary`, `btn-secondary`

## Completed Templates ✅

### Elections
- ✅ `elections/commission_list.html`
- ✅ `elections/commission_detail.html`
- ✅ `elections/commission_form.html`
- ✅ `elections/election_list.html`
- ✅ `elections/election_detail.html`
- ✅ `elections/election_form.html`
- ✅ `elections/candidacy_list.html`

## Remaining Templates to Create

### Elections (Remaining)
- [ ] `elections/candidacy_apply.html` - Form for users to apply for candidacy
- [ ] `elections/vote.html` - Voting interface for elections (secret ballot)

### Board of Auditors
- [ ] `auditors/board_list.html` - List all boards of auditors
- [ ] `auditors/board_detail.html` - Board details with members and reports
- [ ] `auditors/board_form.html` - Create/edit board form
- [ ] `auditors/audit_report_list.html` - List audit reports
- [ ] `auditors/audit_report_form.html` - Create audit report form

### Disciplinary System
- [ ] `disciplinary/case_list.html` - List disciplinary cases
- [ ] `disciplinary/case_detail.html` - Case details with sanctions
- [ ] `disciplinary/case_form.html` - Report/create disciplinary case
- [ ] `disciplinary/sanction_form.html` - Apply disciplinary sanction

### Association Events
- [ ] `events/event_list.html` - List association events
- [ ] `events/event_detail.html` - Event details with organizing committee
- [ ] `events/event_form.html` - Create/edit event form

### Communications
- [ ] `communications/list.html` - List communications
- [ ] `communications/detail.html` - Communication details
- [ ] `communications/form.html` - Create/edit communication form

### Association Documents
- [ ] `documents/list.html` - List documents
- [ ] `documents/form.html` - Upload document form

### Additional Assembly Templates
- [ ] `assemblies/propose_agenda_item.html` - Member proposal form
- [ ] `assemblies/request_extraordinary.html` - Request extraordinary assembly

## Template Patterns

### List Template Pattern
```html
{% extends "governance/base.html" %}
{% load i18n %}

{% block title %}{% trans "Title" %} - {{ block.super }}{% endblock %}
{% block page_heading %}{% trans "Title" %}{% endblock %}

{% block content %}
<div class="flex items-center justify-between mb-6">
    <div>
        <h2 class="text-2xl font-bold text-gray-900">{% trans "Title" %}</h2>
        <p class="text-sm text-gray-600 mt-1">{% trans "Description" %}</p>
    </div>
    <a href="{% url 'governance:create_url' %}" class="btn-primary">
        {% trans "Create" %}
    </a>
</div>

{% if items %}
<div class="space-y-4">
    {% for item in items %}
    <div class="governance-card">
        <!-- Item content -->
    </div>
    {% endfor %}
</div>
{% else %}
<div class="empty-state">
    <p class="text-gray-500">{% trans "No items found" %}</p>
</div>
{% endif %}
{% endblock %}
```

### Form Template Pattern
```html
{% extends "governance/base.html" %}
{% load i18n %}

{% block title %}{% trans "Form Title" %} - {{ block.super }}{% endblock %}
{% block page_heading %}{% trans "Form Title" %}{% endblock %}

{% block content %}
<div class="max-w-2xl">
    <form method="post" class="governance-card">
        {% csrf_token %}
        <div class="space-y-6">
            <!-- Form fields -->
        </div>
        <div class="mt-6 flex items-center justify-end space-x-4">
            <a href="{% url 'governance:list_url' %}" class="btn-secondary">
                {% trans "Cancel" %}
            </a>
            <button type="submit" class="btn-primary">
                {% trans "Submit" %}
            </button>
        </div>
    </form>
</div>
{% endblock %}
```

### Detail Template Pattern
```html
{% extends "governance/base.html" %}
{% load i18n %}

{% block title %}{{ object.name }} - {{ block.super }}{% endblock %}
{% block page_heading %}{{ object.name }}{% endblock %}

{% block content %}
<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <div class="lg:col-span-2">
        <div class="governance-card">
            <!-- Main content -->
        </div>
    </div>
    <div>
        <div class="governance-card">
            <!-- Sidebar content -->
        </div>
    </div>
</div>
{% endblock %}
```

## CSS Classes Reference

### Cards
- `governance-card` - Main card container
- `stat-card` - Statistics card with border accent
- `dashboard-card` - Dashboard section card

### Buttons
- `btn-primary` - Primary action button (green)
- `btn-secondary` - Secondary button (gray)
- `btn-danger` - Danger button (red)

### Forms
- `form-input` - Text input
- `form-textarea` - Textarea
- `form-select` - Select dropdown
- `form-checkbox` - Checkbox

### Status Badges
- `bg-green-100 text-green-800` - Success/Active
- `bg-yellow-100 text-yellow-800` - Warning/Pending
- `bg-red-100 text-red-800` - Error/Rejected
- `bg-blue-100 text-blue-800` - Info/In Progress
- `bg-gray-100 text-gray-800` - Neutral/Completed

### Empty States
- `empty-state` - Container for empty state
- `empty-state-icon` - Icon in empty state

## Implementation Priority

1. **High Priority** (Core Functionality):
   - Election voting interface
   - Candidacy application form
   - Disciplinary case management
   - Audit report forms

2. **Medium Priority** (Management):
   - Board of Auditors templates
   - Event management templates
   - Communication templates

3. **Low Priority** (Additional):
   - Document management
   - Assembly proposal forms

## Notes

- All templates should be responsive (mobile-first)
- Use i18n tags for all user-facing text
- Include proper error handling and validation messages
- Follow accessibility best practices
- Use semantic HTML elements
- Include loading states where appropriate









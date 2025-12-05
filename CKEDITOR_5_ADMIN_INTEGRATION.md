# CKEditor 5 Admin Integration Fix

## Issue
The Django admin was not using django-ckeditor-5 for rich text editing. Instead, it was using Unfold's built-in WysiwygWidget (Trix editor).

## Solution
Updated the `BaseAdmin` class in `config/admin.py` to use CKEditor 5 widget instead of Unfold's Trix editor.

## Changes Made

### 1. Updated BaseAdmin Class (`config/admin.py`)

**Before:**
- Used Unfold's `WysiwygWidget` (Trix editor)
- Limited formatting options
- Not using the configured CKEditor 5 setup

**After:**
- Uses `CKEditor5Widget` from `django_ckeditor_5`
- Full CKEditor 5 feature set available
- Uses configurations from `CKEDITOR_5_CONFIGS` in settings

### 2. Implementation Details

The `BaseAdmin` class now:
- Imports `CKEditor5Widget` from `django_ckeditor_5.widgets`
- Overrides `formfield_for_dbfield()` to automatically use CKEditor 5 for all TextField fields
- Falls back to standard Textarea if CKEditor 5 is not available
- Uses the 'default' config from `CKEDITOR_5_CONFIGS`

### 3. CKEditor 5 Configuration

CKEditor 5 is already configured in `config/settings/base.py` with:
- **Default config**: Basic toolbar with headings, bold, italic, links, lists, blockquote, and image upload
- **Extended config**: Full-featured toolbar with tables, code blocks, font colors, and more

## Features Available

With CKEditor 5, admins now have access to:

### Basic Formatting
- Headings (H1, H2, H3)
- Bold, Italic, Underline, Strikethrough
- Text alignment
- Font colors and background colors

### Lists & Structure
- Bulleted lists
- Numbered lists
- Todo lists
- Block quotes

### Advanced Features
- Links
- Images (with upload support)
- Tables
- Code blocks
- Source editing
- Media embeds

### Customizable
- Configuration can be customized per field
- Multiple configs available ('default', 'extends', 'list')
- Toolbar and features configurable in settings

## Usage

All models using `BaseAdmin` automatically get CKEditor 5:

```python
from config.admin import BaseAdmin

@admin.register(News)
class NewsAdmin(BaseAdmin):
    list_display = ['title', 'author', 'created_at']
    # All TextField fields will automatically use CKEditor 5
```

### Using Different Configs

To use a different CKEditor config for specific fields:

```python
class AdvancedPostAdmin(BaseAdmin):
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if isinstance(db_field, models.TextField) and db_field.name == 'content':
            formfield.widget.config_name = 'extends'  # Use extended config
        return formfield
```

## Models Affected

All models that inherit from `BaseAdmin` will now use CKEditor 5:
- ✅ News (content field)
- ✅ Events (description field)
- ✅ Testimonials (testimonial field)
- ✅ Success Stories (story field)
- ✅ Life in Italy (content field)
- ✅ Any other models using `BaseAdmin`

## Testing

After deploying these changes:

1. **Clear Browser Cache**: Old cached admin files might interfere
   - Press `Ctrl + Shift + Delete` (or `Cmd + Shift + Delete` on Mac)
   - Clear cached images and files

2. **Collect Static Files**: Ensure CKEditor 5 static files are collected
   ```bash
   python manage.py collectstatic
   ```

3. **Test in Admin**:
   - Navigate to any model using `BaseAdmin` (e.g., News, Events)
   - Edit a record with a TextField
   - Verify CKEditor 5 toolbar appears
   - Test formatting options (bold, italic, lists, etc.)
   - Test image upload functionality

## Configuration Reference

CKEditor 5 configurations are defined in `config/settings/base.py`:

```python
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload'],
    },
    'extends': {
        # Full-featured toolbar with tables, code blocks, etc.
        ...
    },
}
```

To customize the editor, modify these configurations in settings.py.

## Benefits

1. **Rich Text Editing**: Professional WYSIWYG editor with full formatting options
2. **Image Upload**: Built-in support for image uploads in content
3. **Consistent Experience**: Same editor used across all admin forms
4. **Configurable**: Easy to customize toolbar and features
5. **Modern**: Uses latest CKEditor 5 (not deprecated CKEditor 4)

## Files Modified

1. `config/admin.py`
   - Replaced Unfold WysiwygWidget with CKEditor5Widget
   - Updated BaseAdmin to use formfield_for_dbfield() for widget assignment

## Next Steps

1. Deploy the changes
2. Run `collectstatic` to ensure CKEditor 5 assets are available
3. Test in admin interface
4. Customize CKEditor configurations if needed

The admin interface now uses CKEditor 5 for all TextField fields in models using `BaseAdmin`! 🎉


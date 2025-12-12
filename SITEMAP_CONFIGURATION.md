# Sitemap Configuration

## Overview
This project now includes a comprehensive dynamic sitemap configuration for SEO purposes. The sitemap is automatically generated from your database models and static pages.

## Files Created/Modified

1. **`config/sitemaps.py`** - New file containing all sitemap classes
2. **`config/urls.py`** - Updated to include sitemap URL endpoint

## Sitemap Structure

The sitemap includes the following sections:

### Static Pages (Priority: 1.0 for home, 0.8 for others)
- Home page (`/`)
- Main section index pages (diaspora, community, universities, scholarships, gallery, downloads, contact, mentorship)

### Dynamic Content

1. **News Articles** (Priority: 0.8)
   - All published news articles from the diaspora app

2. **Events** (Priority: 0.8)
   - All published events from the diaspora app

3. **Universities** (Priority: 0.64)
   - All university detail pages

4. **Scholarships** (Priority: 0.64)
   - Active scholarship detail pages
   - Special pages like DISCO Lazio

5. **Gallery Albums** (Priority: 0.64)
   - All gallery album detail pages

6. **Success Stories** (Priority: 0.64)
   - Published success stories from the diaspora app

7. **Diaspora Pages** (Priority: 0.64)
   - News list, events list, testimonials, success stories, life in Italy pages

8. **Account Pages** (Priority: 0.8 for login/signup, 0.64 for password reset)
   - Login, signup, and password reset pages

## Accessing the Sitemap

The sitemap is available at: **`https://ascai.org/sitemap.xml`**

This will automatically generate an XML sitemap index that references all individual sitemaps.

## How It Works

1. Django's sitemap framework automatically generates XML from the sitemap classes
2. Each sitemap class queries the database for relevant content
3. The sitemap is regenerated on each request (for up-to-date content)
4. Only published/public content is included (e.g., `is_published=True` for news, events, success stories)

## SEO Best Practices Implemented

- ✅ Priority values assigned based on page importance
- ✅ Change frequency indicators (weekly, monthly)
- ✅ Last modification dates for dynamic content
- ✅ Only includes public, published content
- ✅ Automatic updates when content changes

## Submitting to Search Engines

1. **Google Search Console**: Submit `https://ascai.org/sitemap.xml`
2. **Bing Webmaster Tools**: Submit `https://ascai.org/sitemap.xml`

## Maintenance

The sitemap requires no manual maintenance - it automatically:
- Updates when new content is published
- Removes unpublished content
- Includes proper modification dates
- Handles URL generation correctly

## Testing

To test the sitemap locally:

```bash
# Run the development server
python manage.py runserver

# Visit in browser
http://localhost:8000/sitemap.xml
```

You should see an XML sitemap index listing all the sitemap sections.

## Notes

- The sitemap is placed outside `i18n_patterns` so it doesn't have language prefixes, which is standard for SEO
- URLs are generated using Django's `reverse()` function, ensuring correct URL structure
- The sitemap respects the same URL patterns as your main application


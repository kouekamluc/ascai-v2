#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive health check script for ASCAI Lazio application.
Tests all major components and logs results.
"""
import os
import sys
import django
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Setup Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

django.setup()

import json
import traceback
from datetime import datetime
from django.test import Client
from django.urls import reverse, NoReverseMatch
from django.db import connection
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

# Log file path
LOG_FILE = BASE_DIR / '.cursor' / 'debug.log'

def log_entry(session_id, run_id, hypothesis_id, location, message, data, timestamp=None):
    """Write a log entry in NDJSON format."""
    if timestamp is None:
        timestamp = int(datetime.now().timestamp() * 1000)
    
    entry = {
        "id": f"log_{timestamp}_{hash(message) % 10000}",
        "timestamp": timestamp,
        "location": location,
        "message": message,
        "data": data,
        "sessionId": session_id,
        "runId": run_id,
        "hypothesisId": hypothesis_id
    }
    
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
    except Exception as e:
        print(f"Error writing log: {e}")

# Initialize
session_id = "health-check-session"
run_id = "run1"
# Use Client with enforce_csrf_checks=False to avoid CSRF issues in tests
# and set proper headers to avoid ALLOWED_HOSTS issues
client = Client(enforce_csrf_checks=False, HTTP_HOST='localhost')

# Test results
results = {
    "url_routing": {"passed": 0, "failed": 0, "errors": []},
    "views": {"passed": 0, "failed": 0, "errors": []},
    "database": {"passed": 0, "failed": 0, "errors": []},
    "templates": {"passed": 0, "failed": 0, "errors": []},
    "static_files": {"passed": 0, "failed": 0, "errors": []},
    "authentication": {"passed": 0, "failed": 0, "errors": []},
    "models": {"passed": 0, "failed": 0, "errors": []}
}

print("=" * 80)
print("ASCAI Lazio Application Health Check")
print("=" * 80)
print()

# Hypothesis A: URL Routing Issues
print("Testing URL Routing (Hypothesis A)...")
log_entry(session_id, run_id, "A", "health_check.py:URL_ROUTING", "Starting URL routing tests", {})

url_tests = [
    ('core:home', {}),
    ('health', {}),
    ('diaspora:index', {}),
    ('diaspora:news_list', {}),
    ('diaspora:event_list', {}),
    ('students:index', {}),
    ('universities:index', {}),
    ('scholarships:index', {}),
    ('gallery:index', {}),
    ('contact:index', {}),
    ('community:index', {}),
    ('mentorship:index', {}),
]

for url_name, kwargs in url_tests:
    try:
        # #region agent log
        log_entry(session_id, run_id, "A", f"health_check.py:reverse_{url_name}", 
                 f"Testing URL reverse for {url_name}", {"url_name": url_name, "kwargs": kwargs})
        # #endregion
        
        url = reverse(url_name, kwargs=kwargs)
        
        # #region agent log
        log_entry(session_id, run_id, "A", f"health_check.py:reverse_success_{url_name}",
                 f"URL reverse successful", {"url_name": url_name, "resolved_url": url})
        # #endregion
        
        results["url_routing"]["passed"] += 1
        print(f"  [OK] {url_name} -> {url}")
    except NoReverseMatch as e:
        # #region agent log
        log_entry(session_id, run_id, "A", f"health_check.py:reverse_error_{url_name}",
                 f"URL reverse failed", {"url_name": url_name, "error": str(e)})
        # #endregion
        
        results["url_routing"]["failed"] += 1
        error_msg = f"{url_name}: {str(e)}"
        results["url_routing"]["errors"].append(error_msg)
        print(f"  [FAIL] {url_name}: {str(e)}")
    except Exception as e:
        # #region agent log
        log_entry(session_id, run_id, "A", f"health_check.py:reverse_exception_{url_name}",
                 f"URL reverse exception", {"url_name": url_name, "error": str(e), "traceback": traceback.format_exc()})
        # #endregion
        
        results["url_routing"]["failed"] += 1
        error_msg = f"{url_name}: Unexpected error - {str(e)}"
        results["url_routing"]["errors"].append(error_msg)
        print(f"  [FAIL] {url_name}: Unexpected error - {str(e)}")

print()

# Hypothesis B: View Execution Issues
print("Testing View Execution (Hypothesis B)...")
log_entry(session_id, run_id, "B", "health_check.py:VIEW_EXECUTION", "Starting view execution tests", {})

view_tests = [
    ('core:home', 200),
    ('health', 200),
    ('diaspora:index', 200),
    ('diaspora:news_list', 200),
    ('diaspora:event_list', 200),
    ('students:index', 200),
    ('universities:index', 200),
    ('scholarships:index', 200),
    ('gallery:index', 200),
    ('contact:index', 200),
    ('community:index', 200),
    ('mentorship:index', 200),
]

for url_name, expected_status in view_tests:
    try:
        # #region agent log
        log_entry(session_id, run_id, "B", f"health_check.py:view_request_{url_name}",
                 f"Requesting view {url_name}", {"url_name": url_name, "expected_status": expected_status})
        # #endregion
        
        url = reverse(url_name)
        response = client.get(url)
        
        # #region agent log
        log_entry(session_id, run_id, "B", f"health_check.py:view_response_{url_name}",
                 f"View response received", {"url_name": url_name, "status_code": response.status_code, 
                 "expected_status": expected_status, "content_length": len(response.content)})
        # #endregion
        
        if response.status_code == expected_status:
            results["views"]["passed"] += 1
            print(f"  [OK] {url_name}: {response.status_code}")
        else:
            results["views"]["failed"] += 1
            error_msg = f"{url_name}: Expected {expected_status}, got {response.status_code}"
            results["views"]["errors"].append(error_msg)
            print(f"  [FAIL] {error_msg}")
    except Exception as e:
        # #region agent log
        log_entry(session_id, run_id, "B", f"health_check.py:view_exception_{url_name}",
                 f"View execution exception", {"url_name": url_name, "error": str(e), 
                 "traceback": traceback.format_exc()})
        # #endregion
        
        results["views"]["failed"] += 1
        error_msg = f"{url_name}: {str(e)}"
        results["views"]["errors"].append(error_msg)
        print(f"  [FAIL] {error_msg}")

print()

# Hypothesis C: Database Connection/Query Issues
print("Testing Database Connection (Hypothesis C)...")
log_entry(session_id, run_id, "C", "health_check.py:DATABASE", "Starting database tests", {})

try:
    # #region agent log
    log_entry(session_id, run_id, "C", "health_check.py:db_connection",
             "Testing database connection", {})
    # #endregion
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        # #region agent log
        log_entry(session_id, run_id, "C", "health_check.py:db_query_success",
                 "Database query successful", {"result": str(result)})
        # #endregion
        
        if result:
            results["database"]["passed"] += 1
            print("  [OK] Database connection: OK")
        else:
            results["database"]["failed"] += 1
            error_msg = "Database query returned no result"
            results["database"]["errors"].append(error_msg)
            print(f"  [FAIL] {error_msg}")
except Exception as e:
    # #region agent log
    log_entry(session_id, run_id, "C", "health_check.py:db_exception",
             "Database connection exception", {"error": str(e), "traceback": traceback.format_exc()})
    # #endregion
    
    results["database"]["failed"] += 1
    error_msg = f"Database connection failed: {str(e)}"
    results["database"]["errors"].append(error_msg)
    print(f"  [FAIL] {error_msg}")

print()

# Hypothesis D: Model Query Issues
print("Testing Model Queries (Hypothesis D)...")
log_entry(session_id, run_id, "D", "health_check.py:MODELS", "Starting model query tests", {})

model_tests = [
    ('apps.diaspora.models.News', 'objects.all()'),
    ('apps.diaspora.models.Event', 'objects.all()'),
    ('apps.universities.models.University', 'objects.all()'),
    ('apps.scholarships.models.Scholarship', 'objects.all()'),
    ('apps.gallery.models.GalleryAlbum', 'objects.all()'),
]

for model_path, query in model_tests:
    try:
        # #region agent log
        log_entry(session_id, run_id, "D", f"health_check.py:model_query_{model_path}",
                 f"Testing model query", {"model_path": model_path, "query": query})
        # #endregion
        
        module_path, model_name = model_path.rsplit('.', 1)
        module = __import__(module_path, fromlist=[model_name])
        model = getattr(module, model_name)
        
        # Execute query
        queryset = eval(f"model.{query}")
        count = queryset.count()
        
        # #region agent log
        log_entry(session_id, run_id, "D", f"health_check.py:model_query_success_{model_path}",
                 f"Model query successful", {"model_path": model_path, "count": count})
        # #endregion
        
        results["models"]["passed"] += 1
        print(f"  [OK] {model_path}: {count} records")
    except Exception as e:
        # #region agent log
        log_entry(session_id, run_id, "D", f"health_check.py:model_exception_{model_path}",
                 f"Model query exception", {"model_path": model_path, "error": str(e), 
                 "traceback": traceback.format_exc()})
        # #endregion
        
        results["models"]["failed"] += 1
        error_msg = f"{model_path}: {str(e)}"
        results["models"]["errors"].append(error_msg)
        print(f"  [FAIL] {error_msg}")

print()

# Hypothesis E: Static Files
print("Testing Static Files (Hypothesis E)...")
log_entry(session_id, run_id, "E", "health_check.py:STATIC_FILES", "Starting static file tests", {})

static_tests = [
    '/static/images/favicon.ico',
    '/static/images/web-app-manifest-512x512.png',
    '/static/css/ascai-design-system.css',
]

for static_path in static_tests:
    try:
        # #region agent log
        log_entry(session_id, run_id, "E", f"health_check.py:static_request_{static_path}",
                 f"Requesting static file", {"static_path": static_path})
        # #endregion
        
        response = client.get(static_path)
        
        # #region agent log
        log_entry(session_id, run_id, "E", f"health_check.py:static_response_{static_path}",
                 f"Static file response", {"static_path": static_path, "status_code": response.status_code,
                 "content_length": len(response.content) if hasattr(response, 'content') else 0})
        # #endregion
        
        if response.status_code == 200:
            results["static_files"]["passed"] += 1
            print(f"  [OK] {static_path}: OK")
        else:
            results["static_files"]["failed"] += 1
            error_msg = f"{static_path}: Status {response.status_code}"
            results["static_files"]["errors"].append(error_msg)
            print(f"  [FAIL] {error_msg}")
    except Exception as e:
        # #region agent log
        log_entry(session_id, run_id, "E", f"health_check.py:static_exception_{static_path}",
                 f"Static file exception", {"static_path": static_path, "error": str(e),
                 "traceback": traceback.format_exc()})
        # #endregion
        
        results["static_files"]["failed"] += 1
        error_msg = f"{static_path}: {str(e)}"
        results["static_files"]["errors"].append(error_msg)
        print(f"  [FAIL] {error_msg}")

print()

# Hypothesis F: Template Rendering
print("Testing Template Rendering (Hypothesis F)...")
log_entry(session_id, run_id, "F", "health_check.py:TEMPLATES", "Starting template rendering tests", {})

template_tests = [
    ('core:home', 'core/home.html'),
    ('diaspora:index', 'diaspora/index.html'),
    ('students:index', 'students/index.html'),
]

for url_name, template_name in template_tests:
    try:
        # #region agent log
        log_entry(session_id, run_id, "F", f"health_check.py:template_render_{url_name}",
                 f"Testing template rendering", {"url_name": url_name, "template_name": template_name})
        # #endregion
        
        url = reverse(url_name)
        response = client.get(url)
        
        # #region agent log
        log_entry(session_id, run_id, "F", f"health_check.py:template_response_{url_name}",
                 f"Template response received", {"url_name": url_name, "status_code": response.status_code,
                 "has_content": len(response.content) > 0, "content_preview": response.content[:100].decode('utf-8', errors='ignore') if response.content else ""})
        # #endregion
        
        if response.status_code == 200 and len(response.content) > 0:
            # Check if template was rendered (basic check)
            if b'<!DOCTYPE html' in response.content or b'<html' in response.content:
                results["templates"]["passed"] += 1
                print(f"  [OK] {template_name}: Rendered")
            else:
                results["templates"]["failed"] += 1
                error_msg = f"{template_name}: No HTML content"
                results["templates"]["errors"].append(error_msg)
                print(f"  [FAIL] {error_msg}")
        else:
            results["templates"]["failed"] += 1
            error_msg = f"{template_name}: Status {response.status_code}"
            results["templates"]["errors"].append(error_msg)
            print(f"  [FAIL] {error_msg}")
    except Exception as e:
        # #region agent log
        log_entry(session_id, run_id, "F", f"health_check.py:template_exception_{url_name}",
                 f"Template rendering exception", {"url_name": url_name, "error": str(e),
                 "traceback": traceback.format_exc()})
        # #endregion
        
        results["templates"]["failed"] += 1
        error_msg = f"{template_name}: {str(e)}"
        results["templates"]["errors"].append(error_msg)
        print(f"  [FAIL] {error_msg}")

print()

# Hypothesis G: Authentication
print("Testing Authentication (Hypothesis G)...")
log_entry(session_id, run_id, "G", "health_check.py:AUTHENTICATION", "Starting authentication tests", {})

try:
    # #region agent log
    log_entry(session_id, run_id, "G", "health_check.py:auth_login_page",
             "Testing login page access", {})
    # #endregion
    
    login_url = reverse('account_login')
    response = client.get(login_url)
    
    # #region agent log
    log_entry(session_id, run_id, "G", "health_check.py:auth_login_response",
             "Login page response", {"status_code": response.status_code, "url": login_url})
    # #endregion
    
    if response.status_code == 200:
        results["authentication"]["passed"] += 1
        print(f"  [OK] Login page: Accessible")
    else:
        results["authentication"]["failed"] += 1
        error_msg = f"Login page: Status {response.status_code}"
        results["authentication"]["errors"].append(error_msg)
        print(f"  [FAIL] {error_msg}")
except Exception as e:
    # #region agent log
    log_entry(session_id, run_id, "G", "health_check.py:auth_exception",
             "Authentication exception", {"error": str(e), "traceback": traceback.format_exc()})
    # #endregion
    
    results["authentication"]["failed"] += 1
    error_msg = f"Authentication test failed: {str(e)}"
    results["authentication"]["errors"].append(error_msg)
    print(f"  [FAIL] {error_msg}")

print()

# Summary
print("=" * 80)
print("HEALTH CHECK SUMMARY")
print("=" * 80)

total_passed = sum(r["passed"] for r in results.values())
total_failed = sum(r["failed"] for r in results.values())

for category, result in results.items():
    total = result["passed"] + result["failed"]
    if total > 0:
        percentage = (result["passed"] / total) * 100
        status = "[OK]" if result["failed"] == 0 else "[FAIL]"
        print(f"{status} {category.upper()}: {result['passed']}/{total} passed ({percentage:.1f}%)")
        if result["errors"]:
            for error in result["errors"][:3]:  # Show first 3 errors
                print(f"    - {error}")

print()
print(f"TOTAL: {total_passed} passed, {total_failed} failed")

# #region agent log
log_entry(session_id, run_id, "SUMMARY", "health_check.py:SUMMARY",
         "Health check completed", {
             "total_passed": total_passed,
             "total_failed": total_failed,
             "results": results
         })
# #endregion

if total_failed == 0:
    print("\n[SUCCESS] All components are working normally!")
    sys.exit(0)
else:
    print(f"\n[FAILED] {total_failed} test(s) failed. Check logs for details.")
    sys.exit(1)

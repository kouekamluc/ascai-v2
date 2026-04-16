"""
Management command to smoke-test the main authentication entry points.
"""
from types import SimpleNamespace
from unittest.mock import patch

from django.conf import settings
from django.core.management.base import BaseCommand
from django.test import Client
from django.test.utils import override_settings
from django.urls import reverse


class Command(BaseCommand):
    help = (
        "Test authentication flows: registration, login, password reset, "
        "email verification, and auth configuration."
    )

    def handle(self, *args, **options):
        self.stdout.write("Testing authentication flows...\n")
        allowed_hosts = sorted({*settings.ALLOWED_HOSTS, "testserver", "localhost"})
        with override_settings(ALLOWED_HOSTS=allowed_hosts):
            client = Client()
            passed = []
            failed = []

            checks = [
                ("Registration page", lambda: self._check_page(client, "account_signup")),
                ("Login page", lambda: self._check_page(client, "account_login")),
                (
                    "Password reset page",
                    lambda: self._check_page(client, "account_reset_password"),
                ),
                (
                    "Email verification notice page",
                    lambda: self._check_page(client, "account_email_verification_notice"),
                ),
            ]

            for label, check in checks:
                self.stdout.write(f"- {label}...")
                try:
                    check()
                except Exception as exc:
                    failed.append(f"{label}: {exc}")
                    self.stdout.write(self.style.ERROR(f"  FAIL {exc}"))
                else:
                    passed.append(label)
                    self.stdout.write(self.style.SUCCESS("  OK"))

            self.stdout.write("- Auth configuration...")
            try:
                self._check_configuration()
            except Exception as exc:
                failed.append(f"Auth configuration: {exc}")
                self.stdout.write(self.style.ERROR(f"  FAIL {exc}"))
            else:
                passed.append("Auth configuration")
                self.stdout.write(self.style.SUCCESS("  OK"))

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(f"Passed: {len(passed)}")
        self.stdout.write(f"Failed: {len(failed)}")

        if failed:
            self.stdout.write("\nFailures:")
            for failure in failed:
                self.stdout.write(self.style.ERROR(f"  - {failure}"))
            self.stdout.write(self.style.WARNING("\nAuthentication flow checks completed with failures."))
        else:
            self.stdout.write(self.style.SUCCESS("\nAll authentication flow checks passed."))

    def _check_page(self, client, route_name):
        site = SimpleNamespace(name="ASCAI Lazio", domain="ascai.test")
        with patch("allauth.account.views.get_current_site", return_value=site):
            response = client.get(reverse(route_name))
        if response.status_code != 200:
            raise AssertionError(f"returned status {response.status_code}")

    def _check_configuration(self):
        if settings.ACCOUNT_ADAPTER != "apps.accounts.adapters.CustomAccountAdapter":
            raise AssertionError("custom account adapter is not configured")

        required_form_overrides = {
            "add_email": "apps.accounts.forms.CustomAddEmailForm",
            "change_password": "apps.accounts.forms.CustomChangePasswordForm",
            "login": "apps.accounts.forms.CustomLoginForm",
            "reset_password": "apps.accounts.forms.CustomResetPasswordForm",
            "reset_password_from_key": "apps.accounts.forms.CustomResetPasswordKeyForm",
            "set_password": "apps.accounts.forms.CustomSetPasswordForm",
            "signup": "apps.accounts.forms.CustomSignupForm",
        }
        configured_forms = getattr(settings, "ACCOUNT_FORMS", {})
        for key, expected in required_form_overrides.items():
            if configured_forms.get(key) != expected:
                raise AssertionError(f"ACCOUNT_FORMS['{key}'] is not set correctly")

        if settings.ACCOUNT_EMAIL_VERIFICATION != "optional":
            raise AssertionError("ACCOUNT_EMAIL_VERIFICATION should be optional")

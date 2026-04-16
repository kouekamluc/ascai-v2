"""
Canonical auth form customizations for the accounts app.
"""
from allauth.account.forms import (
    AddEmailForm,
    ChangePasswordForm,
    LoginForm,
    ResetPasswordForm,
    ResetPasswordKeyForm,
    SetPasswordForm,
    SignupForm,
)
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User

INPUT_CLASS = (
    "w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-gray-900 "
    "focus:border-cameroon-green focus:ring-2 focus:ring-cameroon-green"
)
SELECT_CLASS = (
    "w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-gray-900 "
    "focus:border-cameroon-green focus:ring-2 focus:ring-cameroon-green"
)


def _update_widget_attrs(field, **attrs):
    if not field:
        return
    field.widget.attrs.update(attrs)


class StyledAuthFormMixin:
    """Apply the shared ASCAI styling to auth-related allauth forms."""

    def style_text_input(self, field_name, *, placeholder=None, autocomplete=None):
        field = self.fields.get(field_name)
        if not field:
            return
        attrs = {"class": INPUT_CLASS}
        if placeholder is not None:
            attrs["placeholder"] = placeholder
        if autocomplete is not None:
            attrs["autocomplete"] = autocomplete
        _update_widget_attrs(field, **attrs)

    def style_password_input(self, field_name, *, placeholder=None, autocomplete=None):
        self.style_text_input(
            field_name,
            placeholder=placeholder,
            autocomplete=autocomplete,
        )

    def style_select(self, field_name):
        field = self.fields.get(field_name)
        if field:
            _update_widget_attrs(field, **{"class": SELECT_CLASS})


class CustomLoginForm(StyledAuthFormMixin, LoginForm):
    """Login form that enforces approval rules and preserves styled widgets."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_text_input(
            "login",
            placeholder=_("Enter your username or email"),
            autocomplete="username",
        )
        _update_widget_attrs(self.fields.get("login"), autofocus=True)
        self.style_password_input(
            "password",
            placeholder=_("Enter your password"),
            autocomplete="current-password",
        )
        if "remember" in self.fields:
            _update_widget_attrs(
                self.fields["remember"],
                **{
                    "class": "w-4 h-4 rounded border-gray-300 text-cameroon-green focus:ring-cameroon-green"
                },
            )

    def clean(self):
        cleaned_data = super().clean()
        login_value = cleaned_data.get("login")
        password = cleaned_data.get("password")

        if not login_value or not password:
            return cleaned_data

        try:
            user = User.objects.get(username=login_value)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=login_value)
            except User.DoesNotExist:
                return cleaned_data

        if user.is_superuser:
            return cleaned_data

        if not user.is_active:
            raise ValidationError(
                _("Your account is inactive. Please contact an administrator.")
            )

        if not user.is_approved:
            raise ValidationError(
                _(
                    "Your account is pending admin approval. Please wait for approval before logging in."
                )
            )

        return cleaned_data


class CustomSignupForm(StyledAuthFormMixin, SignupForm):
    """Signup form with the extra profile fields used on the site."""

    phone = forms.CharField(
        max_length=20,
        required=False,
        label=_("Phone Number"),
    )
    role = forms.ChoiceField(
        choices=[("student", _("Student")), ("mentor", _("Mentor"))],
        initial="student",
        label=_("I am a"),
    )
    language_preference = forms.ChoiceField(
        choices=User.LANGUAGE_CHOICES,
        initial="en",
        label=_("Language Preference"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_text_input(
            "username",
            placeholder=_("Choose a username"),
            autocomplete="username",
        )
        _update_widget_attrs(self.fields.get("username"), autofocus=True)
        self.style_text_input(
            "email",
            placeholder=_("Enter your email"),
            autocomplete="email",
        )
        _update_widget_attrs(self.fields.get("email"), autofocus=True)
        self.style_password_input(
            "password1",
            placeholder=_("Create a password"),
            autocomplete="new-password",
        )
        self.style_password_input(
            "password2",
            placeholder=_("Confirm your password"),
            autocomplete="new-password",
        )
        self.style_text_input(
            "phone",
            placeholder=_("Phone number (optional)"),
            autocomplete="tel",
        )
        self.style_select("role")
        self.style_select("language_preference")


class CustomAddEmailForm(StyledAuthFormMixin, AddEmailForm):
    """Styled add-email form used from the account email management page."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_text_input(
            "email",
            placeholder=_("Enter your email address"),
            autocomplete="email",
        )


class CustomChangePasswordForm(StyledAuthFormMixin, ChangePasswordForm):
    """Styled in-account password change form."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_password_input(
            "oldpassword",
            placeholder=_("Enter your current password"),
            autocomplete="current-password",
        )
        _update_widget_attrs(self.fields.get("oldpassword"), autofocus=True)
        self.style_password_input(
            "password1",
            placeholder=_("Enter your new password"),
            autocomplete="new-password",
        )
        _update_widget_attrs(self.fields.get("password1"), autofocus=True)
        self.style_password_input(
            "password2",
            placeholder=_("Confirm your new password"),
            autocomplete="new-password",
        )


class CustomSetPasswordForm(StyledAuthFormMixin, SetPasswordForm):
    """Styled set-password form used when no current password exists."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_password_input(
            "password1",
            placeholder=_("Enter your new password"),
            autocomplete="new-password",
        )
        _update_widget_attrs(self.fields.get("password1"), autofocus=True)
        self.style_password_input(
            "password2",
            placeholder=_("Confirm your new password"),
            autocomplete="new-password",
        )


class CustomResetPasswordForm(StyledAuthFormMixin, ResetPasswordForm):
    """Styled password reset request form."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_text_input(
            "email",
            placeholder=_("Enter your email"),
            autocomplete="email",
        )


class CustomResetPasswordKeyForm(StyledAuthFormMixin, ResetPasswordKeyForm):
    """Styled password reset completion form."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_password_input(
            "password1",
            placeholder=_("Enter your new password"),
            autocomplete="new-password",
        )
        self.style_password_input(
            "password2",
            placeholder=_("Confirm your new password"),
            autocomplete="new-password",
        )

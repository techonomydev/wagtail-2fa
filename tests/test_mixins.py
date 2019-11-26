from django_otp.middleware import OTPMiddleware as _OTPMiddleware
from django.core.exceptions import PermissionDenied
import pytest
from wagtail_2fa.mixins import OtpRequiredMixin
from django_otp import user_has_device


class TestOtpRequiredMixin:
    def test_handle_no_permission_raises_if_authenticated(self, rf, user):
        request = rf.get('/admin/')
        request.user = user

        mixin = OtpRequiredMixin()

        with pytest.raises(PermissionDenied):
            mixin.handle_no_permission(request)

    def test_handle_no_permission_redirects_to_login_if_not_authenticated(self, rf):
        request = rf.get('/admin/')

        mixin = OtpRequiredMixin()
        response = mixin.handle_no_permission(request)
        assert response.status_code == 302
        assert response.url == '/accounts/login/?next=/admin/'

    def test_user_allowed_with_verified_user_returns_true(self, rf, verified_user):
        user = verified_user

        mixin = OtpRequiredMixin()
        result = mixin.user_allowed(user)
        assert result is True

    def test_user_allowed_when_no_device_and_if_configured_returns_true(self, rf, user):
        request = rf.get('/admin/')
        request.user = user
        middleware = _OTPMiddleware()
        user = middleware._verify_user(request, user)
        assert not user_has_device(user)
        assert user.is_authenticated

        mixin = OtpRequiredMixin()
        mixin.if_configured = True
        result = mixin.user_allowed(user)
        assert result is True

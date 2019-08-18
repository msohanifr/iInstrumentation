from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from .models import Profile


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        profile = Profile.objects.get(user__username=user)
        return (
                six.text_type(user.pk) + six.text_type(timestamp) +
                #six.text_type(user.is_active)
                six.text_type(profile.user_email_verification)
        )


account_activation_token = TokenGenerator()


class SMSTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        profile = Profile.objects.get(user__username=user)
        print('in hash generator:', profile.phone_verification_status)
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(profile.phone_verification_status)
        )


sms_activation_token = SMSTokenGenerator()
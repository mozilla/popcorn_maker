from django.conf import settings
from django.contrib.auth.models import User


if "django_mailer" in settings.INSTALLED_APPS:
    from django_mailer import send_mail
else:
    from django.core.mail import send_mail


def notify_admins(subject, body):
    """Emails the ``superusers``"""
    user_list = User.objects.filter(is_superuser=True)
    recipient_list = [user.email for user in user_list]
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipient_list)

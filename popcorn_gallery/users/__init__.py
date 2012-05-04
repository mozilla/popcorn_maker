from django.contrib.auth.models import User


User._meta.get_field_by_name('email')[0]._unique = True

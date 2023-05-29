from django.contrib.auth.backends import ModelBackend
from .models import WebUser

class WebUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            web_user = WebUser.objects.get(username=username)
        except WebUser.DoesNotExist:
            return None

        if web_user.check_password(password):
            return web_user

        return None

    def get_user(self, user_id):
        try:
            return WebUser.objects.get(pk=user_id)
        except WebUser.DoesNotExist:
            return None

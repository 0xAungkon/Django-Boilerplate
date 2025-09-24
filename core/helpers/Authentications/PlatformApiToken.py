from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from common.models import APITokenModel


class PlatformApiTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):

        token = request.headers.get("X-API-KEY")  # or request.META['HTTP_X_API_KEY']
        request.is_plartform = False
        if not token:
            return None  # Let other authenticators try

        try:
            token_obj = APITokenModel.objects.select_related("user").get(token=token)
        except APITokenModel.DoesNotExist:
            raise AuthenticationFailed("Invalid token")

        if not token_obj.is_valid():
            raise AuthenticationFailed("Token expired or inactive")

        if not token_obj.user.is_active:
            raise AuthenticationFailed("User inactive or deleted")

        request.is_plartform = True

        return (token_obj.user, token_obj)

    def authenticate_header(self, request):
        # Not strictly needed for X-API-KEY, but you can set it
        return "X-API-KEY"

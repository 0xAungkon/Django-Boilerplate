# Import necessary modules
from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from common.models import APITokenModel
from loguru import logger


# Custom middleware to disable CSRF check for all incoming requests
class CsrfExemptMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Disable CSRF check for all incoming requests
        setattr(request, "_dont_enforce_csrf_checks", True)
        return None


# Custom middleware to handle errors and return JSON responses
class HandleErrorsMiddleware(MiddlewareMixin):
    def process_response(self, request, response):

        if settings.DEBUG:
            return response

        # Return the response unchanged if it's successful
        if 200 <= response.status_code < 300 or response.status_code == 302:
            return response
        # Handle 3xx redirects

        try:
            if response.data and isinstance(response.data, dict):
                return response
        except Exception as e:
            logger.info(f"Error processing response data: {e}")

        if isinstance(response, JsonResponse):
            # If it's already a JsonResponse, return it as is
            return response

        error_data = {"detail": ""}

        # Handle 4xx errors (client errors)
        if 400 <= response.status_code < 500:
            if response.status_code == 401:
                error_data["detail"] = "Authentication required"
            if response.status_code == 404:
                error_data["detail"] = "404 Not Found"
            elif response.status_code == 403:
                error_data["detail"] = "Authorization required"
            elif response.status_code == 404:
                error_data["detail"] = "Resource not found"
            elif response.status_code == 429:
                error_data["detail"] = "Too many requests"

        # Handle 5xx errors (server errors)
        elif 500 <= response.status_code < 600:
            error_data["detail"] = "Server error"

        error_data["detail"] = response.reason_phrase
        # Include the original status code and any content

        # Return a JSON response with the error data
        return JsonResponse(error_data, status=response.status_code)


class PlatformTokenAuthMiddleware(MiddlewareMixin):
    "NOT USING"

    def process_request(self, request):
        if request.user.is_authenticated:
            return

        # Check for Authorization header with Bearer token
        auth_header = request.headers.get("X-Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            # request.user = None
            # request.platform_token = None
            return

        token = auth_header[len("Bearer ") :]
        try:
            token_obj = APITokenModel.objects.select_related("user").get(token=token)
        except Exception:
            # request.user = None
            # request.platform_token = None
            return

        if not token_obj.is_valid() or not token_obj.user.is_active:
            # request.user = None
            # request.platform_token = None
            return

        # Attach user and token to request for downstream use
        request.user = token_obj.user
        request.platform_token = token_obj

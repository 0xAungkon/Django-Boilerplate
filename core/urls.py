# Library imports
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from os import getenv
from django.http import JsonResponse

# Configure OpenAPI schema Informations
schema_view = get_schema_view(
    openapi.Info(
        title=getenv("OPENAPI_TITLE", "API"),
        default_version=getenv("OPENAPI_DEFAULT_VERSION", "v1"),
        description=getenv("OPENAPI_DESCRIPTION", "API documentation"),
        terms_of_service=getenv("OPENAPI_TERMS_OF_SERVICE", "https://hros.com/terms/"),
        contact=openapi.Contact(
            email=getenv("OPENAPI_CONTACT_EMAIL", "support@example.com")
        ),
        license=openapi.License(
            name=getenv("OPENAPI_LICENSE_NAME", "License Agreement")
        ),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


# A simple ping view to check if the server is running
def ping(request):
    """
    A simple view to check if the server is running.
    """
    return JsonResponse({"status": "ok"})


# url patterns
urlpatterns = [
    path("", ping, name="ping"),
    path("admin/", admin.site.urls),
    path("api/v1/", include("common.urls")),
]

# swagger UI configuration
if getenv("SWAGGER_UI", "false") == "true":
    urlpatterns += [
        path(
            "api/v1/swagger/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
    ]

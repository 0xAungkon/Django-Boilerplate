from rest_framework.routers import DefaultRouter
from django.urls import path
from common.controllers.Envelop.EnvelopRecipentsController import (
    EnvelopRecipentsViewSet,
)
from common.controllers.Envelop.EnvelopDocumentController import EnvelopDocumentViewSet
from common.controllers.Envelop.EnvelopFieldsController import EnvelopFieldsViewSet
from common.controllers.Envelop.EnvelopValuesController import EnvelopValuesViewSet
from common.controllers.Template.EnvelopTemplateController import (
    EnvelopTemplateRecipentsViewSet,
)
from common.controllers.Template.EnvelopTemplateFieldsController import (
    EnvelopTemplateFieldsViewSet,
)

router = DefaultRouter()

urlpatterns = [
    # Envelop Document URLs
    path(
        "envelop/documents/",
        EnvelopDocumentViewSet.as_view({"get": "list", "post": "create"}),
        name="envelop-document-list",
    ),
    path(
        "envelop/documents/<uuid:pk>/",
        EnvelopDocumentViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="envelop-document-detail",
    ),
    # Envelop Template URLs
    path(
        "envelop/templates/",
        EnvelopTemplateRecipentsViewSet.as_view({"get": "list", "post": "create"}),
        name="envelop-template-list",
    ),
    path(
        "envelop/templates/<uuid:pk>/",
        EnvelopTemplateRecipentsViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="envelop-template-detail",
    ),
    path(
        "envelop/templates/<uuid:pk>/use/",
        EnvelopTemplateRecipentsViewSet.as_view({"get": "use_template"}),
        name="envelop-value-list",
    ),
    # Envelop Template Fields URLs
    path(
        "envelop/template-fields/",
        EnvelopTemplateFieldsViewSet.as_view({"get": "list", "post": "create"}),
        name="envelop-template-field-list",
    ),
    path(
        "envelop/template-fields/<uuid:pk>/",
        EnvelopTemplateFieldsViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="envelop-template-field-detail",
    ),
    # Envelop Recipients URLs
    # path('envelop/', EnvelopRecipentsViewSet.as_view({'get': 'list', 'post': 'create'}), name='envelop-recipient-list'),
    path(
        "envelop/",
        EnvelopRecipentsViewSet.as_view({"get": "list", "post": "create"}),
        name="envelop-recipient-list",
    ),
    # path('envelop/box/<str:box_type>/', EnvelopRecipentsViewSet.as_view({'get': 'list'}), name='envelop-recipient-box'),  # box_type choices: 'inbox', 'sent'
    path(
        "envelop/<uuid:pk>/",
        EnvelopRecipentsViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="envelop-recipient-detail",
    ),
    # path('envelop/inbox', EnvelopRecipentsViewSet.as_view({'get': 'list'}), name='envelop-recipient-inbox-list'),
    # path('envelop/sent', EnvelopRecipentsViewSet.as_view({'get': 'list'}), name='envelop-recipient-sent-list'),
    # Envelop Fields URLs
    path(
        "envelop/fields/",
        EnvelopFieldsViewSet.as_view({"get": "list", "post": "create"}),
        name="envelop-field-list",
    ),
    path(
        "envelop/fields/<uuid:pk>/",
        EnvelopFieldsViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="envelop-field-detail",
    ),
    # Envelop Values URLs
    path(
        "envelop/values/",
        EnvelopValuesViewSet.as_view({"post": "create"}),
        name="envelop-value-list",
    ),
    # path('envelop/values/<uuid:pk>/', EnvelopValuesViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='envelop-value-detail'),
    # Envelop Values URLs
]

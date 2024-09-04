from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from . import views


schema_view = get_schema_view(
    openapi.Info(
        title="Image Processing API",
        default_version='v1',
        description="API for image uploading, resizing, cropping, and transformations",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@imageprocessing.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
   
    path('upload/', views.upload_image),
    path('resize/', views.resize_image),
    path('crop/', views.crop_image),
    path('format/', views.change_format),
    path('all/', views.get_all_images),
    path('<int:image_id>/', views.get_image),
    path('<int:image_id>/delete/', views.delete_image),
    path('<int:image_id>/remove/', views.remove_background),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

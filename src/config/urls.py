from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import generic

from repositories import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # APPS
    path("", generic.TemplateView.as_view(template_name="repositories/compare.html")),
    path("compare/", views.CompareView.as_view(), name="compare_view"),
    path("users/", include("users.urls"), name="users"),
    path("repositories/", include("repositories.urls"), name="repositories"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

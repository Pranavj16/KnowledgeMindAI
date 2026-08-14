from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.views.generic import TemplateView
from dashboard.views import analytics_view, history_view, settings_view
from accounts.views import profile_view

def favicon_view(request):
    return HttpResponse(status=204)

urlpatterns = [
    path("favicon.ico", favicon_view),
    path("favicon.png", favicon_view),
    path("", TemplateView.as_view(template_name="landing/index.html"), name="landing"),
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("analytics/", analytics_view, name="analytics_root"),
    path("history/", history_view, name="history_root"),
    path("profile/", profile_view, name="profile_root"),
    path("settings/", settings_view, name="settings_root"),

    path(
        "chat/",
        include("chat.urls")
    ),
    path("", include("agent.urls")),
    path(
        "knowledge-base/",
        include("knowledge_base.urls")
    ),
]


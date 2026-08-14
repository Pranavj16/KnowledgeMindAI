from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("analytics/", views.analytics_view, name="analytics"),
    path("history/", views.history_view, name="history"),
    path("settings/", views.settings_view, name="settings"),
]

from django.urls import path
from .views import placeholder_view

urlpatterns = [
    path("agents/", placeholder_view, {"title": "Multi-Agent workspace", "eyebrow": "future / orchestration"}, name="agents"),
    path("teams/", placeholder_view, {"title": "Team collaboration", "eyebrow": "future / shared workspaces"}, name="teams"),
    path("playground/", placeholder_view, {"title": "API playground", "eyebrow": "future / developer tools"}, name="playground"),
    path("voice/", placeholder_view, {"title": "Voice assistant", "eyebrow": "future / multimodal"}, name="voice"),
]

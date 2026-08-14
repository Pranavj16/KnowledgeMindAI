from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from knowledge_base.models import Document
from chat.models import Conversation


def _shell(request, template, **context):
    context.setdefault("section", "dashboard")
    context.setdefault("documents", Document.objects.all().order_by("-uploaded_at"))
    return render(request, template, context)


def dashboard_view(request):
    return _shell(request, "app/dashboard.html", section="dashboard", stats={
        "bases": Document.objects.count(),
        "questions": Conversation.objects.count(),
        "chunks": len(request.session.get("chunks", [])),
        "response": "—",
    })


def analytics_view(request):
    return _shell(request, "app/analytics.html", section="analytics")


def history_view(request):
    return _shell(request, "app/history.html", section="history", conversations=Conversation.objects.order_by("-created_at"))


def settings_view(request):
    return _shell(request, "app/settings.html", section="settings")

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from knowledge_base.models import Document
from chat.models import Conversation


def _shell(request, template, **context):
    context.setdefault("section", "dashboard")
    user_docs = Document.objects.filter(user=request.user).order_by("-uploaded_at") if request.user.is_authenticated else Document.objects.none()
    context.setdefault("documents", user_docs)
    return render(request, template, context)


@login_required(login_url="login")
def dashboard_view(request):
    user_docs = Document.objects.filter(user=request.user)
    return _shell(request, "app/dashboard.html", section="dashboard", stats={
        "bases": user_docs.count(),
        "questions": Conversation.objects.count(),
        "chunks": len(request.session.get("chunks", [])),
        "response": "< 1.2s",
    })


@login_required(login_url="login")
def analytics_view(request):
    user_docs = Document.objects.filter(user=request.user)
    user_convs = Conversation.objects.filter(user=request.user)
    return _shell(request, "app/analytics.html", section="analytics", stats={
        "bases": user_docs.count(),
        "questions": user_convs.count(),
        "chunks": len(request.session.get("chunks", [])) or (user_docs.count() * 6),
        "response": "< 850ms",
    }, recent_conversations=user_convs.order_by("-created_at")[:6])


@login_required(login_url="login")
def history_view(request):
    return _shell(request, "app/history.html", section="history", conversations=Conversation.objects.order_by("-created_at"))


@login_required(login_url="login")
def settings_view(request):
    return _shell(request, "app/settings.html", section="settings")

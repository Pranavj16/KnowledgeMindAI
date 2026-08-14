from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation
from knowledge_base.models import Document
from knowledge_base.chroma_service import search_chunks
from agent.llm import ask_llm


@login_required(login_url="login")
def chat_view(request, document_id=None):
    answer = None
    question = ""
    sources = []

    if request.method == "POST":
        question = request.POST.get("question", "").strip()
        if question:
            results = search_chunks(question)
            documents = results.get("documents", [[]])[0] if results else []
            sources = [
                {"chunk_number": index, "text": chunk}
                for index, chunk in enumerate(documents, start=1)
            ]
            if sources:
                answer = ask_llm(question, "\n".join(item["text"] for item in sources))
            else:
                answer = "No relevant information found in the active knowledge base."
        if question:
            Conversation.objects.create(question=question, answer=answer or "")

    document = get_object_or_404(Document, pk=document_id, user=request.user) if document_id else None

    conversations = Conversation.objects.order_by("-created_at")[:8]
    return render(
        request,
        "chat/chat.html",
        {
            "answer": answer,
            "question": question,
            "sources": sources,
            "conversations": conversations,
            "document": document,
            "section": "chat",
        }
    )


@login_required(login_url="login")
def history_view(request):
    return render(request, "app/history.html", {"conversations": Conversation.objects.order_by("-created_at"), "section": "history"})

from django.shortcuts import render, get_object_or_404, redirect
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
    
    all_documents = Document.objects.filter(user=request.user).order_by("-uploaded_at")
    
    # Resolve requested knowledge base (from URL or GET param)
    selected_doc_id = document_id or request.GET.get("kb")
    document = None
    if selected_doc_id and str(selected_doc_id).strip() and str(selected_doc_id).lower() != "all":
        try:
            document = get_object_or_404(Document, pk=selected_doc_id, user=request.user)
        except Exception:
            document = None

    if request.method == "POST":
        question = request.POST.get("question", "").strip()
        post_doc_id = request.POST.get("document_id")
        
        if post_doc_id and str(post_doc_id).strip() and str(post_doc_id).lower() != "all":
            try:
                document = Document.objects.filter(pk=post_doc_id, user=request.user).first()
            except Exception:
                pass
        elif post_doc_id == "all":
            document = None

        if question:
            doc_id_to_search = document.id if document else None
            results = search_chunks(question, document_id=doc_id_to_search, user_id=request.user.id)
            documents = results.get("documents", [[]])[0] if results else []
            sources = [
                {"chunk_number": index, "text": chunk}
                for index, chunk in enumerate(documents, start=1)
            ]
            
            if sources:
                context_str = "\n\n".join(item["text"] for item in sources)
                answer = ask_llm(question, context_str)
            else:
                if document:
                    answer = f"I could not find relevant information in '{document.title}' to answer your question. Try rephrasing or asking across all knowledge bases."
                else:
                    answer = "No relevant information found across your indexed knowledge bases."

            Conversation.objects.create(
                user=request.user,
                document=document,
                question=question,
                answer=answer or ""
            )

    # Scoped history
    if document:
        conversations = Conversation.objects.filter(user=request.user, document=document).order_by("-created_at")[:12]
    else:
        conversations = Conversation.objects.filter(user=request.user).order_by("-created_at")[:12]

    return render(
        request,
        "chat/chat.html",
        {
            "answer": answer,
            "question": question,
            "sources": sources,
            "conversations": conversations,
            "document": document,
            "all_documents": all_documents,
            "section": "chat",
        }
    )


@login_required(login_url="login")
def history_view(request):
    all_documents = Document.objects.filter(user=request.user).order_by("-uploaded_at")
    kb_id = request.GET.get("kb")
    
    query = Conversation.objects.filter(user=request.user)
    selected_document = None
    
    if kb_id and kb_id.strip() and kb_id.lower() != "all":
        try:
            selected_document = Document.objects.filter(pk=kb_id, user=request.user).first()
            if selected_document:
                query = query.filter(document=selected_document)
        except Exception:
            pass

    conversations = query.order_by("-created_at")
    
    return render(
        request,
        "app/history.html",
        {
            "conversations": conversations,
            "all_documents": all_documents,
            "selected_document": selected_document,
            "section": "history"
        }
    )

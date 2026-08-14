from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import DocumentForm
from .models import Document
from .loaders import load_pdf
from .chunking import chunk_text
from .chroma_service import (
    store_chunks,
    get_total_chunks
)


def upload_document(request):
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            
            # Ensure valid user object is attached
            if request.user.is_authenticated:
                document.user = request.user
            else:
                user = User.objects.first()
                if not user:
                    user = User.objects.create_user(username="demo_user", email="demo@example.com")
                document.user = user

            document.save()

            try:
                # Read uploaded file stream or path
                file_obj = document.file
                text = load_pdf(file_obj)
                chunks = chunk_text(text)
                
                if chunks:
                    store_chunks(chunks)
                    request.session["chunks"] = chunks
                    document.processed = True
                    document.save(update_fields=["processed"])
                    messages.success(request, f"Successfully created {len(chunks)} chunks from {document.title}.")
                else:
                    messages.warning(request, f"No text content could be extracted from {document.title}.")
            except Exception as exc:
                print(f"Upload processing error: {exc}")
                messages.error(request, f"Error processing file: {exc}")

            return redirect("upload")
    else:
        form = DocumentForm()

    documents = Document.objects.all().order_by("-uploaded_at")
    chunks = request.session.get("chunks", [])

    return render(
        request,
        "knowledge_base/upload.html",
        {
            "form": form,
            "documents": documents,
            "chunks": chunks,
        },
    )



def knowledge_base_list(request):
    documents = Document.objects.all().order_by("-uploaded_at")
    return render(request, "app/knowledge_bases.html", {"documents": documents, "section": "knowledge_bases"})


def knowledge_base_detail(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    chunks = request.session.get("chunks", [])
    return render(request, "app/kb_detail.html", {"document": document, "chunks": chunks, "section": "knowledge_bases"})


def chunk_explorer(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    chunks = request.session.get("chunks", [])
    return render(request, "app/chunks.html", {"document": document, "chunks": chunks, "section": "knowledge_bases"})


def reprocess_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    if request.method != "POST":
        return redirect("kb_chunks", document_id=document.id)

    try:
        text = load_pdf(document.file.path)
        chunks = chunk_text(text)
        if not chunks:
            raise ValueError("No text chunks were produced from this document.")
        store_chunks(chunks)
        request.session["chunks"] = chunks
        document.processed = True
        document.save(update_fields=["processed"])
        messages.success(request, f"Created {len(chunks)} chunks from {document.title}.")
    except Exception as exc:
        document.processed = False
        document.save(update_fields=["processed"])
        messages.error(request, f"Chunk creation failed: {exc}")

    return redirect("kb_chunks", document_id=document.id)


def delete_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    if request.method == "POST":
        title = document.title
        if document.file:
            document.file.delete(save=False)
        document.delete()
        request.session.pop("chunks", None)
        messages.success(request, f"Removed {title} from your knowledge bases.")
    return redirect("knowledge_bases")

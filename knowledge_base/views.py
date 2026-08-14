from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import DocumentForm
from .models import Document
from .loaders import load_pdf
from .chunking import chunk_text
from .chroma_service import (
    store_chunks,
    get_total_chunks
)


@login_required(login_url="login")
def upload_document(request):
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
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

    documents = Document.objects.filter(user=request.user).order_by("-uploaded_at")
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


@login_required(login_url="login")
def knowledge_base_list(request):
    documents = Document.objects.filter(user=request.user).order_by("-uploaded_at")
    return render(request, "app/knowledge_bases.html", {"documents": documents, "section": "knowledge_bases"})


@login_required(login_url="login")
def knowledge_base_detail(request, document_id):
    document = get_object_or_404(Document, pk=document_id, user=request.user)
    chunks = request.session.get("chunks", [])
    return render(request, "app/kb_detail.html", {"document": document, "chunks": chunks, "section": "knowledge_bases"})


@login_required(login_url="login")
def chunk_explorer(request, document_id):
    document = get_object_or_404(Document, pk=document_id, user=request.user)
    chunks = request.session.get("chunks", [])
    return render(request, "app/chunks.html", {"document": document, "chunks": chunks, "section": "knowledge_bases"})


@login_required(login_url="login")
def reprocess_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id, user=request.user)
    if request.method != "POST":
        return redirect("kb_chunks", document_id=document.id)

    try:
        text = load_pdf(document.file)
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


@login_required(login_url="login")
def delete_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id, user=request.user)
    if request.method == "POST":
        title = document.title
        if document.file:
            try:
                document.file.delete(save=False)
            except Exception:
                pass
        document.delete()
        request.session.pop("chunks", None)
        messages.success(request, f"Removed {title} from your knowledge bases.")
    return redirect("knowledge_bases")

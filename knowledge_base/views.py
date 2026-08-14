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

        form = DocumentForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            # Create document object
            document = form.save(
                commit=False
            )

            # Temporary user assignment
            document.user = User.objects.first()

            # Save uploaded file
            document.save()

            # Extract text from PDF
            text = load_pdf(
                document.file.path
            )

            # Generate chunks
            chunks = chunk_text(
                text
            )
            print("STORING CHUNKS...")

            # Store chunks in ChromaDB
            store_chunks(
                chunks
            )
            print("DONE STORING!")
            print(
                get_total_chunks()
            )
            # Store chunks in session for frontend display
            request.session["chunks"] = chunks

            # Print PDF text
            print("\n")
            print("=" * 50)
            print("PDF TEXT")
            print("=" * 50)
            print(text)

            # Print chunks
            print("\n")
            print("=" * 50)
            print(f"TOTAL CHUNKS: {len(chunks)}")
            print("=" * 50)

            for i, chunk in enumerate(chunks):

                print(f"\nChunk {i + 1}")
                print(chunk)
                print("-" * 50)

            # Print total chunks stored in ChromaDB
            print("\n")
            print("=" * 50)
            print(
                f"TOTAL STORED CHUNKS: "
                f"{get_total_chunks()}"
            )
            print("=" * 50)

            # Mark document as processed
            document.processed = True

            # Save updated document
            document.save()

            # Redirect back to upload page
            return redirect(
                "upload"
            )

    else:

        form = DocumentForm()

    # Fetch all uploaded documents
    documents = Document.objects.all().order_by(
        "-uploaded_at"
    )

    # Get chunks from session
    chunks = request.session.get(
        "chunks",
        []
    )

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

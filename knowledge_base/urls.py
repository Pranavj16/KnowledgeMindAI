from django.urls import path
from . import views
from chat.views import chat_view

urlpatterns = [
    path("", views.knowledge_base_list, name="knowledge_bases"),
    path("upload/", views.upload_document, name="upload"),
    path("<int:document_id>/", views.knowledge_base_detail, name="kb_detail"),
    path("<int:document_id>/chunks/", views.chunk_explorer, name="kb_chunks"),
    path("<int:document_id>/create-chunks/", views.reprocess_document, name="reprocess_document"),
    path("<int:document_id>/delete/", views.delete_document, name="delete_document"),
    path("<int:document_id>/chat/", chat_view, name="kb_chat"),
]

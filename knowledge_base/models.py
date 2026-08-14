from django.db import models
from django.contrib.auth.models import User


class Document(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    file = models.FileField(
        upload_to="uploads/"
    )

    processed = models.BooleanField(
        default=False
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


class DocumentChunk(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="chunks"
    )
    chunk_index = models.PositiveIntegerField(
        default=0
    )
    content = models.TextField()
    embedding = models.JSONField(
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["chunk_index"]

    def __str__(self):
        return f"{self.document.title} - Chunk #{self.chunk_index}"
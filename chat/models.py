from django.db import models
from django.contrib.auth.models import User
from knowledge_base.models import Document


class Conversation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="conversations"
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversations"
    )
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.question[:50]


class ChatHistory(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    question = models.TextField()

    answer = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.question[:50]
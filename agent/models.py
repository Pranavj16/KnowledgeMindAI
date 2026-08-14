from django.db import models


class Agent(models.Model):

    name = models.CharField(
        max_length=100
    )

    model_name = models.CharField(
        max_length=100,
        default="gpt-5"
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.name
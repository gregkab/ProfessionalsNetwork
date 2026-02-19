from django.core.exceptions import ValidationError
from django.db import models


class Professional(models.Model):
    SOURCE_CHOICES = [
        ("direct", "Direct"),
        ("partner", "Partner"),
        ("internal", "Internal"),
    ]

    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, default="")
    job_title = models.CharField(max_length=255, blank=True, default="")
    phone = models.CharField(max_length=20, unique=True, blank=True, null=True)
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.source})"

    def clean(self):
        if not self.email and not self.phone:
            raise ValidationError("At least one of email or phone must be provided.")

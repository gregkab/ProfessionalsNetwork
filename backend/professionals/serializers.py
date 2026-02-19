from rest_framework import serializers

from .models import Professional


class ProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        fields = [
            "id",
            "full_name",
            "email",
            "company_name",
            "job_title",
            "phone",
            "source",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        if not attrs.get("email") and not attrs.get("phone"):
            raise serializers.ValidationError(
                "At least one of email or phone must be provided."
            )
        return attrs


class BulkProfessionalItemSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField(required=False, allow_blank=True, default=None)
    company_name = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    job_title = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    phone = serializers.CharField(
        max_length=20, required=False, allow_blank=True, default=None
    )
    source = serializers.ChoiceField(choices=Professional.SOURCE_CHOICES)

    def validate(self, attrs):
        email = attrs.get("email") or None
        phone = attrs.get("phone") or None
        attrs["email"] = email
        attrs["phone"] = phone
        if not email and not phone:
            raise serializers.ValidationError(
                "At least one of email or phone must be provided."
            )
        return attrs

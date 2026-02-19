from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Professional
from .serializers import BulkProfessionalItemSerializer, ProfessionalSerializer


class ProfessionalListCreateView(generics.ListCreateAPIView):
    serializer_class = ProfessionalSerializer

    def get_queryset(self):
        qs = Professional.objects.all()
        source = self.request.query_params.get("source")
        if source:
            qs = qs.filter(source=source)
        return qs


class BulkCreateView(APIView):
    """
    Accepts {"professionals": [...]}.
    Upserts each entry by email (primary key), falling back to phone.
    Returns per-item results to support partial success.
    """

    def post(self, request):
        items = request.data.get("professionals", [])
        if not isinstance(items, list):
            return Response(
                {"error": "'professionals' must be a list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = []
        for idx, item_data in enumerate(items):
            serializer = BulkProfessionalItemSerializer(data=item_data)
            if not serializer.is_valid():
                results.append(
                    {"index": idx, "status": "error", "errors": serializer.errors}
                )
                continue

            data = serializer.validated_data
            existing = None

            if data.get("email"):
                existing = Professional.objects.filter(email=data["email"]).first()
            if existing is None and data.get("phone"):
                existing = Professional.objects.filter(phone=data["phone"]).first()

            try:
                if existing:
                    for field, value in data.items():
                        setattr(existing, field, value)
                    existing.full_clean()
                    existing.save()
                    results.append(
                        {
                            "index": idx,
                            "status": "updated",
                            "professional": ProfessionalSerializer(existing).data,
                        }
                    )
                else:
                    prof = Professional(**data)
                    prof.full_clean()
                    prof.save()
                    results.append(
                        {
                            "index": idx,
                            "status": "created",
                            "professional": ProfessionalSerializer(prof).data,
                        }
                    )
            except Exception as e:
                results.append({"index": idx, "status": "error", "errors": str(e)})

        return Response({"results": results}, status=status.HTTP_200_OK)

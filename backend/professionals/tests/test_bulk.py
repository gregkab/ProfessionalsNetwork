from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from professionals.models import Professional


class BulkEndpointTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/professionals/bulk/"

    def test_bulk_create(self):
        payload = [
            {"full_name": "One", "email": "one@test.com", "source": "direct"},
            {"full_name": "Two", "phone": "555-0002", "source": "partner"},
        ]
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 2)
        self.assertEqual(res.data["results"][0]["status"], "created")
        self.assertEqual(res.data["results"][1]["status"], "created")
        self.assertEqual(Professional.objects.count(), 2)

    def test_bulk_upsert_by_email(self):
        Professional.objects.create(
            full_name="Original", email="up@test.com", job_title="Junior", source="direct"
        )
        payload = [
            {
                "full_name": "Updated",
                "email": "up@test.com",
                "job_title": "Senior",
                "source": "partner",
            },
        ]
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.data["results"][0]["status"], "updated")
        self.assertEqual(res.data["results"][0]["professional"]["job_title"], "Senior")
        self.assertEqual(Professional.objects.count(), 1)

    def test_bulk_upsert_by_phone_fallback(self):
        Professional.objects.create(
            full_name="Phone User", phone="555-0010", source="direct"
        )
        payload = [
            {
                "full_name": "Phone Updated",
                "phone": "555-0010",
                "source": "internal",
            },
        ]
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.data["results"][0]["status"], "updated")
        self.assertEqual(Professional.objects.count(), 1)

    def test_bulk_partial_success(self):
        payload = [
            {"full_name": "Good", "email": "good@test.com", "source": "direct"},
            {"full_name": "Bad", "source": "invalid"},
            {"full_name": "Also Good", "phone": "555-0003", "source": "internal"},
        ]
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data["results"]
        self.assertEqual(results[0]["status"], "created")
        self.assertEqual(results[1]["status"], "error")
        self.assertEqual(results[2]["status"], "created")
        self.assertEqual(Professional.objects.count(), 2)

    def test_bulk_rejects_non_list(self):
        res = self.client.post(self.url, {"not": "a list"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bulk_empty_list(self):
        res = self.client.post(self.url, [], format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 0)

    def test_bulk_upsert_email_takes_priority_over_phone(self):
        """When both email and phone match is possible, email match wins."""
        Professional.objects.create(
            full_name="Email Match", email="match@test.com", phone="555-0020",
            source="direct"
        )
        Professional.objects.create(
            full_name="Phone Match", phone="555-0030", source="direct"
        )
        payload = [
            {
                "full_name": "Should Update Email Match",
                "email": "match@test.com",
                "source": "partner",
            },
        ]
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.data["results"][0]["status"], "updated")
        updated = res.data["results"][0]["professional"]
        self.assertEqual(updated["email"], "match@test.com")
        self.assertEqual(updated["full_name"], "Should Update Email Match")
        self.assertEqual(Professional.objects.count(), 2)

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from .models import Professional


class ProfessionalModelTest(TestCase):
    def test_str_representation(self):
        p = Professional.objects.create(
            full_name="Jane Doe", email="jane@test.com", source="direct"
        )
        self.assertEqual(str(p), "Jane Doe (direct)")

    def test_requires_email_or_phone(self):
        from django.core.exceptions import ValidationError

        p = Professional(full_name="No Contact", source="direct")
        with self.assertRaises(ValidationError):
            p.full_clean()


class SingleCreateEndpointTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/professionals/"

    def test_create_professional(self):
        payload = {
            "full_name": "Alice Chen",
            "email": "alice@example.com",
            "phone": "555-0001",
            "job_title": "Engineer",
            "company_name": "Acme",
            "source": "direct",
        }
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["full_name"], "Alice Chen")
        self.assertEqual(res.data["source"], "direct")
        self.assertIn("id", res.data)
        self.assertIn("created_at", res.data)

    def test_duplicate_email_rejected(self):
        Professional.objects.create(
            full_name="Existing", email="dup@example.com", source="direct"
        )
        payload = {
            "full_name": "New",
            "email": "dup@example.com",
            "phone": "555-9999",
            "source": "direct",
        }
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", res.data)

    def test_duplicate_phone_rejected(self):
        Professional.objects.create(
            full_name="Existing", phone="555-0001", source="direct"
        )
        payload = {"full_name": "New", "phone": "555-0001", "source": "partner"}
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone", res.data)

    def test_invalid_source_rejected(self):
        payload = {
            "full_name": "Bad Source",
            "email": "bad@example.com",
            "source": "unknown",
        }
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("source", res.data)

    def test_requires_email_or_phone(self):
        payload = {"full_name": "No Contact", "source": "direct"}
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class ListEndpointTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/professionals/"
        Professional.objects.create(
            full_name="A", email="a@test.com", source="direct"
        )
        Professional.objects.create(
            full_name="B", email="b@test.com", source="partner"
        )
        Professional.objects.create(
            full_name="C", email="c@test.com", source="partner"
        )

    def test_list_all(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 3)

    def test_filter_by_source(self):
        res = self.client.get(self.url, {"source": "partner"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertTrue(all(p["source"] == "partner" for p in res.data))

    def test_filter_returns_empty_for_no_match(self):
        res = self.client.get(self.url, {"source": "internal"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)


class BulkEndpointTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/professionals/bulk"

    def test_bulk_create(self):
        payload = {
            "professionals": [
                {"full_name": "One", "email": "one@test.com", "source": "direct"},
                {"full_name": "Two", "phone": "555-0002", "source": "partner"},
            ]
        }
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
        payload = {
            "professionals": [
                {
                    "full_name": "Updated",
                    "email": "up@test.com",
                    "job_title": "Senior",
                    "source": "partner",
                },
            ]
        }
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.data["results"][0]["status"], "updated")
        self.assertEqual(res.data["results"][0]["professional"]["job_title"], "Senior")
        self.assertEqual(Professional.objects.count(), 1)

    def test_bulk_upsert_by_phone_fallback(self):
        Professional.objects.create(
            full_name="Phone User", phone="555-0010", source="direct"
        )
        payload = {
            "professionals": [
                {
                    "full_name": "Phone Updated",
                    "phone": "555-0010",
                    "source": "internal",
                },
            ]
        }
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.data["results"][0]["status"], "updated")
        self.assertEqual(Professional.objects.count(), 1)

    def test_bulk_partial_success(self):
        payload = {
            "professionals": [
                {"full_name": "Good", "email": "good@test.com", "source": "direct"},
                {"full_name": "Bad", "source": "invalid"},
                {"full_name": "Also Good", "phone": "555-0003", "source": "internal"},
            ]
        }
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data["results"]
        self.assertEqual(results[0]["status"], "created")
        self.assertEqual(results[1]["status"], "error")
        self.assertEqual(results[2]["status"], "created")
        self.assertEqual(Professional.objects.count(), 2)

    def test_bulk_rejects_non_list(self):
        res = self.client.post(
            self.url, {"professionals": "not a list"}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

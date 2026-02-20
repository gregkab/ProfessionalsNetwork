from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from professionals.models import Professional


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

    def test_create_with_email_only(self):
        payload = {
            "full_name": "Email Only",
            "email": "emailonly@example.com",
            "source": "partner",
        }
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_with_phone_only(self):
        payload = {
            "full_name": "Phone Only",
            "phone": "555-1234",
            "source": "internal",
        }
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

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

    def test_missing_full_name_rejected(self):
        payload = {"email": "noname@example.com", "source": "direct"}
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("full_name", res.data)

    def test_missing_source_rejected(self):
        payload = {"full_name": "No Source", "email": "nosrc@example.com"}
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("source", res.data)

    def test_empty_email_does_not_violate_unique(self):
        """Multiple submissions with blank email should not cause IntegrityError."""
        payload_a = {
            "full_name": "Person A",
            "email": "",
            "phone": "555-8001",
            "source": "direct",
        }
        payload_b = {
            "full_name": "Person B",
            "email": "",
            "phone": "555-8002",
            "source": "direct",
        }
        res_a = self.client.post(self.url, payload_a, format="json")
        res_b = self.client.post(self.url, payload_b, format="json")
        self.assertEqual(res_a.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_b.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(res_a.data["email"])
        self.assertIsNone(res_b.data["email"])

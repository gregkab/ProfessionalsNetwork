from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from professionals.models import Professional


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

    def test_response_contains_all_fields(self):
        res = self.client.get(self.url)
        entry = res.data[0]
        for field in ["id", "full_name", "email", "phone", "job_title",
                       "company_name", "source", "created_at"]:
            self.assertIn(field, entry)

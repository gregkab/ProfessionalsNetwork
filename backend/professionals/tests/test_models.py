from django.core.exceptions import ValidationError
from django.test import TestCase

from professionals.models import Professional


class ProfessionalModelTest(TestCase):
    def test_str_representation(self):
        p = Professional.objects.create(
            full_name="Jane Doe", email="jane@test.com", source="direct"
        )
        self.assertEqual(str(p), "Jane Doe (direct)")

    def test_requires_email_or_phone(self):
        p = Professional(full_name="No Contact", source="direct")
        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_ordering_is_newest_first(self):
        a = Professional.objects.create(
            full_name="First", email="first@test.com", source="direct"
        )
        b = Professional.objects.create(
            full_name="Second", email="second@test.com", source="direct"
        )
        professionals = list(Professional.objects.all())
        self.assertEqual(professionals[0].pk, b.pk)
        self.assertEqual(professionals[1].pk, a.pk)

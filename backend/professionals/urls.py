from django.urls import path

from . import views

urlpatterns = [
    path("professionals/", views.ProfessionalListCreateView.as_view(), name="professional-list-create"),
    path("professionals/bulk/", views.BulkCreateView.as_view(), name="professional-bulk"),
]

from django.urls import path
from .views.views import InstitutionListView, InstitutionDetailView

urlpatterns = [
    path(
        "institutions/", InstitutionListView.as_view(), name="institution_list_create"
    ),
    path(
        "institutions/<uuid:id>/",
        InstitutionDetailView.as_view(),
        name="institution_detail_update_delete",
    ),
]

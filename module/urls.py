from django.urls import path
from module.views import ModuleDetailView, ModuleListView, ModuleContentsView

urlpatterns = [
    path("module/", ModuleListView.as_view(), name="module_list"),
    path(
        "module/<uuid:id>/",
        ModuleDetailView.as_view(),
        name="module_detail",
    ),
    path(
        "module/<uuid:id>/contents/",
        ModuleContentsView.as_view(),
        name="module_contents",
    ),
]

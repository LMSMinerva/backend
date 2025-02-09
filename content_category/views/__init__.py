"""
init module for ContentsCategory views
"""

from content_category.views.content_category import (
    ContentCategoryListView,
    ContentCategoryDetailView,
)

__all__ = [
    "ContentCategoryListView",
    "ContentCategoryDetailView",
]

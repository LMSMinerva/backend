"""
init module for courses views
"""

from courses.views.courses import (
    CourseView,
    CourseDetailViewById,
    CourseDetailViewBySlug,
)

__all__ = ["CourseView", "CourseDetailViewById", "CourseDetailViewBySlug"]

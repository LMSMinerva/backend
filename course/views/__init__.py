"""
init module for courses views
"""

from course.views.course import (
    CourseView,
    CourseDetailViewById,
    CourseDetailViewBySlug,
)

__all__ = ["CourseView", "CourseDetailViewById", "CourseDetailViewBySlug"]

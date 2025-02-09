"""
init module for courses views
"""

from course.views.course import (
    CourseView,
    CourseDetailViewById,
    CourseDetailViewBySlug,
    CourseModulesView,
)

__all__ = [
    "CourseView",
    "CourseDetailViewById",
    "CourseDetailViewBySlug",
    "CourseModulesView",
]

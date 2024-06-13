from django.urls import path
from django.urls import include
from .views import (
    CoursesHomeViewSet,  
    CourseSearchViewSet, 
    CourseDetailView, 
    CourseStudyViewSet, 
    CourseManageViewSet, 
    GetCartDetailView, 
    SearchCourseViewSet, 
    AddCommentViewSet
)
from rest_framework.routers import DefaultRouter


app_name = 'courses'

router = DefaultRouter()
router.register(r'courses_home', CoursesHomeViewSet, basename='courses_home')
router.register(r'course_search', CourseSearchViewSet, basename='course_search')
router.register(r'course_detail', CourseDetailView, basename='course_detail')
router.register(r'course_study', CourseStudyViewSet, basename='course_study')
router.register(r'course_manage_course_list', CourseManageViewSet, basename='course_manage_course_list')
router.register(r'course_manage', CourseManageViewSet, basename='course_manage')
router.register(r'get_cart_detail', GetCartDetailView, basename='get_cart_detail')
router.register(r'search_course', SearchCourseViewSet, basename='search_course')
router.register(r'add_comment', AddCommentViewSet, basename='add_comment')

urlpatterns = [
    path('', include(router.urls)),
]

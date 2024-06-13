from django.core.exceptions import ValidationError
from django.db.models.query_utils import Q
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Course, Sector
from .serializers import (CartItemSerializer, CommentSerializer, CourseDisplaySerializer,
                          CourseListSerializer, CoursePaidSerializer, CourseUnPaidSerializer,
                          )
from decimal import Decimal
import json


class CoursesHomeViewSet(viewsets.ViewSet):
    def list(self, request):
        sectors = Sector.objects.order_by('?')[:6]
        sector_response = []

        for sector in sectors:
            sector_courses = sector.related_courses.order_by('?')[:4]
            courses_serializer = CourseDisplaySerializer(sector_courses, many=True)
            sector_obj = {
                "sector_name": sector.name,
                "sector_uuid": sector.sector_uuid,
                "featured_courses": courses_serializer.data,
                "sector_image": sector.sector_image.url
            }
            sector_response.append(sector_obj)

        return Response(data=sector_response, status=status.HTTP_200_OK)


class CourseSearchViewSet(viewsets.ViewSet):
    def list(self, request):
        sector_uuid = request.query_params.get('sector_uuid')
        sector = Sector.objects.filter(sector_uuid=sector_uuid).first()

        if not sector:
            return HttpResponseBadRequest("Course sector does not exist")

        sector_courses = sector.related_courses.all()
        serializer = CourseListSerializer(sector_courses, many=True)

        total_students = sum(course.get_enrolled_students() for course in sector_courses)

        return Response({'data': serializer.data,
                         'sector_name': sector.name,
                         'total_students': total_students,
                         'image': sector.sector_image.url},
                        status=status.HTTP_200_OK)


class CourseDetailView(viewsets.ViewSet):
    def retrieve(self, request, course_uuid):
        try:
            course = Course.objects.get(course_uuid=course_uuid)
        except Course.DoesNotExist:
            return HttpResponseBadRequest('Course does not exist')

        serializer = CourseUnPaidSerializer(course)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseStudyViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, course_uuid):
        course = Course.objects.filter(course_uuid=course_uuid).first()

        if not course:
            return HttpResponseBadRequest('Course does not exist')

        if not request.user.paid_course.filter(course_uuid=course_uuid).exists():
            return HttpResponseNotAllowed("User has not purchased this course")

        serializer = CoursePaidSerializer(course)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseManageViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CoursePaidSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Course.objects.filter(author=self.request.user)


class GetCartDetailView(viewsets.ViewSet):
    def create(self, request):
        try:
            body = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return HttpResponseBadRequest()

        if not isinstance(body.get('cart'), list):
            return HttpResponseBadRequest()

        cart_uuids = body.get("cart")
        if not cart_uuids:
            return Response(data=[])

        courses = Course.objects.filter(course_uuid__in=cart_uuids)
        serializer = CartItemSerializer(courses, many=True)

        cart_cost = sum(Decimal(item.price) for item in serializer.data)

        return Response(data={"cart_detail": serializer.data, "cart_total": str(cart_cost)},
                        status=status.HTTP_200_OK)


class SearchCourseViewSet(viewsets.ViewSet):
    def list(self, request):
        search_term = request.query_params.get('search_term')
        matches = Course.objects.filter(Q(title__icontains=search_term) | Q(description__icontains=search_term))
        serializer = CourseListSerializer(matches, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class AddCommentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, course_uuid):
        try:
            course = Course.objects.get(course_uuid=course_uuid)
        except Course.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        content = json.loads(request.body)

        if not content.get('message'):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = CommentSerializer(data=content)

        if serializer.is_valid():
            comment = serializer.save(user=request.user)
            course.comment.add(comment)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

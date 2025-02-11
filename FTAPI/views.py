from django.shortcuts import render  # type: ignore
from django.urls import resolve
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

from .models import File
from .serializers import FileSerializer
from .mixins import FileHandlerMixin
from .utils import *
from home.settings import USER_FILES_ENDPOINT

from urllib.parse import urljoin


# Create your views here.
class ListCreateFilesView(GenericAPIView, FileHandlerMixin):
    pagination_class = PageNumberPagination
    pagination_class.page_size = 250

    @extend_schema(
        summary="List all uploaded files",
        description=(
            "This endpoint retrieves a list of all files stored in the database. "
            "Each file includes metadata such as the filename, suffix, size, and URL, "
            "but excludes the actual file content."
        ),
        responses={
            200: OpenApiResponse(
                response=FileSerializer,
                description="Success response",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={
                            "data": [
                                {
                                    "id": 1,
                                    "filename": "example",
                                    "suffix": ".txt",
                                    "size": 1024,
                                    "url": "http://localhost:8000/files/1/",
                                    "uploaded_date": "2025-01-06",
                                    "uploaded_time": "10:30:45"
                                },
                                {
                                    "id": 2,
                                    "filename": "photo",
                                    "suffix": ".jpg",
                                    "size": 2048,
                                    "url": "http://localhost:8000/files/2/",
                                    "uploaded_date": "2025-01-06",
                                    "uploaded_time": "11:45:00"
                                }
                            ]
                        },
                    ),
                ]
            ),
            500: OpenApiResponse(
                response=FileSerializer,
                description="Internal server error",
                examples=[OpenApiExample(
                    "Internal Server Error",
                    value=None,
                    response_only=True,
                    status_codes=["500"],
                )]
            ),
        },
    )
    @method_decorator(cache_page(60))
    def get(self, request: Request) -> Response:
        try: file_qs = File.objects.all()
        except: 
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        page = self.paginate_queryset(file_qs)
        to_serialize_data = file_qs if page is None else page

        files_serialized = FileSerializer(to_serialize_data, many=True)
        files_data = files_serialized.data

        for file in files_data:
            file.pop("file")

        response = Response(data=files_data) if page is None else self.get_paginated_response(files_data)
        response.headers["cache-control"] = "no-store"

        return response

    @extend_schema(
        summary="Create a new file record.",
        description="""This endpoint allows you to create a new file record. 
        It accepts a JSON request containing the `filename`, `suffix`, and `file_hex` fields. 
        The file is converted from hex data, stored in the database, and relevant metadata is returned.""",
        request=FileSerializer,
        responses={
            201: OpenApiResponse(
                response=FileSerializer,
                description="File created successfully. Returns file details except for the file content.",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={
                            "id": 1,
                            "filename": "example",
                            "suffix": "txt",
                            "size": 12345,
                            "url": "http://example.com/files/1/",
                            "uploaded_date": "2025-01-01",
                            "uploaded_time": "12:34:56",
                        },
                    )
                ],
            ),
            400: OpenApiResponse(
                response=FileSerializer,
                description="Bad request errors that can occur.",
                examples=[
                    OpenApiExample(
                        "data not valid error.",
                        value={"Error": "Data isn't valid."}
                    ),
                    OpenApiExample(
                        "Failed extracting file_hex field.",
                        value={"Error": "Failed while extracting file_hex field from request body with error {e}."},
                    ),
                ]
            ),
        },
        examples=[
            OpenApiExample(
                "Request Example",
                value={
                    "filename": "example",
                    "suffix": "txt",
                    "file_hex": "AA BD 42",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request: Request) -> Response:
        try:
            file_hex = request.data.pop("file_hex")
        except Exception as e:
            err = {"Error": f"Failed while extracting file_hex field from request body with error {e}."}

            return Response(
                data=err,
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = request.data

        file_obj = self.hex_to_django_file_obj(file_hex, data["filename"])
        size = file_obj.size
        data["file"] = file_obj
        data["size"] = size

        file_srlzd = FileSerializer(data=data)

        try: file_srlzd.is_valid(raise_exception=True)
        except:
            err = {"Error": f"Data isn't valid."}

            return Response(
                data=err,
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        file_model = file_srlzd.save()
        
        file_url = urljoin(get_base_url(request), USER_FILES_ENDPOINT)
        file_url = urljoin(file_url,  str(file_model.id))
        file_model.url = file_url
        file_model.save()

        file_data = FileSerializer(file_model).data
        file_data.pop("file")

        return Response(data=file_data)
    
class DetailDelFilesView(APIView, FileHandlerMixin):
    @extend_schema(
        summary="Retrieve a single file record.",
        description="""
        Retrive a single file record from database, 
        including all fields from list files view and 
        file content as hexadecimal string.
        """,
        responses={
            200: OpenApiResponse(
                response=FileSerializer,
                description="Success full response.",
                examples=[
                    OpenApiExample(
                        name="Normal example",
                        value={
                            "id": 1,
                            "filename": "example",
                            "suffix": "txt",
                            "size": 12345,
                            "url": "http://example.com/files/1/",
                            "uploaded_date": "2025-01-01",
                            "uploaded_time": "12:34:56",
                            "file_hex": "41 4a 4c 45",
                        },
                    )
                ],
            ),
            404: OpenApiResponse(
                response=FileSerializer,
                description="File not found",
                examples=[
                    OpenApiExample(
                        name="File not found",
                        value={"Error": "File with specified id {file_id} couldn't be found to be returned."},
                    )
                ]
            )
        }
    )
    def get(self, request: Request, file_id: int) -> Response:
        # Getting from cache if exists
        url_obj = resolve(request.path_info)
        key = key = get_unique_resource_key(url_obj.route, str(file_id))

        if cache.has_key(key):
            return Response(data=cache.get(key))
        
        try:
            file = File.objects.get(id=file_id)
        except:
            error = {"error": f"File with specified id {file_id} couldn't be found to be returned."}

            return Response(data=error, status=status.HTTP_404_NOT_FOUND)

        file_data = FileSerializer(file).data
        file_data.pop("file")
        file_hex = self.fieldfile_to_hex(file.file)
        file_data["file_hex"] = file_hex
        
        cache.set(key, file_data, 60)

        response = Response(data=file_data)

        return response

    @extend_schema(
        summary="Delete a file record.",
        description="""
        Delete a file record from database given a file_id. Return 404 error if file 
        record couldn't be found.
        """,
        responses={
            200: OpenApiResponse(
                description="Deletion successfully, nothing returned.",
                response=None,
            ),
            404: OpenApiResponse(
                response=FileSerializer,
                description="File record could not be found to deletion.",
                examples=[OpenApiExample(
                    "Record not found",
                    value={"Error": "File with specified id {file_id} couldn't be found to delete."},
                )]
            )
        }
    )
    def delete(self, request: Request, file_id: int) -> Response:
        try:
            file = File.objects.get(id=file_id)
        except:
            error = {"error": f"File with specified id {file_id} couldn't be found to delete."}

            return Response(data=error, status=status.HTTP_404_NOT_FOUND)
        
        # deleting from DB and fs
        file.delete()
        file.file.delete(save=False)

        # deleting from cache
        url_obj = resolve(request.path_info)
        key = get_unique_resource_key(url_obj.route, str(file_id))
        cache.delete(key)

        response = Response(status=status.HTTP_200_OK)

        return response

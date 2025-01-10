from django.shortcuts import render  # type: ignore
from django.urls import resolve
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

from .models import File
from .serializers import FileSerializer
from .mixins import FileHandlerMixin
from .utils import *
from home.settings import USER_FILES_ENDPOINT

from urllib.parse import urljoin


# TODO: Modularizar as views em funções ou métodos
# TODO: Criar a documentação da API

# Create your views here.
class ListCreateFilesView(APIView, FileHandlerMixin):

    @method_decorator(cache_page(60))
    def get(self, request: Request) -> Response:
        try: file_qs = File.objects.all()
        except: 
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        files_serialized = FileSerializer(file_qs, many=True)

        files_data = files_serialized.data

        for file in files_data:
            file.pop("file")

        response = Response(data=files_data)
        response.headers["cache-control"] = "no-store"

        return response


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
    def get(self, request: Request, file_id: int) -> Response:
        # Getting from cache if exists
        url_obj = resolve(request.path_info)
        key = url_obj.route + "_" + str(file_id)

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
        key = url_obj.route + "_" + str(file_id)
        cache.delete(key)

        response = Response(status=status.HTTP_200_OK)

        return response

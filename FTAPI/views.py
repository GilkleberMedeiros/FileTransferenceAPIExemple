from django.shortcuts import render  # type: ignore
from django.urls import resolve
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.renderers import JSONRenderer

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
        file_qs = File.objects.all()
        files_serialized = FileSerializer(file_qs, many=True)
        exclude_fields = ["file"]

        files_data = files_serialized.data

        for file in files_data:
            for field in exclude_fields:
                file.pop(field)

        json_response = JSONRenderer().render(files_data)
        response = Response(data=json_response)
        response.headers["cache-control"] = "no-store"

        return response


    def post(self, request: Request) -> Response:
        try:
            file_hex = request.data.pop("file_hex")
        except Exception as e:
            err = {"Error": f"Failed while extracting file_hex field from request body with error {e}."}
            json_err = JSONRenderer().render(err)

            return Response(
                data=json_err,
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
            json_err = JSONRenderer().render(err)

            return Response(
                data=json_err,
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        file_model = file_srlzd.save()
        
        file_url = urljoin(get_base_url(request), USER_FILES_ENDPOINT)
        file_url = urljoin(file_url,  str(file_model.id))
        file_model.url = file_url
        file_model.save()

        file_data = FileSerializer(file_model).data
        file_data.pop("file")

        json_response = JSONRenderer().render(data=file_data)

        return Response(data=json_response)
    
class DetailDelFilesView(APIView, FileHandlerMixin):
    def get(self, request: Request, file_id: int) -> Response:
        json_renderer = JSONRenderer()

        # Getting from cache if exists
        url_obj = resolve(request.path_info)
        key = url_obj.route + "_" + str(file_id)

        if cache.has_key(key):
            json_response = json_renderer.render(data=cache.get(key))

            return Response(data=json_response)
        
        try:
            file = File.objects.get(id=file_id)
        except:
            error = {"error": f"File with specified id {file_id} couldn't be found to be returned."}
            error = json_renderer.render(error)

            return Response(data=error, status=status.HTTP_404_NOT_FOUND)

        file_data = FileSerializer(file).data
        file_data.pop("file")
        file_bytes = file.file.file.read()
        file_hex = file_bytes.hex(sep=" ", bytes_per_sep=2)
        file_data["file_hex"] = file_hex
        
        cache.set(key, file_data, 60)

        json_response = json_renderer.render(file_data)
        response = Response(data=json_response)

        return response

    def delete(self, request: Request, file_id: int) -> Response:
        try:
            file = File.objects.get(id=file_id)
        except:
            error = {"error": f"File with specified id {file_id} couldn't be found to delete."}
            error = JSONRenderer().render(error)

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

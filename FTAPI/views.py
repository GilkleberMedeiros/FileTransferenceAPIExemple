from django.shortcuts import render  # type: ignore
from django.http.request import HttpRequest
from django.core.files.uploadedfile import UploadedFile

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.renderers import JSONRenderer

from .models import File
from .serializers import FileSerializer
from home.settings import USER_FILES_ENDPOINT

import io
from urllib.parse import urljoin

# Create your views here.
class ListCreateDelFilesView(APIView):
    def post(self, request: Request) -> Response:
        protocol = "https" if request.is_secure() else "http"
        host = request.get_host()

        try:
            file_hex = request.data.pop("file_hex")
        except Exception as e:
            return Response(
                data=f"Error: {e}",
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = request.data

        file_bytes = bytes.fromhex(file_hex)
        file_obj = io.BytesIO(file_bytes)
        file_obj = UploadedFile(file_obj, name=data["filename"], size=len(file_obj.getvalue()))
        size = file_obj.size
        data["file"] = file_obj
        data["size"] = size

        file_srlzd = FileSerializer(data=data)

        try: file_srlzd.is_valid(raise_exception=True)
        except Exception as e:
            return Response(
                data=f"Error: {e}",
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        file_model = file_srlzd.save()
        
        file_url = urljoin(f"{protocol}://{host}", USER_FILES_ENDPOINT)
        file_url = urljoin(file_url,  str(file_model.id))
        file_model.url = file_url
        file_model.save()

        file_data = FileSerializer(file_model).data
        file_data.pop("file")

        json_response = JSONRenderer().render(data=file_data)

        return Response(data=json_response)

from django.core.files.uploadedfile import UploadedFile

import io
from typing import TypeVar


DjangoFieldFile = TypeVar("DjangoFieldFile")

class FileHandlerMixin():

    @staticmethod
    def hex_to_file_obj(file_hex: str) -> io.BytesIO:
        """
        Receive hexadecimal string representing file bytes content 
        and return a file object io.BytesIO.
        """
        file_bytes = bytes.fromhex(file_hex)
        return io.BytesIO(file_bytes)

    @staticmethod
    def hex_to_django_file_obj(file_hex: str, filename: str) -> UploadedFile:
        """
        Receive file bytes in hexadecimal, filename and 
        return an UploadedFile django object.
        """
        file_obj = FileHandlerMixin.hex_to_file_obj(file_hex)

        return UploadedFile(file_obj, name=filename, size=len(file_obj.getvalue()))
    
    @staticmethod
    def fieldfile_to_hex(
            field_file: DjangoFieldFile, 
            chunk_size: int = -1, 
            sep: str = " ", 
            bytes_per_sep: int = 1
        ) -> str:
        """
        Receive a django FieldFile and return file bytes content 
        as hexadecimal string.
        """
        file_bytes = field_file.file.read(chunk_size)

        return file_bytes.hex(sep=sep, bytes_per_sep=bytes_per_sep)
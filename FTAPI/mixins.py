from django.core.files.uploadedfile import UploadedFile
from django.db.models import FieldFile

import io


class FileHandlerMixin():

    @staticmethod
    def hex_to_file_obj(file_hex: str) -> io.BytesIO:
        """
        Receive hexadecimal string representing file bytes content 
        and return a file object io.BytesIO.
        """
        file_bytes = bytes.fromhex(file_hex)
        file_obj = io.BytesIO(file_bytes)

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
            field_file: FieldFile, 
            chunk_size: int = -1, 
            sep: str = " ", 
            bytes_per_sep: int = 2
        ) -> str:
        file_bytes = field_file.file.read(chunk_size)
        return file_bytes.hex(sep=sep, bytes_per_sep=bytes_per_sep)
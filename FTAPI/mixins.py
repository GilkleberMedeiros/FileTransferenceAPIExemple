from django.core.files.uploadedfile import UploadedFile

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
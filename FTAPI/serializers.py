from rest_framework import serializers
from .models import File



class FileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    filename = serializers.CharField(
        max_length=250,
    )
    suffix =serializers.CharField(
        max_length=15,
    )
    file = serializers.FileField(
        max_length=250,
    )
    size = serializers.IntegerField()
    url = serializers.URLField(
        required=False,
    )
    uploaded_date =serializers.DateField(
        read_only=True,
        required=False,
    )
    uploaded_time = serializers.TimeField(
        read_only=True,
        required=False,
    )

    def create(self, validated_data: dict[str, any]) -> File:
        return File.objects.create(**validated_data)
    
    def update(self, instance: File, validated_data: dict[str, any]) -> File:
        instance.filename = validated_data.get('filename', instance.filename)
        instance.suffix = validated_data.get('suffix', instance.suffix)
        instance.file = validated_data.get('file', instance.file)
        instance.size = validated_data.get('size', instance.size)
        instance.url = validated_data.get('url', instance.url)
        instance.save()

        return instance
    


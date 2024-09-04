from rest_framework import serializers
from .models import image

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = image
        fields = ['id', 'image']
class ImageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = image
        fields = ['id', 'user', 'image', 'url', 'format', 'size']
        
        
        
class resizeserializer(serializers.Serializer):
    image_id = serializers.IntegerField()
    height = serializers.IntegerField()
    width=serializers.IntegerField()
   
class cropserializer(serializers.Serializer):
    image_id = serializers.IntegerField()
    box=serializers.CharField()
      
      
class formatchange(serializers.Serializer):
    image_id = serializers.IntegerField()
    format=serializers.CharField()
                
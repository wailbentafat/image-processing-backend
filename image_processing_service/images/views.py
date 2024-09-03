from django.core.files.storage import default_storage
from django.http import HttpResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from PIL import Image as PilImage
import io
from .models import image
from .serializers import ImageSerializer, ImageListSerializer, resizeserializer, cropserializer, formatchange
from . import pic
from django_ratelimit.decorators import ratelimit
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache



class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 10

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_image(request):
    serializer = ImageSerializer(data=request.data)
    if serializer.is_valid():
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            
            image = serializer.save(user=request.user)
            
           
            image_instance = PilImage.open(image_file)
            format = image_instance.format
            size = f"{image_instance.width}x{image_instance.height}"

            image.format = format
            image.size = size
            image.save()

            file_url = image.image.url
            response = {
                'id': image.id,
                'url': file_url,
                'format': format,
                'size': size
            }
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    
@api_view(['GET'])
def get_image(request, image_id):
    try:
        cach_key=f"image_{image_id}"
        if cache.get(cach_key):
            return Response(cache.get(cach_key))
        else:
            image_instance = image.objects.get(id=image_id, user=request.user)
            serializer = ImageSerializer(image_instance)
            cache.set(cach_key, serializer.data, 60)
            return Response(serializer.data)
       
    except image.DoesNotExist:
        return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def delete_image(request, image_id):
    try:
        
        image.objects.get(id=image_id, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except image.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
def get_all_images(request):
  
        page=StandardResultsSetPagination()
        images = image.objects.filter(user=request.user)
        paginate=page.paginate_queryset(images, request)
        
        serializer = ImageSerializer(paginate, many=True)
        return page.get_paginated_response(serializer.data)
    
            
        
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def resize_image(request, image_id):
    serializer = resizeserializer(data=request.data)
    if serializer.is_valid():
        width = serializer.validated_data['width']
        height = serializer.validated_data['height']

        try:
        
            image_instance = image.objects.get(id=image_id, user=request.user)
            image_file = image_instance.image
            pil_image = PilImage.open(image_file)
            resized_image = pil_image.resize((width, height))
            buffer = io.BytesIO()
            resized_image.save(buffer, format='PNG')
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="cropped_{image_id}.png"'
            
            return Response(response, status=status.HTTP_201_CREATED)
        except image.DoesNotExist:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def crop_image(request, image_id):
    serializer = cropserializer(data=request.data)
    if serializer.is_valid():
        box = serializer.validated_data['box']

        try:
            image_instance = image.objects.get(id=image_id, user=request.user)
            image_file = image_instance.image
            pil_image = PilImage.open(image_file)
            cropped_image = pil_image.crop(box)
            buffer = io.BytesIO()
            cropped_image.save(buffer, format='PNG')
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="cropped_{image_id}.png"'
            return Response(response, status=status.HTTP_201_CREATED)
        except image.DoesNotExist:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def change_format(request, image_id):
    serializer=formatchange(data=request.data)
    if serializer.is_valid():
       image_instance = image.objects.get(id=image_id, user=request.user) 
       image_file = image_instance.image
       pil_image = PilImage.open(image_file)
       format = serializer.validated_data['format']
       pil_image = pil_image.convert(format)
       buffer = io.BytesIO()
       pil_image.save(buffer, format=format)
       buffer.seek(0)
       response = HttpResponse(buffer, content_type='image/png')
       response['Content-Disposition'] = f'attachment; filename="cropped_{image_id}.png"'
       return Response(response, status=status.HTTP_201_CREATED)
    else:
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  
@ratelimit(key='user', rate='5/m', method='ALL')
@api_view(['POST'])
def remove_background(request, image_id):

        try:
            image_instance = image.objects.get(id=image_id, user=request.user)
            image_file = image_instance.image
            pil_image = PilImage.open(image_file)
            rem_pic=pic.remove_background(pil_image)
            buffer = io.BytesIO()
            rem_pic.save(buffer, format='PNG')
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="removed_{image_id}.png"'
            return Response(response, status=status.HTTP_201_CREATED)
        except image.DoesNotExist:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
   

    
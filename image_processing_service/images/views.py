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
    print(f"Request data: {request.data}")
    serializer = ImageSerializer(data=request.data)
    if serializer.is_valid():
        print("Serializer is valid")
        image_file = request.FILES.get('image')
        if not image_file:
            print("No image file")
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            print("Trying to save image")
            
            image = serializer.save(user=request.user)
            
           
            image_instance = PilImage.open(image_file)
            format = image_instance.format
            size = f"{image_instance.width}x{image_instance.height}"

            print(f"Image format is {format}, size is {size}")

            image.format = format
            image.size = size
            image.save()

            print("Image saved")

            file_url = image.image.url
            response = {
                'id': image.id,
                'url': file_url,
                'format': format,
                'size': size
            }
            print("Returning response")
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    print("Serializer is not valid")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    
@api_view(['GET'])
def get_image(request, image_id):
    print(f"Getting image {image_id}")
    try:
        cach_key=f"image_{image_id}"
        if cache.get(cach_key):
            print(f"Returning cached image {image_id}")
            return Response(cache.get(cach_key))
        else:
            print(f"Loading image {image_id} from database")
            image_instance = image.objects.get(id=image_id, user=request.user)
            serializer = ImageSerializer(image_instance)
            print(f"Saving image {image_id} to cache")
            cache.set(cach_key, serializer.data, 60)
            return Response(serializer.data)
       
    except image.DoesNotExist:
        print(f"Image {image_id} not found")
        return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def delete_image(request, image_id):
    print(f"Deleting image {image_id}")
    try:
        print(f"Trying to delete image {image_id}")
        image.objects.get(id=image_id, user=request.user).delete()
        print(f"Deleted image {image_id}")
        return Response(status=status.HTTP_204_NO_CONTENT)
    except image.DoesNotExist:
        print(f"Image {image_id} not found")
        return Response(status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
def get_all_images(request):
    print(f"Getting all images")
    page=StandardResultsSetPagination()
    print(f"Filtering images for user {request.user}")
    images = image.objects.filter(user=request.user)
    print(f"Paginating images")
    paginate=page.paginate_queryset(images, request)
    print(f"Serializing images")
    serializer = ImageSerializer(paginate, many=True)
    print(f"Returning paginated response")
    return page.get_paginated_response(serializer.data)
    
            
        
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def resize_image(request, image_id):
    print(f"Resizing image {image_id}")
    serializer = resizeserializer(data=request.data)
    if serializer.is_valid():
        print(f"Serializer is valid")
        width = serializer.validated_data['width']
        height = serializer.validated_data['height']

        try:
            print(f"Trying to resize image {image_id}")
            image_instance = image.objects.get(id=image_id, user=request.user)
            image_file = image_instance.image
            pil_image = PilImage.open(image_file)
            resized_image = pil_image.resize((width, height))
            buffer = io.BytesIO()
            resized_image.save(buffer, format='PNG')
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="cropped_{image_id}.png"'
            print(f"Returning resized image {image_id}")
            return Response(response, status=status.HTTP_201_CREATED)
        except image.DoesNotExist:
            print(f"Image {image_id} not found")
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
    print("Serializer is not valid")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def crop_image(request, image_id):
    print(f"Received request to crop image {image_id}")
    serializer = cropserializer(data=request.data)
    if serializer.is_valid():
        print(f"Serializer is valid")
        box = serializer.validated_data['box']

        try:
            print(f"Trying to crop image {image_id}")
            image_instance = image.objects.get(id=image_id, user=request.user)
            image_file = image_instance.image
            pil_image = PilImage.open(image_file)
            cropped_image = pil_image.crop(box)
            buffer = io.BytesIO()
            cropped_image.save(buffer, format='PNG')
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="cropped_{image_id}.png"'
            print(f"Returning cropped image {image_id}")
            return Response(response, status=status.HTTP_201_CREATED)
        except image.DoesNotExist:
            print(f"Image {image_id} not found")
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
    print("Serializer is not valid")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def change_format(request, image_id):
    print(f"Received request to change format of image {image_id}")
    serializer=formatchange(data=request.data)
    if serializer.is_valid():
        print(f"Serializer is valid")
        try:
            print(f"Trying to change format of image {image_id}")
            image_instance = image.objects.get(id=image_id, user=request.user)
            image_file = image_instance.image
            pil_image = PilImage.open(image_file)
            format = serializer.validated_data['format']
            pil_image = pil_image.convert(format)
            buffer = io.BytesIO()
            pil_image.save(buffer, format=format)
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="format_changed_{image_id}.png"'
            print(f"Returning format changed image {image_id}")
            return Response(response, status=status.HTTP_201_CREATED)
        except image.DoesNotExist:
            print(f"Image {image_id} not found")
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        print("Serializer is not valid")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  
@ratelimit(key='user', rate='5/m', method='ALL')
@api_view(['POST'])
def remove_background(request, image_id):

        print(f"Received request to remove background of image {image_id}")
        try:
            print(f"Trying to remove background of image {image_id}")
            image_instance = image.objects.get(id=image_id, user=request.user)
            image_file = image_instance.image
            pil_image = PilImage.open(image_file)
            rem_pic=pic.remove_background(pil_image)
            buffer = io.BytesIO()
            rem_pic.save(buffer, format='PNG')
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="removed_{image_id}.png"'
            print(f"Returning removed background image {image_id}")
            return Response(response, status=status.HTTP_201_CREATED)
        except image.DoesNotExist:
            print(f"Image {image_id} not found")
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
   

    
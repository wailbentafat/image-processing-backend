
# Image Processing Service

## Overview

This project provides a backend service for image processing, offering functionalities such as image upload, transformation, and retrieval. Users can perform transformations like resizing, cropping, format conversion, and background removal. The service is secured with JWT authentication, features caching for performance, and implements rate limiting to prevent abuse.

## Technologies Used

- **Django**: A high-level Python web framework for rapid development.
- **Django REST Framework**: A toolkit for building Web APIs.
- **Simple JWT**: For JSON Web Token (JWT) authentication.
- **Pillow**: Python Imaging Library for image processing.
- **Django Ratelimit**: For rate limiting requests.
- **Django Cache Framework**: For caching transformed images.
- **rembg**: Deep learning-based background removal library.
- **Python's `io` module**: For handling in-memory binary streams.

## Features

### User Authentication

- **Sign-Up**: Users can create new accounts.
- **Log-In**: Users can log into their accounts.
- **JWT Authentication**: Secure endpoints with JSON Web Tokens.

### Image Management

- **Upload Image**: Users can upload images.
- **Transform Image**: Users can perform transformations including resize, crop, change format, and remove background.
- **Retrieve Image**: Users can retrieve images in various formats.
- **List Images**: Users can list all uploaded images with metadata.

### Image Transformations

- **Resize**: Modify the dimensions of the image.
- **Crop**: Crop the image to specified dimensions and coordinates.
- **Change Format**: Convert the image to different formats (e.g., JPEG, PNG).
- **Remove Background**: Use deep learning techniques to remove the background from images.

## Implementation Details

### JWT Authentication

The project uses `djangorestframework-simplejwt` for JWT-based authentication. Tokens are issued upon user login and are required for accessing protected endpoints.

### Caching

Transformed images are cached using Django’s caching framework to enhance performance and reduce the time required for frequently accessed transformations.

### Rate Limiting

The `django_ratelimit` package is employed to restrict the number of requests a user can make to image transformation endpoints. This helps in managing server load and preventing misuse.

### Image Processing

- **Resize**: Adjust the image to specified width and height.
- **Crop**: Extract a portion of the image based on provided dimensions and coordinates.
- **Change Format**: Convert the image to a different file format.
- **Remove Background**: Utilize the `rembg` library to remove the background from images using deep learning.

### Error Handling

Robust error handling and validation are implemented across all endpoints to ensure smooth operation and clear communication of issues.

## Setup and Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/image-processing-backend.git
   ```

2. **Navigate to the Project Directory**
   ```bash
   cd image-processing-backend
   ```

3. **Create and Activate a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Apply Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

## Testing

To run tests, use the Django test management command:

```bash
python manage.py test
```

## Contributing

Contributions are welcome. Please submit issues or pull requests. Ensure that your contributions adhere to the project's coding standards and include appropriate tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

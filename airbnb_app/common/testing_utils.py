import base64

from django.core.files.uploadedfile import SimpleUploadedFile


def create_valid_image(filename: str):
    """Creates a valid image file (only for testing purposes)."""
    return SimpleUploadedFile(
        name=filename,
        content=base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4"
                                 "//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="),
        content_type='image/png',
    )


def create_invalid_image(filename: str):
    """Creates an invalid image file (only for testing purposes)."""
    return SimpleUploadedFile(
        name=filename,
        content=b"_",  # invalid image
    )

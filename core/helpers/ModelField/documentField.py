from django.db import models
from django.core.exceptions import ValidationError
import os

DEFAULT_VALID_EXTENSIONS = [
    ".pdf",  # Adobe PDF
    ".doc",  # Microsoft Word (old)
    ".docx",  # Microsoft Word (new)
    ".xls",  # Microsoft Excel (old)
    ".xlsx",  # Microsoft Excel (new)
    ".ppt",  # Microsoft PowerPoint (old)
    ".pptx",  # Microsoft PowerPoint (new)
    ".odt",  # OpenDocument Text
    ".ods",  # OpenDocument Spreadsheet
    ".odp",  # OpenDocument Presentation
    ".rtf",  # Rich Text Format
    ".txt",  # Plain Text
    ".csv",  # Comma-Separated Values
    ".md",  # Markdown
    ".epub",  # eBook format
    ".xml",  # XML Document
    ".json",  # JSON Document
    ".png",  # Portable Network Graphics
    ".jpg",  # Joint Photographic Experts Group
    ".jpeg",  # Joint Photographic Experts Group
    ".gif",  # Graphics Interchange Format
    ".bmp",  # Bitmap
    ".tiff",  # Tagged Image File Format
]


def validate_document_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # Get file extension
    valid_extensions = DEFAULT_VALID_EXTENSIONS
    if not ext.lower() in valid_extensions:
        raise ValidationError(
            f'Unsupported file extension: {ext}. Allowed extensions are: {", ".join(valid_extensions)}'
        )


class DocumentField(models.FileField):
    default_valid_extensions = DEFAULT_VALID_EXTENSIONS

    def __init__(self, *args, **kwargs):
        validators = kwargs.pop("validators", [])
        validators.append(validate_document_file_extension)
        kwargs["validators"] = validators
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # prevent custom validator from duplicating on migrations
        return name, path, args, kwargs

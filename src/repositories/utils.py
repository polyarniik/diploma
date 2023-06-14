import os
import secrets
import string

from django.conf import settings
from django.core.exceptions import ValidationError
from lxml import etree

from documents_workers.utils import convert_to_docx, get_file_format, get_ooxml_from_docx


def validate_xml(value):
    try:
        etree.fromstring(value, parser=None)
    except etree.XMLSyntaxError:
        raise ValidationError("Invalid XML format")


def get_ooxml(path):
    file_format = get_file_format(path)
    if file_format.lower() == "pdf":
        docx_path = os.path.join(settings.MEDIA_ROOT, "pdf2docx", f"{os.path.basename(path)}.pdf")
        convert_to_docx(path, docx_path)
        return get_ooxml_from_docx(docx_path)
    return get_ooxml_from_docx(path)


def generate_random_hash(length):
    characters = string.ascii_letters + string.digits
    random_hash = "".join(secrets.choice(characters) for _ in range(length))
    return random_hash

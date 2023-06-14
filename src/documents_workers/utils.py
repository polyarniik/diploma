import os
import subprocess
from pathlib import Path

import pdf2docx
from docx import Document


def convert_to_pdf(input_filepath: str, output_dir_path: str):
    subprocess.call(
        [
            [
                "soffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                output_dir_path,
                input_filepath,
            ]  # type: ignore
        ]
    )


def convert_to_docx(input_filepath: str, output_filepath: str):
    cv = pdf2docx.Converter(input_filepath)
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    cv.convert(output_filepath)
    cv.close()


def get_file_format(file_path: str):
    return Path(file_path).suffix


def get_ooxml_from_docx(docx_file):
    document = Document(docx_file)
    ooxml_content = document._element.xml
    return ooxml_content


def convert_ooxml_to_docx(ooxml, docx_file):
    doc = Document()
    doc.oxml = ooxml
    doc.save(docx_file)

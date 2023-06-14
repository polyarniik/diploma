import os
import zipfile
from pathlib import Path

import pdf2docx
from xmldiff import formatting, main

INPUT_DIR = Path(__file__).resolve().parent.joinpath("input")
OUTPUT_DIR = Path(__file__).resolve().parent.joinpath("output")


def convert_pdf_to_docx(input_path: Path, output_path: Path) -> None:
    for root, _, files in os.walk(input_path):
        for i in range(10):
            for f in files:
                if f.endswith(".pdf"):
                    cv = pdf2docx.Converter(os.path.join(root, f))
                    os.makedirs(os.path.join(output_path, f.split(".")[0]), exist_ok=True)
                    cv.convert(os.path.join(output_path, f.split(".")[0], f"iteration_{i+1}.docx"))
                    cv.close()


def docx_to_xml(path: Path):
    doc = zipfile.ZipFile(path).read("word/document.xml")
    return doc


def docx_files_comparing(output_path: Path):
    formatter = formatting.DiffFormatter()

    for root, _, files in os.walk(output_path):
        has_diff = False
        for i in range(len(files)):
            if has_diff:
                print("FAIL", root)
            else:
                for j in range(i + 1, len(files)):
                    f_1 = docx_to_xml(os.path.join(root, files[i]))
                    f_2 = docx_to_xml(os.path.join(root, files[j]))
                    if main.diff_texts(f_1.strip(), f_2.strip(), formatter=formatter):
                        has_diff = True
                        break


if __name__ == "__main__":
    convert_pdf_to_docx(INPUT_DIR, OUTPUT_DIR)
    docx_files_comparing(OUTPUT_DIR)

from xmldiff import main as XMLDiffer

from documents_workers.utils import convert_to_docx, convert_to_pdf, get_file_format, get_ooxml_from_docx


class Comparator:
    def __init__(self, file_path: str, new_file_path: str):
        self.file_path = file_path
        self.new_file_path = new_file_path

    def preproccess(self):
        self.file_docx_representation = self.__convert_to_docx("output_file_path")
        self.new_file_docx_representation = self.__convert_to_docx("output_file_path")
        self.file_ooxml = get_ooxml_from_docx(self.file_docx_representation)
        self.new_file_ooxml = get_ooxml_from_docx(self.new_file_docx_representation)

    def __convert_to_docx(self, output_filepath: str):
        file_format = get_file_format(self.file_path)
        if file_format.upper() == "DOCX":
            convert_to_pdf(self.file_path, output_filepath)
        convert_to_docx(self.file_path, output_filepath)

    def compare(self):
        return XMLDiffer.diff_texts(
            self.file_ooxml,
            self.new_file_ooxml,
            diff_options={
                "F": 1,
                "ratio_mode": "accurate",
            },
        )

from pypdf import PdfReader


def extract_text_from_pdf(file_path: str):

    reader = PdfReader(file_path)

    extracted_text = ""

    for page in reader.pages:
        text = page.extract_text()

        if text:
            extracted_text += text + "\n"

    return extracted_text
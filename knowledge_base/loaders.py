def load_pdf(file_source):
    from pypdf import PdfReader

    try:
        reader = PdfReader(file_source)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except Exception as e:
        print(f"PDF read error: {e}")
        return ""

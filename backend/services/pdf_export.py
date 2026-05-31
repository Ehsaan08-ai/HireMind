import logging

try:
    from weasyprint import HTML

    WEASYPRINT_INSTALLED = True
    WEASYPRINT_ERROR = ""
except (ImportError, OSError) as e:
    WEASYPRINT_INSTALLED = False
    WEASYPRINT_ERROR = str(e)

logger = logging.getLogger("ats_resume_scorer")


def generate_combined_pdf(html_docs: dict[str, str]) -> bytes:
    if not WEASYPRINT_INSTALLED:
        raise ImportError(
            f"WeasyPrint is not functional: {WEASYPRINT_ERROR}. "
            "On Windows, WeasyPrint requires GTK+ to be installed on your system. "
            "Please install the GTK3 runtime for Windows (providing libgobject-2.0-0) "
            "and restart your terminal/IDE."
        )

    documents = []

    for name, html_str in html_docs.items():
        doc = HTML(string=html_str).render()
        documents.append(doc)

    # Combine all documents into one PDF
    first_doc = documents[0]
    for other_doc in documents[1:]:
        for page in other_doc.pages:
            first_doc.pages.append(page)

    # Write combined PDF to bytes
    pdf_bytes = first_doc.write_pdf()
    return pdf_bytes

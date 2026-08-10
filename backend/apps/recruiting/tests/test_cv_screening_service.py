from unittest.mock import MagicMock, patch

from apps.recruiting.services.cv_screening_service import extract_text_from_pdf, screen_candidate


def _fake_page(text):
    page = MagicMock()
    page.extract_text.return_value = text
    return page


@patch("apps.recruiting.services.cv_screening_service.PdfReader")
def test_extract_text_from_pdf_joins_all_pages(mock_reader_class):
    mock_reader = MagicMock()
    mock_reader.pages = [_fake_page("Página uno"), _fake_page("Página dos")]
    mock_reader_class.return_value = mock_reader

    text = extract_text_from_pdf(object())

    assert text == "Página uno\nPágina dos"


@patch("apps.recruiting.services.cv_screening_service.DeepSeekLLM")
def test_screen_candidate_parses_valid_json_response(mock_llm_class):
    mock_llm_class.return_value.ask.return_value = '{"decision": "aprobado", "razon": "Buen fit."}'

    puesto = MagicMock(titulo="Dev", descripcion="...", requisitos="...")
    result = screen_candidate("texto del cv", puesto)

    assert result == {"decision": "aprobado", "razon": "Buen fit."}


@patch("apps.recruiting.services.cv_screening_service.DeepSeekLLM")
def test_screen_candidate_handles_invalid_json_gracefully(mock_llm_class):
    mock_llm_class.return_value.ask.return_value = "esto no es JSON"

    puesto = MagicMock(titulo="Dev", descripcion="...", requisitos="...")
    result = screen_candidate("texto del cv", puesto)

    assert result["decision"] is None

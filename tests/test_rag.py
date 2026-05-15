import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.rag.pipeline import build_prompt, generate_chat_response

def test_build_prompt_injection():
    """Tests that context is correctly formatted into the prompt string without hitting the DB."""
    query = "Does the patient have elevated cholesterol?"
    notes = [
        "Patient exhibits resting heart rate of 95.", 
        "Serum cholesterol is flagged at 240 mg/dl."
    ]
    prompt = build_prompt(query, notes)
    
    assert query in prompt
    assert "Clinical Note 1:" in prompt
    assert "Patient exhibits resting heart rate of 95." in prompt
    assert "Clinical Note 2:" in prompt
    assert "Serum cholesterol is flagged at 240 mg/dl." in prompt

@pytest.mark.asyncio
@patch('app.rag.pipeline.client.chat.completions.create', new_callable=AsyncMock)
@patch('app.rag.pipeline.retrieve_context', new_callable=AsyncMock)
@patch('app.rag.pipeline.generate_embedding', new_callable=AsyncMock)
async def test_generate_chat_response_mocked(mock_embed, mock_retrieve, mock_completion):
    """Tests the full RAG execution path with a mocked OpenAI client and DB session."""
    
    mock_embed.return_value = [0.05] * 1536
    mock_retrieve.return_value = ["Mocked note text indicating high blood pressure."]
    
    mock_choice = MagicMock()
    mock_choice.message.content = "Based on the records, the patient has high blood pressure."
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_completion.return_value = mock_response
    
    dummy_session = AsyncMock()
    
    response = await generate_chat_response(dummy_session, "What is the blood pressure status?")
    
    assert response == "Based on the records, the patient has high blood pressure."
    mock_embed.assert_called_once_with("What is the blood pressure status?")
    mock_retrieve.assert_called_once_with(dummy_session, [0.05] * 1536)
    mock_completion.assert_called_once()
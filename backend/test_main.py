import pytest
from fastapi.testclient import TestClient
from fastapi import WebSocket
from main import app, SUBTOPICS, extract_text_from_page, generate_dynamic_question_from_text


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


# Test to ensure the root path works and returns HTML
def test_get(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "<html>" in response.text


# Test topic selection - AI and ML
def test_topic_selection(client):
    # Test AI selection
    response = client.websocket_connect("/ws")
    response.send_json({"topic": "AI"})
    data = response.receive_json()
    assert data["type"] == "subtopics"
    assert "Overview of AI" in data["subtopics"]

    # Test ML selection
    response.send_json({"topic": "ML"})
    data = response.receive_json()
    assert data["type"] == "subtopics"
    assert "Machine Learning – The foundation of Artificial Intelligence" in data["subtopics"]


# Test subtopic selection and question generation
def test_subtopic_selection(client):
    # Select topic AI and get subtopics
    response = client.websocket_connect("/ws")
    response.send_json({"topic": "AI"})
    subtopic_data = response.receive_json()
    subtopics = subtopic_data["subtopics"]
    assert len(subtopics) > 0

    # Select a subtopic and level
    response.send_json({"subtopic": subtopics[0], "level": "easy"})
    question_data = response.receive_json()
    assert question_data["type"] == "question"
    assert "?" in question_data["question"]  # Check if it's a question


# Test the answer evaluation
def test_answer_evaluation(client):
    # Select topic AI, subtopic, and level
    response = client.websocket_connect("/ws")
    response.send_json({"topic": "AI"})
    subtopic_data = response.receive_json()
    subtopics = subtopic_data["subtopics"]

    response.send_json({"subtopic": subtopics[0], "level": "easy"})
    question_data = response.receive_json()
    question = question_data["question"]

    # Submit an answer
    response.send_json({"answer": "Artificial Intelligence (AI) is technology used to perform tasks that normally require human intelligence."})
    evaluation_data = response.receive_json()
    assert evaluation_data["type"] == "evaluation"
    assert "Feedback" in evaluation_data["feedback"]
    assert 1 <= evaluation_data["score"] <= 10


# Test invalid topic
def test_invalid_topic_selection(client):
    response = client.websocket_connect("/ws")
    response.send_json({"topic": "InvalidTopic"})
    error_data = response.receive_json()
    assert error_data["type"] == "error"
    assert error_data["message"] == "Invalid topic"


# Test invalid subtopic
def test_invalid_subtopic_selection(client):
    response = client.websocket_connect("/ws")
    response.send_json({"topic": "AI"})
    subtopic_data = response.receive_json()
    subtopics = subtopic_data["subtopics"]

    response.send_json({"subtopic": "InvalidSubtopic", "level": "easy"})
    error_data = response.receive_json()
    assert error_data["type"] == "error"
    assert error_data["message"] == "Invalid subtopic selected"


# Test invalid answer submission
def test_invalid_answer_submission(client):
    # Select topic AI and subtopic
    response = client.websocket_connect("/ws")
    response.send_json({"topic": "AI"})
    subtopic_data = response.receive_json()
    subtopics = subtopic_data["subtopics"]
    response.send_json({"subtopic": subtopics[0], "level": "easy"})
    question_data = response.receive_json()

    # Submit an invalid answer
    response.send_json({"answer": ""})
    error_data = response.receive_json()
    assert error_data["type"] == "error"
    assert error_data["message"] == "No answer provided"


# Test the text extraction from page (using mocked page numbers for subtopics)
def test_extract_text_from_page():
    # Assuming the AI subtopic is on page 7, we mock the PDF file
    pdf_path = "mocked_pdf_path"  # Specify a valid path to test
    text = extract_text_from_page(pdf_path, 7)
    assert len(text) > 0  # Check that some text is extracted


# Test the question generation function
def test_generate_dynamic_question_from_text():
    text = "Artificial Intelligence (AI) is an attempt to make a computer, a robot, or other piece of technology ‘think’ and process data in the same way as humans."
    context, question = generate_dynamic_question_from_text(text, "easy")
    assert "?" in question
    assert len(question) > 0

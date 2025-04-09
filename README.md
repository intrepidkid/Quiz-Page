
# 🧠 AI/ML Quiz Page

An interactive AI/ML Quiz application that uses a fine-tuned LLM to generate topic-based questions and evaluate user answers in real-time. Built with **ReactJS**, **FastAPI**, **WebSockets**, and **Hugging Face Transformers**.

> ⚠️ This is an early-stage project and will be expanded further to reach its full potential as an AI/ML quiz bot.

---

## 🚀 Features

- Real-time quiz using WebSocket
- Dynamic question generation from PDFs using T5 transformer
- Semantic answer evaluation using Sentence Transformers
- Frontend with topic/subtopic/difficulty selection
- Immediate feedback and score (0–10) on answers
- Fully asynchronous backend with FastAPI and Uvicorn
- Unit testing included

---

## 🛠️ Tech Stack

### 🔹 Frontend
- ReactJS
- HTML/CSS
- WebSocket (Client-Side)

### 🔹 Backend
- **FastAPI**: API framework for async backend
- **Uvicorn**: ASGI server for FastAPI
- **WebSocket**: Real-time communication
- **Transformers (Hugging Face)**: T5 model for question generation
- **SentenceTransformers**: MiniLM for semantic similarity scoring
- **PyMuPDF (fitz)**: Extract content from PDFs
- **HTMLResponse**: For rendering HTML via FastAPI

---

## 🧠 Prompt Engineering Best Practices

The effectiveness of the AI/ML quiz system depends significantly on how prompts are designed and used with the models:

- **Clarity and Specificity**: Prompts given to the T5 model for question generation are constructed clearly and concisely to produce relevant questions.
- **Contextual Chunking**: Only the relevant section from the selected subtopic in the PDF is passed to the model, ensuring better focus and relevance.
- **Few-shot Potential** *(to be added in future)*: Example-based prompting could improve question quality and variety as the system evolves.
- **Semantic Scoring Feedback**: Evaluation feedback is based on semantic similarity, emphasizing not just keywords but meaning—critical for NLP tasks.
- **Fallback Strategy** *(early-stage note)*: Simpler fallback (PDFs over external APIs) was used to ensure reliability and reduce latency.
- **Dynamic Prompt Inputs**: The system is structured to accept dynamic topic/difficulty inputs and generate corresponding prompts/questions.

---

## 📦 Models Used

### 1. **Question Generation**
- **Model**: `valhalla/t5-small-qg-prepend`
- **Purpose**: Generates questions based on topic PDFs

### 2. **Answer Evaluation**
- **Model**: `all-MiniLM-L6-v2` (Sentence-BERT)
- **Purpose**: Computes semantic similarity between user input and expected answer

---

## ⚙️ How It Works

1. **Topic Selection**:
   - Choose between `AI` or `ML`.
   - Each has 3 subtopics (from PDF).

2. **Question Generation**:
   - Content is extracted from a selected subtopic PDF.
   - Passed to T5 to generate a question.

3. **User Response**:
   - User submits answer via WebSocket.
   - Answer is evaluated using cosine similarity (via SentenceTransformer).

4. **Feedback & Scoring**:
   - Score (0–10) and dynamic feedback is returned to the frontend.

---

## 📂 Folder Structure (Expected)

```
AI_quiz/
├── backend/
│   ├── main.py
│   ├── utils.py
│   ├── models/
│   ├── pdfs/
│   └── test_main.py
├── frontend/
│   └── [React App Files]
└── README.md
```

---

## 🧪 Testing

- ✅ Unit tests are available in `backend/test_main.py`
- Run using `pytest` or any preferred test runner
- All tests currently pass ✅ (green dot)

---

## 💡 Improvements Planned

- Expand subtopics dynamically
- Use external sources (e.g., Wikipedia API) with optimization
- Fine-tune models for better performance
- Add user authentication and progress tracking

---

## 🖥️ Local Development

### 1. Start Backend
```bash
uvicorn main:app --reload
```

### 2. Start Frontend
```bash
npm install
npm start
```

### 3. Access Application
Open [http://localhost:3000](http://localhost:3000)

---

## 🤝 Credits

Created by intrepidkid as a part of the AI/ML learning journey.

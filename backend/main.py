from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import fitz  # PyMuPDF for PDF processing
from sentence_transformers import SentenceTransformer, util
from transformers import T5Tokenizer, T5ForConditionalGeneration

app = FastAPI()

# Load SentenceTransformer for answer evaluation
sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

# Use T5 tokenizer and model
qg_tokenizer = T5Tokenizer.from_pretrained("valhalla/t5-small-qg-prepend")
qg_model = T5ForConditionalGeneration.from_pretrained("valhalla/t5-small-qg-prepend")

# Hardcoded subtopics and their corresponding page numbers
SUBTOPICS = {
    "AI": {
        "Overview of AI": 7,
        "Areas of Application of AI in our Daily Life": 16,
        "Application Program Interfaces (APIs)": 24
    },
    "ML": {
        "Machine Learning – The foundation of Artificial Intelligence": 6,
        "Understanding Data and Datasets": 10,
        "Machine Learning and CHATBOTs": 29
    }
}

# Function to extract content from a specific page
def extract_text_from_page(pdf_path, page_number, char_limit=1000):
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_number - 1)  # Convert to 0-based index
        text = page.get_text("text")[:char_limit]
        return text.strip()
    except Exception as e:
        return f"Error extracting text: {str(e)}"

# WebSocket communication
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")

    try:
        topic, pdf_path = None, None

        while True:
            data = await websocket.receive_json()

            # Handle topic selection
            if "topic" in data:
                topic = data["topic"]

                # Select PDF based on topic
                if topic == "AI":
                    pdf_path = "C:/Users/karth/AppData/Roaming/Python/Python312/site-packages/AI_Game/Student-Guide-Module-1-Fundamentals-of-AI.pdf"
                elif topic == "ML":
                    pdf_path = "C:/Users/karth/AppData/Roaming/Python/Python312/site-packages/AI_Game/Student-Guide-Module-2-Machine-Learning.pdf"
                else:
                    await websocket.send_json({"type": "error", "message": "Invalid topic"})
                    continue

                # Send subtopics for the selected topic
                subtopics = list(SUBTOPICS.get(topic, {}).keys())
                if not subtopics:
                    await websocket.send_json({"type": "error", "message": "No subtopics available for this topic"})
                    continue
                await websocket.send_json({"type": "subtopics", "subtopics": subtopics})

            # Handle subtopic and level selection
            elif "subtopic" in data and "level" in data:
                subtopic = data["subtopic"]
                level = data["level"]

                # Fetch the page number for the subtopic
                page_number = SUBTOPICS.get(topic, {}).get(subtopic)
                if page_number is None:
                    await websocket.send_json({"type": "error", "message": "Invalid subtopic selected"})
                    continue

                # Extract text from the subtopic's page
                subtopic_text = extract_text_from_page(pdf_path, page_number)
                if not subtopic_text.strip():
                    await websocket.send_json({"type": "error", "message": "No content found for this subtopic"})
                    continue

                # Generate a question based on the subtopic text
                context, question = generate_dynamic_question_from_text(subtopic_text, level)
                await websocket.send_json({"type": "question", "question": question})

            # Handle answer submission
            elif "answer" in data:
                user_answer = data["answer"]

                # Evaluate the answer
                score, feedback = evaluate_answer(question, context, user_answer)
                await websocket.send_json({
                    "type": "evaluation",
                    "score": score,
                    "feedback": feedback
                })

    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Client disconnected")
        await websocket.close()

# Function to generate a dynamic question based on extracted text 
def generate_dynamic_question_from_text(text: str, level: str) -> tuple:
    """
    Generates a question from the extracted text based on difficulty.
    """
    if level == "easy":
        question_prompt = f"generate question: simple | context: {text}"
    elif level == "medium":
        question_prompt = f"generate question: moderate | context: {text}"
    elif level == "hard":
        question_prompt = f"generate question: difficult | context: {text}"
    else:
        question_prompt = f"generate question: | context: {text}"

    # Tokenize and generate the question
    inputs = qg_tokenizer.encode(question_prompt, return_tensors="pt", truncation=True, max_length=512)
    outputs = qg_model.generate(inputs, max_length=100, num_beams=4, early_stopping=True)
    question = qg_tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    # Ensure the question ends with a question mark
    if not question.endswith('?'):
        question += "?"

    return text, question

# Evaluate answer
def evaluate_answer(question: str, context: str, user_answer: str) -> tuple:
    user_answer_embedding = sentence_model.encode(user_answer, convert_to_tensor=True)
    context_embedding = sentence_model.encode(context, convert_to_tensor=True)

    similarity = util.pytorch_cos_sim(user_answer_embedding, context_embedding)[0][0].item()
    score = round(similarity * 10)
    score = min(10, max(score, 1))

    if similarity > 0.8:
        feedback = "Excellent! Your answer is highly relevant."
    elif similarity > 0.5:
        feedback = "Good job! Your answer is close. Elaborate more!"
    elif similarity > 0.3:
        feedback = "You're on the right track. Revisit key points."
    else:
        feedback = "Your answer doesn't align. Revise the concepts."

    return score, feedback



# Basic HTML interface for testing
@app.get("/")
async def get():
    return HTMLResponse("""
    <html>
        <head>
            <script>
                const ws = new WebSocket("ws://localhost:8000/ws");

                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);

                    if (data.type === "subtopics") {
                        const subtopics = data.subtopics;
                        let subtopicSelect = "<h2>Select a Subtopic:</h2><select id='subtopic'>";
                        subtopics.forEach(subtopic => {
                            subtopicSelect += `<option value="${subtopic}">${subtopic}</option>`;
                        });
                        subtopicSelect += "</select>";
                        document.getElementById("subtopic-container").innerHTML = subtopicSelect;
                        document.getElementById("start-subtopic-quiz").style.display = "block"; // Show the subtopic quiz button
                    } else if (data.type === "question") {
                        document.getElementById("question").innerText = data.question;
                        document.getElementById("answer-container").style.display = "block"; // Show the answer input and submit button
                    } else if (data.type === "evaluation") {
                        document.getElementById("feedback").innerText = `Feedback: ${data.feedback}`;
                        document.getElementById("score").innerText = `Score: ${data.score}/10`;
                        document.getElementById("next-round").style.display = "block"; // Show the Next Round button
                    }
                };

                function selectTopic() {
                    const topic = document.getElementById("topic").value;
                    ws.send(JSON.stringify({ topic }));
                    document.getElementById("subtopic-container").innerHTML = "Loading subtopics...";
                    document.getElementById("start-subtopic-quiz").style.display = "none"; // Hide the subtopic quiz button until subtopics load
                }

                function selectSubtopic() {
                    const subtopic = document.getElementById("subtopic").value;
                    const level = document.getElementById("level").value;
                    ws.send(JSON.stringify({ subtopic, level }));
                    document.getElementById("question").innerText = "Waiting for the question...";
                    document.getElementById("answer-container").style.display = "none"; // Hide the answer section
                }

                function submitAnswer() {
                    const answer = document.getElementById("answer").value;
                    ws.send(JSON.stringify({ answer }));
                }

                function resetGame() {
                    // Reset UI elements for a new round
                    document.getElementById("topic").value = "";
                    document.getElementById("subtopic-container").innerHTML = "";
                    document.getElementById("question").innerText = "Select a topic to start.";
                    document.getElementById("answer").value = "";
                    document.getElementById("feedback").innerText = "";
                    document.getElementById("score").innerText = "";
                    document.getElementById("next-round").style.display = "none"; // Hide the Next Round button
                }
            </script>
        </head>
        <body>
            <h1>AI/ML Quiz Game</h1>

            <!-- Topic Selection -->
            <div>
                <label for="topic">Choose Topic:</label>
                <select id="topic" onchange="selectTopic()">
                    <option value="">-- Select Topic --</option>
                    <option value="AI">Artificial Intelligence</option>
                    <option value="ML">Machine Learning</option>
                </select>
            </div>

            <!-- Subtopic Container -->
            <div id="subtopic-container"></div>

            <!-- Level Selection -->
            <div>
                <label for="level">Choose Level:</label>
                <select id="level">
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                </select>
            </div>

            <button id="start-subtopic-quiz" style="display:none;" onclick="selectSubtopic()">Start Subtopic Quiz</button>

            <!-- Question Section -->
            <h2 id="question">Select a topic to start.</h2>

            <!-- Answer Input -->
            <div id="answer-container" style="display:none;">
                <input id="answer" placeholder="Enter your answer">
                <button onclick="submitAnswer()">Submit Answer</button>
            </div>

            <!-- Feedback Section -->
            <h3 id="feedback"></h3>
            <h3 id="score"></h3>

            <!-- Next Round Button -->
            <button id="next-round" style="display:none;" onclick="resetGame()">Next Round</button>
        </body>
    </html>
    """)


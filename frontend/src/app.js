import React, { useState, useEffect } from "react";
import './app.css';

function App() {
    const [topic, setTopic] = useState("");
    const [level, setLevel] = useState("");
    const [subtopic, setSubtopic] = useState(""); // New state for subtopic
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState("");
    const [evaluation, setEvaluation] = useState(null);
    const [subtopics, setSubtopics] = useState([]); // New state to store subtopics
    const [socket, setSocket] = useState(null);

    // Initialize WebSocket connection
    useEffect(() => {
        const ws = new WebSocket("ws://127.0.0.1:8000/ws");
        setSocket(ws);

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === "subtopics") {
                setSubtopics(data.subtopics); // Update subtopics after topic selection
            } else if (data.type === "question") {
                setQuestion(data.question);
                setAnswer(""); // Reset the answer field when a new question arrives
                setEvaluation(null); // Reset evaluation when a new question arrives
            } else if (data.type === "evaluation") {
                setEvaluation({
                    score: data.score,
                    feedback: data.feedback,
                });
            }
        };

        ws.onopen = () => console.log("WebSocket connection established.");
        ws.onclose = () => console.log("WebSocket connection closed.");
        ws.onerror = (error) => console.error("WebSocket error:", error);

        // Cleanup WebSocket on component unmount
        return () => {
            ws.close();
        };
    }, []);

    // Handle topic selection
    const handleTopicSelection = (selectedTopic) => {
        setTopic(selectedTopic);
        setLevel(""); // Reset level when new topic is selected
        setSubtopic(""); // Reset subtopic
        setQuestion(""); // Reset question
        setEvaluation(null); // Reset evaluation
        setSubtopics([]); // Clear subtopics

        // Send topic to backend to fetch subtopics
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ topic: selectedTopic }));
        }
    };

    // Handle subtopic selection
    const handleSubtopicSelection = (selectedSubtopic) => {
        setSubtopic(selectedSubtopic);
        setQuestion(""); // Reset question when a new subtopic is selected
        setEvaluation(null); // Reset evaluation
    };

    // Handle level selection and request for a question
    const handleLevelSelection = (selectedLevel) => {
        setLevel(selectedLevel);
        setQuestion(""); // Reset question when a new level is selected
        setEvaluation(null); // Reset evaluation
        if (socket && socket.readyState === WebSocket.OPEN) {
            // Send topic, subtopic, and level to backend to request a question
            socket.send(JSON.stringify({ subtopic, level: selectedLevel }));
        }
    };

    // Handle answer submission
    const handleSubmitAnswer = () => {
        if (socket && socket.readyState === WebSocket.OPEN && answer.trim() !== "") {
            // Send user's answer to the backend for evaluation
            socket.send(JSON.stringify({ answer }));
        }
    };

    // Reset the game to allow selecting a new topic
    const handleNextRound = () => {
        setTopic("");
        setLevel("");
        setSubtopic("");
        setQuestion("");
        setAnswer("");
        setEvaluation(null); // Reset everything for the new round
    };

    return (
        <div className="app">
            <h1>1Q AI/ML Quiz</h1>

            {/* Topic selection */}
            {!topic ? (
                <div className="selection">
                    <h2>Select a Topic:</h2>
                    <button onClick={() => handleTopicSelection("AI")}>Artificial Intelligence</button>
                    <button onClick={() => handleTopicSelection("ML")}>Machine Learning</button>
                </div>
            ) : !subtopic ? (
                <div className="selection">
                    <h2>Select a Subtopic:</h2>
                    {/* Display subtopic selection after topic selection */}
                    {subtopics.length > 0 ? (
                        <div>
                            {subtopics.map((sub, index) => (
                                <button key={index} onClick={() => handleSubtopicSelection(sub)}>
                                    {sub}
                                </button>
                            ))}
                        </div>
                    ) : (
                        <p>Loading subtopics...</p>
                    )}
                </div>
            ) : !level ? (
                <div className="selection">
                    <h2>Select Difficulty Level:</h2>
                    <button onClick={() => handleLevelSelection("easy")}>Easy</button>
                    <button onClick={() => handleLevelSelection("medium")}>Medium</button>
                    <button onClick={() => handleLevelSelection("hard")}>Hard</button>
                </div>
            ) : (
                <div className="quiz">
                    <h2>Question:</h2>
                    <p>{question || "Waiting for the question..."}</p>

                    {/* If evaluation is not available, show answer input and submit button */}
                    {!evaluation ? (
                        <div className="answer-section">
                            <input
                                type="text"
                                placeholder="Enter your answer"
                                value={answer}
                                onChange={(e) => setAnswer(e.target.value)}
                            />
                            <button onClick={handleSubmitAnswer}>Submit Answer</button>
                        </div>
                    ) : (
                        <div className="evaluation">
                            <h3>Score: {evaluation.score}/10</h3>
                            <p>Feedback: {evaluation.feedback}</p>
                            <button onClick={handleNextRound}>Next Round</button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default App;

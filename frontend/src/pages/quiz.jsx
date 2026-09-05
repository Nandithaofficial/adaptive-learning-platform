import { useState } from "react";
import { useNavigate } from "react-router-dom";

const questions = [
  {
    question: "What is 2 + 2?",
    options: ["3", "4", "5", "6"],
    answer: "4",
  },
  {
    question: "What is the capital of France?",
    options: ["Berlin", "Madrid", "Paris", "Rome"],
    answer: "Paris",
  },
  {
    question: "Which language is React built with?",
    options: ["Python", "JavaScript", "Ruby", "Go"],
    answer: "JavaScript",
  },
];

function Quiz() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [selected, setSelected] = useState(null);
  const [showResult, setShowResult] = useState(false);
  const navigate = useNavigate();

  const handleNext = () => {
    if (selected === questions[currentIndex].answer) {
      setScore(score + 1);
    }
    setSelected(null);

    if (currentIndex + 1 < questions.length) {
      setCurrentIndex(currentIndex + 1);
    } else {
      setShowResult(true);
    }
  };

  if (showResult) {
    return (
      <div className="quiz-container">
        <h1>Quiz Complete!</h1>
        <p>Your score: {score} / {questions.length}</p>
        <button onClick={() => navigate("/dashboard")}>Back to Dashboard</button>
      </div>
    );
  }

  const current = questions[currentIndex];

  return (
    <div className="quiz-container">
      <h1>Quiz</h1>
      <p>Question {currentIndex + 1} of {questions.length}</p>
      <h2>{current.question}</h2>

      <div className="options">
        {current.options.map((option) => (
          <button
            key={option}
            className={selected === option ? "selected" : ""}
            onClick={() => setSelected(option)}
          >
            {option}
          </button>
        ))}
      </div>

      <button onClick={handleNext} disabled={!selected}>
        {currentIndex + 1 === questions.length ? "Finish" : "Next"}
      </button>
    </div>
  );
}

export default Quiz;
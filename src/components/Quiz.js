import React, { useState } from "react";
import styles from "./Quiz.module.css";

export default function Quiz({ question, options, answer, maxTries = 1 }) {
    const [selected, setSelected] = useState(null);
    const [submitted, setSubmitted] = useState(false);
    const [tries, setTries] = useState(0);
    const [showAnswer, setShowAnswer] = useState(false);

    const handleSubmit = () => {
        if (selected !== null) {
            setSubmitted(true);
            setTries((prev) => prev + 1);
        }
    };

    return (
        <div className={styles.quizBox}>
            <p className={styles.question}>{question}</p>
            <ul className={styles.options}>
                {options.map((opt, idx) => (
                    <li key={idx} className={styles.option}>
                        <label>
                            <input
                                type="radio"
                                name={`quiz-${question}`}
                                value={idx}
                                checked={selected === idx}
                                onChange={() => {
                                    setSelected(idx);
                                    setSubmitted(false);
                                    setShowAnswer(false);
                                }}
                            />
                            {" "}{opt}
                        </label>
                    </li>
                ))}
            </ul>

            <div className={styles.buttonRow}>
                <button
                    className={styles.button}
                    onClick={handleSubmit}
                    disabled={submitted || selected === null}
                >
                    Submit
                </button>

                {/* Show Answer button (only if wrong AND tries >= maxTries) */}
                {submitted && selected !== answer && tries >= maxTries && (
                    <button
                        className={`${styles.button} ${styles.showAnswerBtn}`}
                        onClick={() => setShowAnswer(true)}
                    >
                        Show Answer
                    </button>
                )}
            </div>

            {submitted && (
                <p
                    className={`${styles.feedback} ${selected === answer ? styles.correct : styles.incorrect
                        }`}
                >
                    {selected === answer ? "✅ Correct!" : "❌ Try again."}
                </p>
            )}

            {showAnswer && (
                <p className={`${styles.feedback} ${styles.correct}`}>
                    ✅ The correct answer is: <strong>{options[answer]}</strong>
                </p>
            )}
        </div>
    );
}

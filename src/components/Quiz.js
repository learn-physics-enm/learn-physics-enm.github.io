import React, { useState } from "react";
import styles from "./Quiz.module.css"; // keep your CSS module

export default function Quiz({ question, options, answer }) {
    const [selected, setSelected] = useState(null);
    const [submitted, setSubmitted] = useState(false);

    const handleSubmit = () => {
        if (selected !== null) {
            setSubmitted(true);
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
                                name={`quiz-${question}`} // unique per quiz
                                value={idx}
                                checked={selected === idx}
                                onChange={() => {
                                    setSelected(idx);
                                    setSubmitted(false); // 🚀 reset feedback until resubmit
                                }}
                            />
                            {" "}{opt}
                        </label>
                    </li>
                ))}
            </ul>
            <button
                className={styles.button}
                onClick={handleSubmit}
                disabled={submitted || selected === null} // disable if no choice
            >
                Submit
            </button>
            {submitted && (
                <p
                    className={`${styles.feedback} ${selected === answer ? styles.correct : styles.incorrect
                        }`}
                >
                    {selected === answer ? "✅ Correct!" : "❌ Try again."}
                </p>
            )}
        </div>
    );
}

import { useEffect, useState } from 'react'
import './App.css'

interface Question {
  question: string
  question_id: string
  category: string
  value: string
  round: string
}

export async function fetchQuestion(): Promise<Question> {
  const rounds = ["Jeopardy!", "Double Jeopardy!", "Final Jeopardy!"];
  const values = [200, 300, 500, 750, 1000, 1200];

  let attempts = 0;
  const maxAttempts = 10; // For some combinations of round/value there's no valid question, so I fetch with retry

  while (attempts < maxAttempts) {
    attempts++;

    const round = rounds[Math.floor(Math.random() * rounds.length)];
    const value = values[Math.floor(Math.random() * values.length)];

    const response = await fetch(
      `http://localhost:8000/question/?round=${encodeURIComponent(round)}&value=${value}`
    );

    if (!response.ok) {
      continue;
    }

    const data: Question = await response.json();

    if (data && data.question_id) {
      return data;
    }
  }

  throw new Error("Could not fetch a valid question after several attempts");
}

function App() {
  const [question, setQuestion] = useState<Question | null>(null)
  const [answer, setAnswer] = useState('')
  const [isStarted, setIsStarted] = useState(false)
  const [elapsedSeconds, setElapsedSeconds] = useState(0)
  const [blockUi, setBlockUi] = useState(false)
  const [validationResult, setValidationResult] = useState("")

  useEffect(() => {
    if (!isStarted) return
    const intervalId = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1)
    }, 1000)
    return () => clearInterval(intervalId)
  }, [isStarted])

  const handleStart = async () => {
    setIsStarted(true)
    setElapsedSeconds(0)
    setAnswer('')
    const q = await fetchQuestion()
    setQuestion(q)
  }

  const submitAnswer = async () => {
    if (!question) return
    
    setBlockUi(true);

    try {
      const response = await fetch("http://localhost:8000/verify-answer/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question_id: question.question_id,
          user_answer: answer,
        }),
      })

      if (!response.ok) {
        throw new Error(`Failed to verify answer: ${response.statusText}`)
      }

      const result = await response.json()
      setValidationResult(String(result.is_correct));

    } catch (error) {
      console.error("Error submitting answer:", error)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <main style={{ flex: '1 0 auto' }}>
        <div style={{ maxWidth: 800, margin: '0 auto', padding: 24 }}>
          <h2 style={{ textAlign: 'center' }}>Jeopardy simulator</h2>

          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 16 }}>
            <button
              onClick={handleStart}
              disabled={isStarted}
              style={{
                backgroundColor: isStarted ? undefined : '#22c55e',
                color: isStarted ? undefined : '#fff',
                border: isStarted ? undefined : '1px solid #16a34a',
                padding: '8px 16px',
                borderRadius: 6,
                cursor: isStarted ? 'default' : 'pointer',
                opacity: isStarted ? 0.6 : 1
              }}
            >
              Start
            </button>
          </div>

          <h2 style={{ textAlign: 'center', minHeight: 48, margin: 16 }}>
            {question?.question} {isStarted && (

              <table className="info-table">
                <tr>
                  <th>ID</th>
                  <td>{question?.question_id}</td>
                </tr>
                <tr>
                  <th>Round</th>
                  <td>{question?.round}</td>
                </tr>
                <tr>
                  <th>Category</th>
                  <td>{question?.category}</td>
                </tr>
                <tr>
                  <th>Value</th>
                  <td>{question?.value}$</td>
                </tr>
                <tr>
                  <th>Time</th>
                  <td>{elapsedSeconds}s</td>
                </tr>
              </table>

            )}
          </h2>

          <div style={{ display: 'flex', gap: 8, justifyContent: 'center', alignItems: 'center' }}>
            <input
              type="text"
              placeholder="Type your answer"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              disabled={!isStarted || blockUi}
              style={{ padding: 12, width: 520, fontSize: 18, borderRadius: 6 }}
            />
            {
              isStarted && <button className={!blockUi? "submit-btn" : ""} disabled={blockUi} onClick={(e) => submitAnswer()}>Submit</button>
            }

          </div>
          
          {
            validationResult && <div className="validationBlock">
              Valid: {validationResult.toUpperCase()}
            </div>
          }

          {/* <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginTop: 16 }}>
            <div style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: 12 }}>
              <h3 style={{ margin: 0, fontSize: 16, textAlign: 'center' }}>Agent easy</h3>
            </div>
            <div style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: 12 }}>
              <h3 style={{ margin: 0, fontSize: 16, textAlign: 'center' }}>Agent medium</h3>
            </div>
            <div style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: 12 }}>
              <h3 style={{ margin: 0, fontSize: 16, textAlign: 'center' }}>Agent hard</h3>
            </div>
          </div> */}


        </div>
      </main>
      <footer style={{ flexShrink: 0, padding: '12px 0', textAlign: 'right', color: '#666', width: '100%', backgroundColor: '#f0f0f0' }}>
        © Shtiliyan Uzunov interview submission for TwinKnowledge &nbsp; &nbsp; &nbsp;
      </footer>
    </div>
  )
}

export default App

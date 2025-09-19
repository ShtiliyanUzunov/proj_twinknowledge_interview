import { useEffect, useState } from 'react'
import './App.css'

type Question = {
  id: string
  text: string
}

async function mockFetchQuestion(): Promise<Question> {
  // Simulate a backend call
  await new Promise((resolve) => setTimeout(resolve, 300))
  return { id: 'q1', text: 'What is the capital of France?' }
}

function App() {
  const [question, setQuestion] = useState<Question | null>(null)
  const [answer, setAnswer] = useState('')
  const [isStarted, setIsStarted] = useState(false)
  const [elapsedSeconds, setElapsedSeconds] = useState(0)

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
    const q = await mockFetchQuestion()
    setQuestion(q)
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <main style={{ flex: '1 0 auto' }}>
        <div style={{ maxWidth: 800, margin: '0 auto', padding: 24 }}>
          <h2 style={{ textAlign: 'center'}}>Jeopardy simulator</h2>

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

          <h1 style={{ textAlign: 'center', minHeight: 48, margin: 16 }}>
            {question?.text} {isStarted && (
              <span>{elapsedSeconds}s</span>
            )}
          </h1>

          <div style={{ display: 'flex', gap: 8, justifyContent: 'center', alignItems: 'center' }}>
            <input
              type="text"
              placeholder="Type your answer"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              disabled={!isStarted}
              style={{ padding: 12, width: 520, fontSize: 18, borderRadius: 6 }}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginTop: 16 }}>
            <div style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: 12 }}>
              <h3 style={{ margin: 0, fontSize: 16, textAlign: 'center' }}>Agent easy</h3>
            </div>
            <div style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: 12 }}>
              <h3 style={{ margin: 0, fontSize: 16, textAlign: 'center' }}>Agent medium</h3>
            </div>
            <div style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: 12 }}>
              <h3 style={{ margin: 0, fontSize: 16, textAlign: 'center' }}>Agent hard</h3>
            </div>
          </div>

  
        </div>
      </main>
      <footer style={{ flexShrink: 0, padding: '12px 0', textAlign: 'right', color: '#666', width: '100%', backgroundColor: '#f0f0f0' }}>
        © Shtiliyan Uzunov interview submission for TwinKnowledge &nbsp; &nbsp; &nbsp;
      </footer>
    </div>
  )
}

export default App

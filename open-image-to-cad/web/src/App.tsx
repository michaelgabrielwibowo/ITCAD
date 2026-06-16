import { useState } from 'react'

function App() {
  const [prompt, setPrompt] = useState('make a plate with two holes')
  const [status, setStatus] = useState('')

  const handleGenerate = async () => {
    setStatus('Generating...')
    try {
      const res = await fetch('http://localhost:8000/text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, adapter: 'mock', engine: 'cadquery' })
      })
      const data = await res.json()
      setStatus(`Status: ${data.status}, run_id: ${data.run_id}`)
    } catch (e) {
      setStatus(`Error: ${e}`)
    }
  }

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>Open Image-to-CAD</h1>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxWidth: '400px' }}>
        <textarea
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          rows={4}
        />
        <button onClick={handleGenerate} style={{ padding: '0.5rem' }}>
          Generate (Mock)
        </button>
        <div>{status}</div>
      </div>
    </div>
  )
}

export default App

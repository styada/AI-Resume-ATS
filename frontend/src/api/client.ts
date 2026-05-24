const BASE = '/api'

export async function parseResume(file: File): Promise<any> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/parse-resume`, { method: 'POST', body: form })
  if (!res.ok) throw new Error((await res.json()).error || 'Parse failed')
  return res.json()
}

export async function atsScore(resumeText: string, jobDescription: string): Promise<any> {
  const res = await fetch(`${BASE}/ats-score`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume_text: resumeText, job_description: jobDescription })
  })
  if (!res.ok) throw new Error((await res.json()).error || 'ATS score failed')
  return res.json()
}

export async function* roastStream(resumeText: string, personality: string): AsyncGenerator<any> {
  const res = await fetch(`${BASE}/roast`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume_text: resumeText, personality })
  })
  if (!res.ok) throw new Error('Roast request failed')
  const reader = res.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6))
          yield data
        } catch {}
      }
    }
  }
}

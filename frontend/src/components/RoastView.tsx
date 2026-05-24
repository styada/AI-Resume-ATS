import { useEffect, useRef, useState } from 'react'
import { roastStream } from '../api/client'
import type { CritiqueItem, Personality } from '../types'
import CritiqueCard from './CritiqueCard'
import PersonalitySelector from './PersonalitySelector'

interface Props {
  resumeText: string
  personality: Personality
  onPersonalityChange: (p: Personality) => void
}

function SkeletonCard() {
  return (
    <div className="bg-zinc-900 rounded-xl border-l-4 border-l-zinc-700 p-5 animate-pulse space-y-3">
      <div className="h-3 bg-zinc-800 rounded w-1/4" />
      <div className="h-3 bg-zinc-800 rounded w-3/4" />
      <div className="h-3 bg-zinc-800 rounded w-1/2" />
    </div>
  )
}

/** Full roast panel with progressive critique reveal */
export default function RoastView({ resumeText, personality, onPersonalityChange }: Props) {
  const [critiques, setCritiques] = useState<CritiqueItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [visibleCount, setVisibleCount] = useState(0)
  const abortRef = useRef<boolean>(false)

  async function fetchRoast() {
    abortRef.current = false
    setCritiques([])
    setVisibleCount(0)
    setLoading(true)
    setError(null)
    try {
      let idx = 0
      for await (const item of roastStream(resumeText, personality)) {
        if (abortRef.current) break
        setCritiques((prev) => [...prev, item])
        const capturedIdx = idx
        setTimeout(() => setVisibleCount((c) => Math.max(c, capturedIdx + 1)), capturedIdx * 200)
        idx++
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRoast()
    return () => { abortRef.current = true }
  }, [personality]) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="space-y-4">
      <PersonalitySelector value={personality} onChange={onPersonalityChange} disabled={loading} />

      {error && (
        <div className="bg-red-950 border border-red-800 rounded-xl p-4 text-red-300 flex items-center justify-between">
          <span>{error}</span>
          <button
            onClick={fetchRoast}
            className="ml-4 px-3 py-1 bg-red-800 hover:bg-red-700 rounded-lg text-sm font-medium transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {loading && critiques.length === 0 && (
        <div className="space-y-3">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      )}

      {critiques.map((c, i) => (
        <CritiqueCard key={i} critique={c} index={i} visible={i < visibleCount} />
      ))}
    </div>
  )
}

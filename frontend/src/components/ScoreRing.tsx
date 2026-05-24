import { useEffect, useState } from 'react'

interface Props {
  score: number
  size?: number
}

/** Circular SVG score ring with animated fill */
export default function ScoreRing({ score, size = 140 }: Props) {
  const [animated, setAnimated] = useState(false)
  const radius = (size - 20) / 2
  const circumference = 2 * Math.PI * radius
  const offset = animated ? circumference - (score / 100) * circumference : circumference

  const color =
    score >= 75 ? '#22c55e' :
    score >= 50 ? '#f59e0b' :
    '#ef4444'

  useEffect(() => {
    const id = setTimeout(() => setAnimated(true), 50)
    return () => clearTimeout(id)
  }, [score])

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#27272a"
          strokeWidth={10}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={10}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 0.8s ease' }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-3xl font-bold text-white">{score}</span>
        <span className="text-xs text-zinc-400">ATS Score</span>
      </div>
    </div>
  )
}

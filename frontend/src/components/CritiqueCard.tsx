import { Share2 } from 'lucide-react'
import type { CritiqueItem } from '../types'

interface Props {
  critique: CritiqueItem
  index: number
  visible: boolean
}

const severityBorder: Record<CritiqueItem['severity'], string> = {
  advisory: 'border-l-blue-500',
  significant: 'border-l-amber-500',
  critical: 'border-l-red-500',
}

const severityBadge: Record<CritiqueItem['severity'], string> = {
  advisory: 'bg-blue-900 text-blue-300',
  significant: 'bg-amber-900 text-amber-300',
  critical: 'bg-red-900 text-red-300',
}

/** Single animated critique card */
export default function CritiqueCard({ critique, visible }: Props) {
  return (
    <div
      className={`bg-zinc-900 rounded-xl border-l-4 ${severityBorder[critique.severity]} p-5 transition-all duration-200 ease-out
        ${visible ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-4'}
      `}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full capitalize ${severityBadge[critique.severity]}`}>
          {critique.severity}
        </span>
        <button
          onClick={() => alert('Share coming soon')}
          className="text-zinc-500 hover:text-zinc-300 transition-colors"
          aria-label="Share critique"
        >
          <Share2 size={16} />
        </button>
      </div>

      {/* Quote */}
      <blockquote className="border-l-2 border-zinc-600 pl-3 text-zinc-400 italic text-sm mb-4">
        "{critique.quote}"
      </blockquote>

      {/* Sections */}
      <div className="space-y-3 text-sm">
        <div>
          <span className="text-xs font-bold text-zinc-500 uppercase tracking-wider">WHY</span>
          <p className="text-zinc-300 mt-1">{critique.why}</p>
        </div>
        <div>
          <span className="text-xs font-bold text-zinc-500 uppercase tracking-wider">PSYCHOLOGY</span>
          <p className="text-zinc-300 mt-1">{critique.psychology}</p>
        </div>
        <div className="bg-green-950/30 border border-green-900/40 rounded-lg p-3">
          <span className="text-xs font-bold text-green-500 uppercase tracking-wider">REWRITE</span>
          <p className="text-zinc-200 mt-1">{critique.rewrite}</p>
        </div>
      </div>
    </div>
  )
}

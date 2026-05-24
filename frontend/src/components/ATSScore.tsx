import type { ATSResult } from '../types'
import ScoreRing from './ScoreRing'

interface Props {
  result: ATSResult
}

interface Bar {
  label: string
  value: number
  max: number
}

/** Full ATS scoring results panel */
export default function ATSScore({ result }: Props) {
  const bars: Bar[] = [
    { label: 'Keyword Match', value: result.breakdown.keyword_match, max: 40 },
    { label: 'Section Completeness', value: result.breakdown.section_completeness, max: 20 },
    { label: 'Formatting', value: result.breakdown.formatting_compliance, max: 20 },
    { label: 'Quantified Impact', value: result.breakdown.quantified_impact, max: 20 },
  ]

  return (
    <div className="bg-zinc-900 rounded-xl p-6 space-y-6">
      {/* Score ring */}
      <div className="flex justify-center">
        <ScoreRing score={result.total_score} />
      </div>

      {/* Breakdown bars */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider">Breakdown</h3>
        {bars.map((bar) => (
          <div key={bar.label}>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-zinc-300">{bar.label}</span>
              <span className="text-zinc-400">{bar.value} / {bar.max}</span>
            </div>
            <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 rounded-full transition-all duration-700"
                style={{ width: `${(bar.value / bar.max) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Missing keywords */}
      {result.missing_keywords.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider mb-2">Missing Keywords</h3>
          <div className="flex flex-wrap gap-2">
            {result.missing_keywords.map((kw) => (
              <span key={kw} className="px-2 py-1 rounded-md text-xs bg-red-950 text-red-400 border border-red-800">
                {kw}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Matched keywords */}
      {result.matched_keywords.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider mb-2">Matched Keywords</h3>
          <div className="flex flex-wrap gap-2">
            {result.matched_keywords.map((kw) => (
              <span key={kw} className="px-2 py-1 rounded-md text-xs bg-green-950 text-green-400 border border-green-800">
                {kw}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Suggestions */}
      {result.suggestions.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider mb-2">Suggestions</h3>
          <ol className="space-y-2">
            {result.suggestions.map((s, i) => (
              <li key={i} className="flex gap-3 bg-blue-950/40 border border-blue-900/50 rounded-lg px-4 py-3 text-sm text-zinc-300">
                <span className="text-blue-400 font-bold shrink-0">{i + 1}.</span>
                <span>{s}</span>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  )
}

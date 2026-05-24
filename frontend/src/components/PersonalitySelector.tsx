import type { Personality } from '../types'

interface Props {
  value: Personality
  onChange: (p: Personality) => void
  disabled: boolean
}

const PERSONALITIES: { value: Personality; label: string }[] = [
  { value: 'professional_recruiter', label: 'Corporate Recruiter' },
  { value: 'faang_hiring_manager', label: 'FAANG HM' },
  { value: 'startup_founder', label: 'Startup Founder' },
  { value: 'blunt_reviewer', label: 'Blunt Critic' },
  { value: 'technical_interviewer', label: 'Tech Interviewer' },
]

/** Horizontal scrollable personality selector */
export default function PersonalitySelector({ value, onChange, disabled }: Props) {
  return (
    <div className="overflow-x-auto">
      <div className="flex gap-2 min-w-max">
        {PERSONALITIES.map((p) => (
          <button
            key={p.value}
            disabled={disabled}
            onClick={() => onChange(p.value)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap
              ${value === p.value
                ? 'bg-blue-600 text-white'
                : 'bg-zinc-800 text-zinc-400 hover:text-white'
              }
              ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            {p.label}
          </button>
        ))}
      </div>
    </div>
  )
}

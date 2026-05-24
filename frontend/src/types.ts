export type Personality = 'professional_recruiter' | 'faang_hiring_manager' | 'startup_founder' | 'blunt_reviewer' | 'technical_interviewer'

export interface ATSBreakdown {
  keyword_match: number
  section_completeness: number
  formatting_compliance: number
  quantified_impact: number
}

export interface ATSResult {
  total_score: number
  breakdown: ATSBreakdown
  matched_keywords: string[]
  missing_keywords: string[]
  suggestions: string[]
}

export interface CritiqueItem {
  quote: string
  why: string
  psychology: string
  rewrite: string
  severity: 'advisory' | 'significant' | 'critical'
}

export interface ParsedResume {
  text: string
  name: string | null
  email: string | null
  phone: string | null
  linkedin: string | null
  sections: Record<string, string>
  missing_sections: string[]
}

import { useState } from 'react'
import { parseResume, atsScore } from './api/client'
import type { ATSResult, ParsedResume, Personality } from './types'
import ATSScore from './components/ATSScore'
import ResumeUpload from './components/ResumeUpload'
import RoastView from './components/RoastView'

type Tab = 'ats' | 'roast'

function EmptyState() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
      <div className="bg-zinc-900 rounded-xl p-6 border border-zinc-800">
        <h3 className="text-blue-400 font-semibold mb-3">ATS Score Mode</h3>
        <ul className="space-y-2 text-sm text-zinc-400 list-disc list-inside">
          <li>Keyword match against job description</li>
          <li>Section completeness analysis</li>
          <li>Formatting compliance check</li>
          <li>Quantified impact scoring</li>
          <li>Actionable improvement suggestions</li>
        </ul>
      </div>
      <div className="bg-zinc-900 rounded-xl p-6 border border-zinc-800">
        <h3 className="text-purple-400 font-semibold mb-3">Resume Roast Mode</h3>
        <ul className="space-y-2 text-sm text-zinc-400 list-disc list-inside">
          <li>Choose from 5 reviewer personalities</li>
          <li>Blunt, psychology-aware critique</li>
          <li>Line-by-line rewrites</li>
          <li>Progressive streaming reveal</li>
          <li>Shareable critique cards</li>
        </ul>
      </div>
    </div>
  )
}

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>('ats')
  const [parsedResume, setParsedResume] = useState<ParsedResume | null>(null)
  const [atsResult, setAtsResult] = useState<ATSResult | null>(null)
  const [jobDescription, setJobDescription] = useState('')
  const [personality, setPersonality] = useState<Personality>('blunt_reviewer')
  const [uploading, setUploading] = useState(false)
  const [atsLoading, setAtsLoading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)

  async function handleFileSelect(file: File) {
    setUploading(true)
    setUploadError(null)
    try {
      const result = await parseResume(file)
      setParsedResume(result)
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  async function handleAnalyze() {
    if (!parsedResume) return
    setAtsLoading(true)
    setAtsResult(null)
    try {
      const result = await atsScore(parsedResume.text, jobDescription)
      setAtsResult(result)
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setAtsLoading(false)
    }
  }

  return (
    <div className="bg-zinc-950 text-white min-h-screen">
      <div className="max-w-3xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6">
          <h1 className="text-2xl font-bold text-white">AI Resume ATS</h1>
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('ats')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors
                ${activeTab === 'ats' ? 'bg-blue-600 text-white' : 'bg-zinc-800 text-zinc-400 hover:text-white'}`}
            >
              ATS Score
            </button>
            <button
              onClick={() => setActiveTab('roast')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors
                ${activeTab === 'roast' ? 'bg-blue-600 text-white' : 'bg-zinc-800 text-zinc-400 hover:text-white'}`}
            >
              Resume Roast
            </button>
          </div>
        </div>

        {/* Upload zone */}
        <ResumeUpload onFileSelect={handleFileSelect} disabled={uploading} />

        {uploading && (
          <p className="text-zinc-400 text-sm mt-2 animate-pulse">Parsing resume...</p>
        )}
        {uploadError && (
          <p className="text-red-400 text-sm mt-2">{uploadError}</p>
        )}
        {parsedResume && (parsedResume.name || parsedResume.email) && (
          <div className="mt-2 text-sm text-zinc-400 flex gap-3 flex-wrap">
            {parsedResume.name && <span className="text-zinc-200 font-medium">{parsedResume.name}</span>}
            {parsedResume.email && <span>{parsedResume.email}</span>}
          </div>
        )}

        {/* Empty state */}
        {!parsedResume && !uploading && <EmptyState />}

        {/* Tab content */}
        {parsedResume && (
          <div className="mt-6">
            {activeTab === 'ats' && (
              <div className="space-y-4">
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the job description here..."
                  rows={6}
                  className="w-full bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-3 text-zinc-200 placeholder-zinc-600 text-sm resize-none focus:outline-none focus:border-blue-500 transition-colors"
                />
                <button
                  onClick={handleAnalyze}
                  disabled={atsLoading || !jobDescription.trim()}
                  className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-medium text-sm transition-colors"
                >
                  {atsLoading ? 'Analyzing...' : 'Analyze'}
                </button>
                {atsLoading && (
                  <div className="bg-zinc-900 rounded-xl p-6 animate-pulse space-y-4">
                    <div className="flex justify-center">
                      <div className="h-36 w-36 rounded-full bg-zinc-800" />
                    </div>
                    <div className="h-3 bg-zinc-800 rounded w-3/4 mx-auto" />
                    <div className="h-3 bg-zinc-800 rounded w-1/2 mx-auto" />
                  </div>
                )}
                {atsResult && !atsLoading && <ATSScore result={atsResult} />}
              </div>
            )}

            {activeTab === 'roast' && (
              <RoastView
                resumeText={parsedResume.text}
                personality={personality}
                onPersonalityChange={setPersonality}
              />
            )}
          </div>
        )}

        {parsedResume && !parsedResume.text && activeTab === 'roast' && (
          <p className="text-zinc-500 text-sm mt-6">Upload a resume above to get your roast</p>
        )}
      </div>
    </div>
  )
}

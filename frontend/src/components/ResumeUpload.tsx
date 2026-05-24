import { useRef, useState } from 'react'
import { Upload, CheckCircle } from 'lucide-react'

interface Props {
  onFileSelect: (file: File) => void
  disabled: boolean
}

/** Drop zone for PDF/DOCX resume upload */
export default function ResumeUpload({ onFileSelect, disabled }: Props) {
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const accept = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  ]

  function handleFile(file: File) {
    if (!accept.includes(file.type)) {
      setError('Only PDF or DOCX files are accepted.')
      return
    }
    setError(null)
    setSelectedFile(file.name)
    onFileSelect(file)
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault()
    setDragging(false)
    if (disabled) return
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  function onChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }

  return (
    <div
      onClick={() => !disabled && inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
      className={`cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition-colors
        bg-zinc-900
        ${dragging ? 'border-blue-400' : 'border-zinc-700 hover:border-blue-500'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
      `}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx"
        className="hidden"
        onChange={onChange}
        disabled={disabled}
      />
      {selectedFile ? (
        <div className="flex items-center justify-center gap-2 text-green-400">
          <CheckCircle size={20} />
          <span className="text-sm font-medium">{selectedFile}</span>
        </div>
      ) : (
        <>
          <Upload className="mx-auto mb-3 text-zinc-500" size={32} />
          <p className="text-zinc-300 font-medium">Drop your resume here</p>
          <p className="text-zinc-500 text-sm mt-1">PDF or DOCX · Click to browse</p>
        </>
      )}
      {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
    </div>
  )
}

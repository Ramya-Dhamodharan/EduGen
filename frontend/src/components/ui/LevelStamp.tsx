interface Props {
  level?: string
}

const LEVEL_COLORS: Record<string, string> = {
  beginner: 'border-ledger text-ledger',
  intermediate: 'border-amber text-amber',
  advanced: 'border-rust text-rust',
}

export default function LevelStamp({ level }: Props) {
  if (!level) return null
  const key = level.toLowerCase()
  const colorClasses = LEVEL_COLORS[key] || 'border-ledger text-ledger'

  return (
    <span
      className={`inline-block -rotate-6 border-2 ${colorClasses} rounded-sm px-2 py-0.5 font-mono text-[10px] uppercase tracking-widest opacity-80`}
    >
      {level}
    </span>
  )
}

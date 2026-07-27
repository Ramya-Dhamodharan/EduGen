export default function Loader({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="p-10 text-center font-mono text-sm text-ledger/60">
      {label}
    </div>
  )
}

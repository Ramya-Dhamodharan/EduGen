export default function ErrorNote({ message }: { message?: string }) {
  return (
    <div className="border-2 border-rust bg-rust/5 rounded-sm p-4 font-mono text-sm text-rust">
      {message || 'Something broke. Try again.'}
    </div>
  )
}

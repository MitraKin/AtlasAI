export function LoadingState({ text = 'Loading...' }: { text?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3">
      <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
      <p className="text-slate-500 text-sm">{text}</p>
    </div>
  )
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3 text-center">
      <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center text-red-500 text-xl">!</div>
      <p className="text-red-600 text-sm max-w-md">{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="mt-2 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors">
          Try Again
        </button>
      )}
    </div>
  )
}

export function EmptyState({ text, suggestion }: { text: string; suggestion?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3 text-center">
      <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 text-xl">?</div>
      <p className="text-slate-500 text-sm">{text}</p>
      {suggestion && <p className="text-slate-400 text-xs">{suggestion}</p>}
    </div>
  )
}

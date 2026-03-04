interface Props {
  stdout: string;
  stderr: string;
  executionTimeMs: number;
  error: string | null;
}

export function ExecutionInfo({ stdout, stderr, executionTimeMs, error }: Props) {
  return (
    <div className="space-y-2">
      {error && (
        <p className="text-xs text-[#D9381E] border border-[#D9381E] p-2" style={{ borderWidth: '1px' }}>
          {error}
        </p>
      )}

      <div className="flex items-center gap-3 text-[10px] text-[#666666] uppercase tracking-[0.1em]" style={{ fontFamily: 'var(--font-mono)' }}>
        <span>{(executionTimeMs / 1000).toFixed(1)}s</span>
      </div>

      {stdout && (
        <details className="text-xs">
          <summary className="cursor-pointer text-[#666666] uppercase tracking-[0.1em] text-[10px]">
            Stdout
          </summary>
          <pre
            className="mt-1 bg-[#0A0A0A] text-[#F2F2EC] p-2 max-h-32 overflow-auto text-[11px] leading-relaxed"
            style={{ fontFamily: 'var(--font-mono)' }}
          >
            {stdout}
          </pre>
        </details>
      )}

      {stderr && !error && (
        <details className="text-xs">
          <summary className="cursor-pointer text-[#D9381E] uppercase tracking-[0.1em] text-[10px]">
            Stderr
          </summary>
          <pre
            className="mt-1 bg-[#0A0A0A] text-[#D9381E] p-2 max-h-32 overflow-auto text-[11px] leading-relaxed"
            style={{ fontFamily: 'var(--font-mono)' }}
          >
            {stderr}
          </pre>
        </details>
      )}
    </div>
  );
}

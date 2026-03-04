import { useState } from "react";

interface Props {
  code: string;
}

export function CodeBlock({ code }: Props) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h4 className="text-[10px] uppercase tracking-[0.15em] text-[#666666]">Generated Code</h4>
        <button
          onClick={handleCopy}
          className="text-[10px] uppercase tracking-[0.1em] px-2 py-0.5 border border-[#0A0A0A] text-[#0A0A0A] hover:bg-[#0A0A0A] hover:text-[#F2F2EC] transition-colors"
          style={{ fontFamily: 'var(--font-mono)', borderWidth: '1px' }}
        >
          {copied ? "COPIED" : "COPY"}
        </button>
      </div>
      <pre
        className="text-[11px] bg-[#0A0A0A] text-green-400 p-3 overflow-auto max-h-64 leading-relaxed"
        style={{ fontFamily: 'var(--font-mono)' }}
      >
        {code}
      </pre>
    </div>
  );
}

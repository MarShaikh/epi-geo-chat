import { useState, type FormEvent } from "react";
import { useAppState } from "../../context/AppContext";

interface Props {
  onSend: (query: string) => void;
}

export function ChatInput({ onSend }: Props) {
  const [input, setInput] = useState("");
  const { isStreaming } = useAppState();

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isStreaming) return;
    onSend(trimmed);
    setInput("");
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-0 border-t border-[#0A0A0A] bg-[#F2F2EC]" style={{ borderWidth: '1.5px' }}>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask about geospatial data..."
        disabled={isStreaming}
        className="flex-1 px-3 py-2.5 bg-transparent text-sm focus:outline-none disabled:opacity-50"
        style={{ fontFamily: 'var(--font-mono)' }}
      />
      <button
        type="submit"
        disabled={isStreaming || !input.trim()}
        className="px-4 py-2.5 bg-[#0A0A0A] text-[#F2F2EC] text-[10px] uppercase tracking-[0.15em] hover:bg-[#D9381E] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        style={{ fontFamily: 'var(--font-mono)' }}
      >
        {isStreaming ? "..." : "SEND"}
      </button>
    </form>
  );
}

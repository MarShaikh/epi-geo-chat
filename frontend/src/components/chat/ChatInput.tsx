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
    <form onSubmit={handleSubmit} className="flex gap-2 p-3 border-t border-slate-200 bg-white">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask about geospatial data..."
        disabled={isStreaming}
        className="flex-1 px-3 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
      />
      <button
        type="submit"
        disabled={isStreaming || !input.trim()}
        className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed"
      >
        {isStreaming ? "..." : "Send"}
      </button>
    </form>
  );
}

import { useEffect, useRef } from "react";
import { useAppState } from "../../context/AppContext";
import { MessageBubble } from "./MessageBubble";

export function MessageList() {
  const { messages } = useAppState();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-3">
      {messages.length === 0 && (
        <div className="text-center text-slate-400 mt-12">
          <p className="text-lg font-medium mb-1">Welcome to Epi-Geo Chat</p>
          <p className="text-sm">Ask about geospatial climate data in Nigeria</p>
          <p className="text-xs mt-3 text-slate-300">
            Try: "Show me rainfall in Lagos for February 2024"
          </p>
        </div>
      )}
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}

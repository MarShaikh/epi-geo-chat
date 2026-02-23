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
        <div className="text-center mt-12">
          <h2 className="text-2xl mb-2" style={{ fontFamily: 'var(--font-serif)' }}>Epi-Geo Chat</h2>
          <p className="text-xs uppercase tracking-[0.15em] text-[#666666]">
            Geospatial climate data analysis for Nigeria
          </p>
          <div className="mt-6 inline-block">
            <p className="text-[10px] uppercase tracking-[0.1em] text-[#666666] mb-2">Try asking</p>
            <div className="border border-[#D9381E] px-4 py-2 text-xs text-[#D9381E] hover:bg-[#D9381E] hover:text-[#F2F2EC] transition-colors cursor-pointer" style={{ borderWidth: '1.5px' }}>
              "Show me rainfall in Lagos for February 2024"
            </div>
          </div>
        </div>
      )}
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}

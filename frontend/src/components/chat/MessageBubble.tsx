import Markdown from "react-markdown";
import type { Message } from "../../types/api";

interface Props {
  message: Message;
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3`}>
      <div
        className={`max-w-[85%] px-3 py-2 rounded-lg text-sm ${
          isUser
            ? "bg-blue-600 text-white rounded-br-sm"
            : "bg-slate-100 text-slate-800 rounded-bl-sm"
        }`}
      >
        {isUser ? (
          <p>{message.content}</p>
        ) : message.content ? (
          <div className="prose prose-sm max-w-none"><Markdown>{message.content}</Markdown></div>
        ) : (
          <span className="text-slate-400 italic">Thinking...</span>
        )}
      </div>
    </div>
  );
}

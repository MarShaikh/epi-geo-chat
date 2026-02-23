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
        className={`max-w-[85%] px-3 py-2 text-sm ${
          isUser
            ? "bg-[#0A0A0A] text-[#F2F2EC]"
            : "bg-transparent border-t border-[#0A0A0A] pt-3"
        }`}
        style={isUser ? {} : { borderWidth: '1px' }}
      >
        {isUser ? (
          <p>{message.content}</p>
        ) : message.content ? (
          <div className="prose prose-sm max-w-none"><Markdown>{message.content}</Markdown></div>
        ) : (
          <span className="text-[#666666] italic">Thinking...</span>
        )}
      </div>
    </div>
  );
}

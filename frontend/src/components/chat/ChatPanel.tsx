import { useChat } from "../../hooks/useChat";
import { AgentProgress } from "./AgentProgress";
import { ChatInput } from "./ChatInput";
import { MessageList } from "./MessageList";

export function ChatPanel() {
  const { sendQuery } = useChat();

  return (
    <div className="flex flex-col h-full">
      <MessageList />
      <AgentProgress />
      <ChatInput onSend={sendQuery} />
    </div>
  );
}

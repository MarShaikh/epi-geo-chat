import { useAppState } from "../../context/AppContext";

const AGENTS = [
  { key: "query_parser", label: "Parse Query", icon: "1" },
  { key: "geocoding", label: "Geocode & Time", icon: "2" },
  { key: "stac_coordinator", label: "STAC Search", icon: "3" },
  { key: "response_synthesizer", label: "Synthesize", icon: "4" },
];

export function AgentProgress() {
  const { currentStep, isStreaming } = useAppState();

  if (!isStreaming || currentStep === null) return null;

  return (
    <div className="flex items-center gap-1 px-3 py-2 bg-[#F2F2EC] border-t border-[#0A0A0A]" style={{ borderWidth: '1px' }}>
      {AGENTS.map((agent, i) => {
        const step = i + 1;
        const isActive = step === currentStep;
        const isDone = step < currentStep;

        return (
          <div key={agent.key} className="flex items-center gap-1">
            <div
              className={`w-6 h-6 flex items-center justify-center text-xs font-medium border border-[#0A0A0A] ${
                isDone
                  ? "bg-[#0A0A0A] text-[#F2F2EC]"
                  : isActive
                    ? "bg-[#D9381E] text-white"
                    : "bg-transparent text-[#666666]"
              }`}
              style={isActive ? { animation: 'pulse 2s ease-in-out infinite', borderWidth: '1.5px' } : { borderWidth: '1.5px' }}
            >
              {isDone ? "✓" : agent.icon}
            </div>
            <span className={`text-[10px] uppercase tracking-[0.05em] hidden sm:inline ${isActive ? "text-[#D9381E] font-medium" : "text-[#666666]"}`}>
              {agent.label}
            </span>
            {i < AGENTS.length - 1 && <div className="w-3 h-px bg-[#0A0A0A] mx-0.5" />}
          </div>
        );
      })}
    </div>
  );
}

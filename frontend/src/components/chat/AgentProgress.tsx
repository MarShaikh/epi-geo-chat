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
    <div className="flex items-center gap-1 px-3 py-2 bg-slate-50 border-t border-slate-200">
      {AGENTS.map((agent, i) => {
        const step = i + 1;
        const isActive = step === currentStep;
        const isDone = step < currentStep;

        return (
          <div key={agent.key} className="flex items-center gap-1">
            <div
              className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${
                isDone
                  ? "bg-green-500 text-white"
                  : isActive
                    ? "bg-blue-500 text-white animate-pulse"
                    : "bg-slate-200 text-slate-500"
              }`}
            >
              {isDone ? "\u2713" : agent.icon}
            </div>
            <span className={`text-xs hidden sm:inline ${isActive ? "text-blue-600 font-medium" : "text-slate-400"}`}>
              {agent.label}
            </span>
            {i < AGENTS.length - 1 && <div className="w-3 h-px bg-slate-300 mx-0.5" />}
          </div>
        );
      })}
    </div>
  );
}

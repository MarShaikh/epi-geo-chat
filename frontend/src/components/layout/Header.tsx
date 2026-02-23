import { useAppState, useAppDispatch, type AppMode } from "../../context/AppContext";

export function Header() {
  const { mode } = useAppState();
  const dispatch = useAppDispatch();

  const setMode = (m: AppMode) => dispatch({ type: "SET_MODE", mode: m });

  return (
    <header className="flex items-center justify-between px-4 py-2 bg-[#F2F2EC] border-b border-[#0A0A0A]" style={{ borderWidth: '1.5px' }}>
      <div className="flex items-center gap-3">
        <h1 className="text-lg tracking-tight" style={{ fontFamily: 'var(--font-serif)' }}>EPI-GEO</h1>
        <span className="text-[10px] uppercase tracking-[0.15em] text-[#666666]" style={{ fontFamily: 'var(--font-mono)' }}>Analytics</span>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex gap-0">
          <button
            onClick={() => setMode("chat")}
            className={`px-3 py-1 text-[10px] uppercase tracking-[0.1em] transition-colors border border-[#0A0A0A] ${
              mode === "chat"
                ? "bg-[#0A0A0A] text-[#F2F2EC]"
                : "bg-transparent text-[#0A0A0A] hover:bg-[#0A0A0A] hover:text-[#F2F2EC]"
            }`}
            style={{ fontFamily: 'var(--font-mono)', borderWidth: '1.5px' }}
          >
            01. Chat Interface
          </button>
          <button
            onClick={() => setMode("explorer")}
            className={`px-3 py-1 text-[10px] uppercase tracking-[0.1em] transition-colors border border-[#0A0A0A] -ml-[1.5px] ${
              mode === "explorer"
                ? "bg-[#0A0A0A] text-[#F2F2EC]"
                : "bg-transparent text-[#0A0A0A] hover:bg-[#0A0A0A] hover:text-[#F2F2EC]"
            }`}
            style={{ fontFamily: 'var(--font-mono)', borderWidth: '1.5px' }}
          >
            02. Data Explorer
          </button>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-500" style={{ animation: 'pulse 2s ease-in-out infinite' }} />
          <span className="text-[10px] uppercase tracking-[0.1em] text-[#666666]" style={{ fontFamily: 'var(--font-mono)' }}>System Online</span>
        </div>
      </div>
    </header>
  );
}

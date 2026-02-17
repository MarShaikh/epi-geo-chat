import { useAppState, useAppDispatch, type AppMode } from "../../context/AppContext";

export function Header() {
  const { mode } = useAppState();
  const dispatch = useAppDispatch();

  const setMode = (m: AppMode) => dispatch({ type: "SET_MODE", mode: m });

  return (
    <header className="flex items-center justify-between px-4 py-2 bg-slate-800 text-white border-b border-slate-700">
      <h1 className="text-lg font-semibold">Epi-Geo Chat</h1>
      <div className="flex gap-1">
        <button
          onClick={() => setMode("chat")}
          className={`px-3 py-1 text-xs rounded transition-colors ${
            mode === "chat"
              ? "bg-slate-600 text-white"
              : "text-slate-400 hover:text-white"
          }`}
        >
          Chat
        </button>
        <button
          onClick={() => setMode("explorer")}
          className={`px-3 py-1 text-xs rounded transition-colors ${
            mode === "explorer"
              ? "bg-purple-600 text-white"
              : "text-slate-400 hover:text-white"
          }`}
        >
          Explorer
        </button>
      </div>
    </header>
  );
}

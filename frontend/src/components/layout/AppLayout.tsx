import type { ReactNode } from "react";
import { useAppState } from "../../context/AppContext";

interface Props {
  chat: ReactNode;
  map: ReactNode;
  results: ReactNode;
  explorer: ReactNode;
}

export function AppLayout({ chat, map, results, explorer }: Props) {
  const { mode } = useAppState();

  if (mode === "explorer") {
    return (
      <div className="grid grid-cols-[360px_1fr] h-full max-md:grid-cols-1 max-md:grid-rows-[auto_1fr]">
        <aside className="border-r border-[#0A0A0A] overflow-hidden flex flex-col" style={{ borderWidth: '1.5px' }}>{explorer}</aside>
        <main className="overflow-hidden">{map}</main>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-[320px_1fr_360px] h-full max-md:grid-cols-1 max-md:grid-rows-[1fr_300px_auto]">
      <aside className="border-r border-[#0A0A0A] overflow-hidden flex flex-col" style={{ borderWidth: '1.5px' }}>{chat}</aside>
      <main className="overflow-hidden">{map}</main>
      <aside className="border-l border-[#0A0A0A] overflow-y-auto" style={{ borderWidth: '1.5px' }}>{results}</aside>
    </div>
  );
}

import type { ReactNode } from "react";

interface Props {
  chat: ReactNode;
  map: ReactNode;
  results: ReactNode;
}

export function AppLayout({ chat, map, results }: Props) {
  return (
    <div className="grid grid-cols-[320px_1fr_360px] h-full max-md:grid-cols-1 max-md:grid-rows-[1fr_300px_auto]">
      <aside className="border-r border-slate-200 overflow-hidden flex flex-col">{chat}</aside>
      <main className="overflow-hidden">{map}</main>
      <aside className="border-l border-slate-200 overflow-y-auto">{results}</aside>
    </div>
  );
}

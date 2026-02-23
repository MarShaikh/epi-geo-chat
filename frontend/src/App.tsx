import { AppProvider } from "./context/AppContext";
import { Header } from "./components/layout/Header";
import { AppLayout } from "./components/layout/AppLayout";
import { ChatPanel } from "./components/chat/ChatPanel";
import { MapPanel } from "./components/map/MapPanel";
import { ResultsPanel } from "./components/results/ResultsPanel";
import { ExplorerPanel } from "./components/explorer/ExplorerPanel";

function App() {
  return (
    <AppProvider>
      <div className="flex flex-col h-full bg-[#F2F2EC]">
        <Header />
        <AppLayout
          chat={<ChatPanel />}
          map={<MapPanel />}
          results={<ResultsPanel />}
          explorer={<ExplorerPanel />}
        />
      </div>
    </AppProvider>
  );
}

export default App;

import { useState } from "react";
import AddProfessional from "./components/AddProfessional";
import ProfessionalsList from "./components/ProfessionalsList";
import "./App.css";

const TABS = [
  { key: "list", label: "Professionals List" },
  { key: "add", label: "Add Professional" },
];

export default function App() {
  const [activeTab, setActiveTab] = useState("list");
  const [refreshKey, setRefreshKey] = useState(0);

  const handleCreated = () => {
    setRefreshKey((k) => k + 1);
    setActiveTab("list");
  };

  return (
    <div className="app">
      <header>
        <h1>Professionals Network</h1>
        <nav>
          {TABS.map((tab) => (
            <button
              key={tab.key}
              className={activeTab === tab.key ? "active" : ""}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </header>
      <main>
        {activeTab === "list" && <ProfessionalsList refreshKey={refreshKey} />}
        {activeTab === "add" && <AddProfessional onCreated={handleCreated} />}
      </main>
    </div>
  );
}

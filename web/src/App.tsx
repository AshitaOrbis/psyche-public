import { useState } from "react";
import { usePsycheStore } from "./state/store";
import { getAllInstruments, isAdaptiveInstrument } from "./instruments/registry";
import { TestRunner } from "./components/TestRunner";
import { AdaptiveTestRunner } from "./components/AdaptiveTestRunner";
import { ResultsViewer } from "./components/ResultsViewer";
import { ProfileDashboard } from "./components/ProfileDashboard";
import { getInstrumentsForTier, TIER_META, INSTRUMENT_CATEGORIES } from "./instruments/tiers";
import type { Tier } from "./instruments/types";

// Register instruments (side-effect imports)
import "./instruments/init";

type View = "instruments" | "dashboard";

function getInitialView(): View {
  return window.location.hash === "#dashboard" ? "dashboard" : "instruments";
}

const TIERS: Tier[] = ["lite", "standard", "heavy"];

export default function App() {
  const [view, setView] = useState<View>(getInitialView);
  const activeId = usePsycheStore((s) => s.activeInstrumentId);
  const results = usePsycheStore((s) => s.results);
  const sessions = usePsycheStore((s) => s.sessions);
  const startInstrument = usePsycheStore((s) => s.startInstrument);
  const resetInstrument = usePsycheStore((s) => s.resetInstrument);
  const exportData = usePsycheStore((s) => s.exportData);
  const importData = usePsycheStore((s) => s.importData);
  const selectedTier = usePsycheStore((s) => s.selectedTier);
  const setTier = usePsycheStore((s) => s.setTier);
  const storageError = usePsycheStore((s) => s.storageError);
  const storageBytes = usePsycheStore((s) => s.storageBytes);
  const clearStorageError = usePsycheStore((s) => s.clearStorageError);

  const allInstruments = getAllInstruments();
  const tierInstrumentIds = getInstrumentsForTier(selectedTier);
  const filteredInstruments = allInstruments.filter(({ instrument }) =>
    tierInstrumentIds.includes(instrument.id)
  );

  const setActiveInstrument = usePsycheStore((s) => s.setActiveInstrument);

  // Active test in progress — dispatch to appropriate runner
  if (activeId) {
    if (isAdaptiveInstrument(activeId)) {
      const itemBankUrl = activeId === "cat-big5"
        ? "/item-banks/big5-grm-params.json"
        : "/item-banks/hexaco-grm-params.json";
      const instrumentName = activeId === "cat-big5" ? "CAT Big Five" : "CAT HEXACO";
      return (
        <AdaptiveTestRunner
          instrumentId={activeId}
          instrumentName={instrumentName}
          itemBankUrl={itemBankUrl}
          onComplete={() => setActiveInstrument(null)}
          onExit={() => setActiveInstrument(null)}
        />
      );
    }
    return <TestRunner />;
  }

  // Profile Dashboard view
  if (view === "dashboard") {
    return (
      <div>
        <div style={{ maxWidth: 960, margin: "0 auto", padding: "1rem 2rem 0" }}>
          <button onClick={() => setView("instruments")} style={btnLink}>
            &larr; Back to Instruments
          </button>
        </div>
        <ProfileDashboard />
      </div>
    );
  }

  // Instruments view
  const handleExport = () => {
    const json = exportData();
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `psyche-data-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImport = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".json";
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {
        if (typeof reader.result === "string") {
          try {
            importData(reader.result);
            alert("Import complete.");
          } catch (err) {
            alert(`Import failed: ${err instanceof Error ? err.message : "unknown error"}`);
          }
        }
      };
      reader.onerror = () => alert("Import failed: could not read file.");
      reader.readAsText(file);
    };
    input.click();
  };

  // Group instruments by category
  const groupedInstruments = INSTRUMENT_CATEGORIES
    .map((cat) => ({
      name: cat.name,
      instruments: filteredInstruments.filter(({ instrument }) =>
        cat.instrumentIds.includes(instrument.id)
      ),
    }))
    .filter((group) => group.instruments.length > 0);

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: "2rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ marginBottom: "0.25rem" }}>Psyche</h1>
          <p style={{ color: "#6b7280", marginTop: 0 }}>
            Psychometric persona profiling framework
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button onClick={() => setView("dashboard")} style={btnPrimary}>
            Profile Dashboard
          </button>
          <button onClick={handleExport} style={btnSecondary}>
            Export JSON
          </button>
          <button onClick={handleImport} style={btnSecondary}>
            Import
          </button>
        </div>
      </div>

      {/* Storage health (psy-9): non-silent quota error + approximate usage */}
      {storageError && (
        <div
          role="alert"
          style={{
            margin: "1rem 0",
            padding: "0.75rem 1rem",
            background: "#fef2f2",
            border: "1px solid #fecaca",
            borderRadius: "0.375rem",
            color: "#991b1b",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: "1rem",
          }}
        >
          <span>{storageError}</span>
          <div style={{ display: "flex", gap: "0.5rem", flexShrink: 0 }}>
            <button onClick={handleExport} style={btnSecondary}>
              Export now
            </button>
            <button onClick={clearStorageError} style={btnLink}>
              Dismiss
            </button>
          </div>
        </div>
      )}
      {storageBytes > 0 && (
        <p style={{ fontSize: "0.75rem", color: "#9ca3af", margin: "0.5rem 0 0" }}>
          Browser storage used: ~{formatBytes(storageBytes)}
        </p>
      )}

      {/* Tier selector */}
      <div style={{ margin: "1rem 0", display: "flex", gap: "0.5rem", alignItems: "center" }}>
        <span style={{ fontSize: "0.875rem", color: "#6b7280", marginRight: "0.5rem" }}>Tier:</span>
        <div style={{ display: "flex", borderRadius: "0.375rem", border: "1px solid #d1d5db", overflow: "hidden" }}>
          {TIERS.map((tier) => {
            const meta = TIER_META[tier];
            const isActive = selectedTier === tier;
            return (
              <button
                key={tier}
                onClick={() => setTier(tier)}
                style={{
                  padding: "0.5rem 1rem",
                  background: isActive ? "#2563eb" : "transparent",
                  color: isActive ? "#fff" : "#374151",
                  border: "none",
                  borderRight: tier !== "heavy" ? "1px solid #d1d5db" : "none",
                  cursor: "pointer",
                  fontSize: "0.875rem",
                  fontWeight: isActive ? 600 : 400,
                }}
                title={`${meta.estimatedItems}, ${meta.estimatedTime}`}
              >
                {meta.label}
              </button>
            );
          })}
        </div>
        <span style={{ fontSize: "0.75rem", color: "#9ca3af", marginLeft: "0.5rem" }}>
          {TIER_META[selectedTier].estimatedItems} &middot; {TIER_META[selectedTier].estimatedTime}
        </span>
      </div>

      <h2>Instrument Battery</h2>
      {groupedInstruments.length === 0 ? (
        <p>No instruments registered yet.</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          {groupedInstruments.map((group) => (
            <div key={group.name}>
              <h3 style={{ fontSize: "0.875rem", color: "#6b7280", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.5rem" }}>
                {group.name}
              </h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                {group.instruments.map(({ instrument: inst }) => {
                  const session = sessions[inst.id];
                  const result = results[inst.id];
                  const status = result
                    ? "completed"
                    : session
                      ? "in-progress"
                      : "not-started";

                  // Check if a lower-tier version of this instrument was completed
                  const lowerTierNote = getLowerTierNote(inst.id, results);

                  return (
                    <div
                      key={inst.id}
                      style={{
                        padding: "1rem 1.5rem",
                        border: "1px solid #e5e7eb",
                        borderRadius: "0.5rem",
                        borderLeft: `4px solid ${
                          status === "completed"
                            ? "#10b981"
                            : status === "in-progress"
                              ? "#f59e0b"
                              : "#d1d5db"
                        }`,
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <div>
                          <strong>{inst.name}</strong>
                          <span style={{ color: "#9ca3af", marginLeft: "0.5rem" }}>
                            {inst.itemCount} items, ~{inst.estimatedMinutes} min
                          </span>
                        </div>
                        <div style={{ display: "flex", gap: "0.5rem" }}>
                          {status === "completed" && (
                            <button onClick={() => resetInstrument(inst.id)} style={btnSecondary}>
                              Retake
                            </button>
                          )}
                          {status !== "completed" && (
                            <button onClick={() => startInstrument(inst.id)} style={btnPrimary}>
                              {status === "in-progress" ? "Resume" : "Start"}
                            </button>
                          )}
                        </div>
                      </div>
                      <p style={{ fontSize: "0.875rem", color: "#6b7280", margin: "0.5rem 0 0" }}>
                        {inst.description}
                      </p>
                      {status === "in-progress" && session && (
                        <p style={{ fontSize: "0.75rem", color: "#f59e0b", margin: "0.25rem 0 0" }}>
                          {session.responses.length} of {inst.itemCount} answered
                        </p>
                      )}
                      {lowerTierNote && status === "not-started" && (
                        <p style={{ fontSize: "0.75rem", color: "#6366f1", margin: "0.25rem 0 0" }}>
                          {lowerTierNote}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Results section */}
      {Object.keys(results).length > 0 && (
        <div style={{ marginTop: "3rem" }}>
          <h2>Results</h2>
          {Object.values(results).map((result) => (
            <ResultsViewer key={result.instrumentId} result={result} />
          ))}
        </div>
      )}
    </div>
  );
}

/** Check if a lower-precision version of this instrument was completed */
function getLowerTierNote(
  instrumentId: string,
  results: Record<string, unknown>,
): string | null {
  const upgradePaths: Record<string, { from: string; label: string }[]> = {
    "ipip-neo-300": [{ from: "ipip-neo-60", label: "NEO-60 completed (Lite)" }],
    "ipip-neo-120": [{ from: "ipip-neo-60", label: "NEO-60 completed (Lite)" }],
    "hexaco-200": [{ from: "hexaco-60", label: "HEXACO-60 completed (Standard)" }],
    "grit-o": [{ from: "grit-s", label: "Grit-S completed" }],
    "bpns-21": [{ from: "bpns-9", label: "BPNS-9 completed" }],
    "levenson-ipc-24": [{ from: "loc-ie4", label: "IE-4 completed" }],
    "snyder-sm-25": [{ from: "self-monitoring-18", label: "SM-18 completed" }],
  };

  const paths = upgradePaths[instrumentId];
  if (!paths) return null;

  for (const { from, label } of paths) {
    if (results[from]) {
      return `${label} — take this for higher precision`;
    }
  }
  return null;
}

/** Human-readable byte size for the storage-usage indicator (psy-9). */
function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

const btnPrimary: React.CSSProperties = {
  padding: "0.5rem 1rem",
  background: "#2563eb",
  color: "#fff",
  border: "none",
  borderRadius: "0.375rem",
  cursor: "pointer",
  fontSize: "0.875rem",
  fontWeight: 500,
};

const btnSecondary: React.CSSProperties = {
  padding: "0.5rem 1rem",
  background: "transparent",
  color: "#374151",
  border: "1px solid #d1d5db",
  borderRadius: "0.375rem",
  cursor: "pointer",
  fontSize: "0.875rem",
};

const btnLink: React.CSSProperties = {
  padding: "0.25rem 0",
  background: "transparent",
  color: "#2563eb",
  border: "none",
  cursor: "pointer",
  fontSize: "0.875rem",
};

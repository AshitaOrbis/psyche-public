/**
 * AdaptiveTestRunner — CAT-based test runner.
 *
 * Fundamentally different from TestRunner:
 * - No fixed item sequence — next item selected dynamically by CATController
 * - Per-dimension flow: cycles through facets until SE threshold met
 * - Shows SE convergence bars instead of "X of Y"
 * - Real-time theta update after each response
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { usePsycheStore } from "../state/store";
import type { GRMItem } from "../scoring/grm-engine";
import {
  initCATSession,
  getNextItem,
  registerResponse,
  getCATProgress,
  validateCATBankOrThrow,
  DEFAULT_STOPPING,
  type CATSession,
} from "../scoring/cat-controller";
import { scoreAdaptive } from "../scoring/engine";
import { getInstrument } from "../instruments/registry";
import { TestItemDisplay } from "./TestItemDisplay";
import { AdaptiveProgress } from "./AdaptiveProgress";

interface AdaptiveTestRunnerProps {
  instrumentId: string;
  instrumentName: string;
  itemBankUrl: string;
  onComplete: () => void;
  onExit: () => void;
}

const LIKERT_LABELS = [
  "Very Inaccurate",
  "Moderately Inaccurate",
  "Neither",
  "Moderately Accurate",
  "Very Accurate",
];

export function AdaptiveTestRunner({
  instrumentId,
  instrumentName,
  itemBankUrl,
  onComplete,
  onExit,
}: AdaptiveTestRunnerProps) {
  const completeInstrument = usePsycheStore((s) => s.completeInstrument);
  const results = usePsycheStore((s) => s.results);

  const [itemBank, setItemBank] = useState<GRMItem[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const sessionRef = useRef<CATSession | null>(null);
  const [currentItem, setCurrentItem] = useState<{ item: GRMItem; dimensionId: string } | null>(null);
  const [progress, setProgress] = useState<ReturnType<typeof getCATProgress>>([]);
  const [totalItems, setTotalItems] = useState(0);

  // Load item bank
  useEffect(() => {
    fetch(itemBankUrl)
      .then((r) => {
        if (!r.ok) throw new Error(`Failed to load item bank: ${r.status}`);
        return r.json();
      })
      .then((data: GRMItem[]) => {
        // Hard gate: refuse to administer a CAT from an invalid item bank
        // (placeholder item text, bad IRT parameters). Theta estimates from
        // such a bank are not psychometrically meaningful.
        validateCATBankOrThrow(data);
        setItemBank(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [itemBankUrl]);

  // Initialize CAT session when item bank is loaded
  useEffect(() => {
    if (!itemBank || sessionRef.current) return;

    // Check for fixed-form scores to use as priors
    const fixedFormSourceIds = instrumentId === "cat-big5"
      ? ["ipip-neo-300", "ipip-neo-120"]
      : ["hexaco-200", "hexaco-60"];
    const fixedFormScores =
      results[fixedFormSourceIds[0]!]?.scores ?? results[fixedFormSourceIds[1]!]?.scores;

    // Exclude items already administered in completed fixed-form instruments,
    // so overlapping items in a real CAT bank are never re-administered.
    // (No-op for banks whose item IDs don't overlap with fixed forms.)
    const fixedFormItemIds = new Set<string>();
    for (const sourceId of fixedFormSourceIds) {
      if (!results[sourceId]) continue;
      const reg = getInstrument(sourceId);
      for (const item of reg?.instrument.items ?? []) {
        fixedFormItemIds.add(item.id);
      }
    }

    const session = initCATSession(
      instrumentId,
      itemBank,
      fixedFormScores,
      fixedFormItemIds.size > 0 ? fixedFormItemIds : undefined,
      DEFAULT_STOPPING,
    );
    sessionRef.current = session;

    // Get first item
    const next = getNextItem(session);
    if (next) {
      sessionRef.current = next.session;
    }
    setCurrentItem(next);
    setProgress(getCATProgress(sessionRef.current));
  }, [itemBank, instrumentId, results]);

  const handleResponse = useCallback(
    (value: number) => {
      if (!sessionRef.current || !itemBank || !currentItem) return;

      // Value is 1-5 for Likert, convert to 0-indexed category
      const category = value - 1;

      const updatedSession = registerResponse(
        sessionRef.current,
        currentItem.item.id,
        category,
        DEFAULT_STOPPING,
      );
      sessionRef.current = updatedSession;

      setTotalItems(updatedSession.totalItemsAdministered);
      setProgress(getCATProgress(updatedSession));

      // Get next item after brief delay
      setTimeout(() => {
        if (!sessionRef.current) return;

        if (sessionRef.current.complete) {
          // All dimensions measured — compute scores (include fixed-form for skipped dims)
          const currentResults = usePsycheStore.getState().results;
          const ffScores = instrumentId === "cat-big5"
            ? currentResults["ipip-neo-300"]?.scores ?? currentResults["ipip-neo-120"]?.scores
            : currentResults["hexaco-200"]?.scores ?? currentResults["hexaco-60"]?.scores;
          const result = scoreAdaptive(instrumentId, sessionRef.current, undefined, ffScores);
          completeInstrument(result);
          onComplete();
          return;
        }

        const next = getNextItem(sessionRef.current);
        if (next) {
          sessionRef.current = next.session;
        }
        setCurrentItem(next);

        if (!next) {
          // All dimensions exhausted — compute scores (include fixed-form for skipped dims)
          const currentResults = usePsycheStore.getState().results;
          const ffScores = instrumentId === "cat-big5"
            ? currentResults["ipip-neo-300"]?.scores ?? currentResults["ipip-neo-120"]?.scores
            : currentResults["hexaco-200"]?.scores ?? currentResults["hexaco-60"]?.scores;
          const result = scoreAdaptive(instrumentId, sessionRef.current, undefined, ffScores);
          completeInstrument(result);
          onComplete();
        }
      }, 200);
    },
    [itemBank, currentItem, instrumentId, completeInstrument, onComplete],
  );

  // Keyboard shortcuts for Likert (1-5)
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName === "INPUT" || target.tagName === "TEXTAREA") return;

      const key = parseInt(e.key);
      if (key >= 1 && key <= 5) {
        e.preventDefault();
        handleResponse(key);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [handleResponse]);

  if (loading) {
    return (
      <div style={{ maxWidth: 700, margin: "0 auto", padding: "2rem", textAlign: "center" }}>
        <h2>{instrumentName}</h2>
        <p>Loading adaptive item bank...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ maxWidth: 700, margin: "0 auto", padding: "2rem", textAlign: "center" }}>
        <h2>{instrumentName}</h2>
        <p style={{ color: "#dc2626" }}>Error: {error}</p>
        <button onClick={onExit} style={exitBtnStyle}>Back to Dashboard</button>
      </div>
    );
  }

  if (!currentItem) {
    return (
      <div style={{ maxWidth: 700, margin: "0 auto", padding: "2rem", textAlign: "center" }}>
        <h2>{instrumentName}</h2>
        <p>Adaptive assessment complete!</p>
        <button onClick={onExit} style={exitBtnStyle}>Back to Dashboard</button>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 700, margin: "0 auto", padding: "2rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2 style={{ margin: 0 }}>{instrumentName}</h2>
        <button onClick={onExit} style={exitBtnStyle}>Save & Exit</button>
      </div>

      <AdaptiveProgress
        dimensions={progress}
        targetSE={DEFAULT_STOPPING.seThreshold}
        totalItemsAdministered={totalItems}
        currentDimensionId={currentItem.dimensionId}
      />

      <div style={{
        fontSize: "0.75rem",
        color: "#9ca3af",
        textAlign: "center",
        marginBottom: "0.5rem",
      }}>
        Measuring: {currentItem.dimensionId}
      </div>

      <TestItemDisplay
        text={currentItem.item.text}
        responseType="likert"
        likertMin={1}
        likertMax={5}
        likertLabels={LIKERT_LABELS}
        selectedValue={null}
        onSelect={handleResponse}
      />

      <div style={{ textAlign: "center", fontSize: "0.75rem", color: "#9ca3af" }}>
        Press 1-5 or click to answer
      </div>
    </div>
  );
}

const exitBtnStyle: React.CSSProperties = {
  padding: "0.25rem 0.75rem",
  background: "transparent",
  border: "1px solid #d1d5db",
  borderRadius: "0.25rem",
  cursor: "pointer",
  fontSize: "0.875rem",
};

/**
 * Shared item display component for Likert and binary response widgets.
 * Used by both TestRunner (fixed-form) and AdaptiveTestRunner (CAT).
 */

import { LikertScale } from "./LikertScale";

interface TestItemDisplayProps {
  /** Item text to display */
  text: string;
  /** Response format */
  responseType: "likert" | "binary";
  /** Likert range (required for likert type) */
  likertMin?: number;
  likertMax?: number;
  likertLabels?: string[];
  /** Binary labels (required for binary type) */
  binaryLabels?: [string, string];
  /** Currently selected value (null if unanswered) */
  selectedValue: number | null;
  /** Callback when a response is selected */
  onSelect: (value: number) => void;
  /** Instruction text override */
  instruction?: string;
}

export function TestItemDisplay({
  text,
  responseType,
  likertMin = 1,
  likertMax = 5,
  likertLabels,
  binaryLabels = ["True", "False"],
  selectedValue,
  onSelect,
  instruction,
}: TestItemDisplayProps) {
  const defaultInstruction = responseType === "likert"
    ? "How accurately does this describe you?"
    : "Is this true or false for you?";

  return (
    <div style={{ textAlign: "center", padding: "2rem 1rem", marginBottom: "1.5rem" }}>
      <p style={{ fontSize: "0.875rem", color: "#6b7280", marginBottom: "0.5rem" }}>
        {instruction ?? defaultInstruction}
      </p>
      <p style={{ fontSize: "1.5rem", fontWeight: 500, margin: "1rem 0 2rem" }}>
        {text}
      </p>

      {responseType === "likert" && (
        <LikertScale
          min={likertMin}
          max={likertMax}
          labels={likertLabels ?? []}
          value={selectedValue}
          onChange={onSelect}
        />
      )}

      {responseType === "binary" && (
        <div style={{ display: "flex", gap: "1rem", justifyContent: "center" }}>
          {binaryLabels.map((label, idx) => {
            const btnValue = idx === 0 ? 1 : 0;
            const isSelected = selectedValue === btnValue;
            return (
              <button
                key={label}
                onClick={() => onSelect(btnValue)}
                style={{
                  padding: "1rem 2.5rem",
                  border: isSelected ? "2px solid #2563eb" : "2px solid #d1d5db",
                  borderRadius: "0.5rem",
                  background: isSelected ? "#2563eb" : "#fff",
                  color: isSelected ? "#fff" : "#374151",
                  cursor: "pointer",
                  fontSize: "1.125rem",
                  fontWeight: isSelected ? 600 : 400,
                  minWidth: "140px",
                  transition: "all 0.15s",
                }}
              >
                <div style={{ fontSize: "0.75rem", color: isSelected ? "#dbeafe" : "#9ca3af" }}>
                  {idx === 0 ? "T / 1" : "F / 2"}
                </div>
                <div>{label}</div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

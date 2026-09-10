/**
 * Adaptive progress display — shows SE convergence per dimension.
 *
 * Unlike fixed-form ProgressBar (X of Y items), this shows:
 * - Per-dimension theta estimates with confidence
 * - SE convergence bars (how close to stopping threshold)
 * - Checkmarks on completed dimensions
 */

interface DimensionProgress {
  dimensionId: string;
  theta: number;
  se: number;
  itemsAdministered: number;
  complete: boolean;
  percentile: number;
}

interface AdaptiveProgressProps {
  dimensions: DimensionProgress[];
  targetSE: number;
  totalItemsAdministered: number;
  currentDimensionId?: string;
}

export function AdaptiveProgress({
  dimensions,
  targetSE,
  totalItemsAdministered,
  currentDimensionId,
}: AdaptiveProgressProps) {
  const completedCount = dimensions.filter((d) => d.complete).length;

  return (
    <div style={{ marginBottom: "1.5rem" }}>
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        fontSize: "0.875rem",
        color: "#6b7280",
        marginBottom: "0.75rem",
      }}>
        <span>{completedCount}/{dimensions.length} facets measured</span>
        <span>{totalItemsAdministered} items administered</span>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(120px, 1fr))", gap: "0.5rem" }}>
        {dimensions.map((dim) => {
          const seProgress = Math.min(1, (1 - dim.se / Math.max(dim.se, targetSE * 3)));
          const isCurrent = dim.dimensionId === currentDimensionId;

          return (
            <div
              key={dim.dimensionId}
              style={{
                padding: "0.5rem",
                borderRadius: "0.375rem",
                border: isCurrent ? "2px solid #2563eb" : "1px solid #e5e7eb",
                background: dim.complete ? "#f0fdf4" : isCurrent ? "#eff6ff" : "#fff",
                fontSize: "0.75rem",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontWeight: 600 }}>{dim.dimensionId}</span>
                {dim.complete ? (
                  <span style={{ color: "#16a34a" }}>&#10003;</span>
                ) : (
                  <span style={{ color: "#9ca3af" }}>{dim.itemsAdministered} items</span>
                )}
              </div>

              {/* SE convergence bar */}
              <div style={{
                height: "4px",
                background: "#e5e7eb",
                borderRadius: "2px",
                marginTop: "0.25rem",
                overflow: "hidden",
              }}>
                <div style={{
                  height: "100%",
                  width: `${seProgress * 100}%`,
                  background: dim.complete ? "#16a34a" : "#2563eb",
                  borderRadius: "2px",
                  transition: "width 0.3s",
                }} />
              </div>

              {dim.itemsAdministered > 0 && (
                <div style={{ marginTop: "0.25rem", color: "#6b7280" }}>
                  SE: {dim.se.toFixed(2)} / {targetSE.toFixed(2)}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

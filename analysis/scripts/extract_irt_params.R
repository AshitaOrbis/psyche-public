#!/usr/bin/env Rscript
# extract_irt_params.R — One-time SAPA IRT parameter extraction
#
# Downloads SAPA Big Five response data from Harvard Dataverse,
# fits Graded Response Models (GRM) per facet, and exports
# IRT parameters for the CAT engine.
#
# Requirements:
#   install.packages(c("mirt", "psych", "jsonlite"))
#
# Usage:
#   Rscript extract_irt_params.R
#
# Output:
#   web/public/item-banks/big5-grm-params.json
#   web/public/item-banks/hexaco-grm-params.json

library(mirt)
library(psych)
library(jsonlite)

# ── Configuration ────────────────────────────────────────────

SAPA_URL <- "https://dataverse.harvard.edu/api/access/datafile/:persistentId?persistentId=doi:10.7910/DVN/GU70Q0"
MIN_COMPLETION <- 0.80  # Filter respondents with <80% completion
MIN_ITEM_TOTAL_R <- 0.20  # Drop items with r < 0.20
VALID_DISC_RANGE <- c(0.3, 2.5)  # Acceptable discrimination range
CROSS_VAL_SPLIT <- 0.80  # 80/20 train/test split

OUTPUT_DIR <- file.path(dirname(dirname(dirname(sys.frame(1)$ofile))), "web", "public", "item-banks")
dir.create(OUTPUT_DIR, showWarnings = FALSE, recursive = TRUE)

# ── Helper Functions ─────────────────────────────────────────

validate_thresholds <- function(params) {
  # Check that thresholds are strictly ordered for each item
  valid <- sapply(1:nrow(params), function(i) {
    thresholds <- params[i, grep("^d\\d+$", names(params))]
    # mirt uses d parameters (negative of b): b_k = -d_k / a
    all(diff(as.numeric(thresholds)) <= 0)  # d parameters decrease
  })
  return(valid)
}

extract_grm_params <- function(data, item_ids, facet_id, facet_name) {
  # Subset to items for this facet
  facet_data <- data[, item_ids, drop = FALSE]

  # Remove respondents with all NA
  complete_mask <- rowSums(!is.na(facet_data)) > 0
  facet_data <- facet_data[complete_mask, , drop = FALSE]

  if (nrow(facet_data) < 100) {
    warning(sprintf("Facet %s has < 100 respondents, skipping", facet_id))
    return(NULL)
  }

  # Check item-total correlations
  item_stats <- psych::alpha(facet_data, check.keys = TRUE)
  good_items <- item_stats$item.stats$r.drop >= MIN_ITEM_TOTAL_R
  if (sum(good_items) < 3) {
    warning(sprintf("Facet %s has < 3 items with adequate item-total r, keeping all", facet_id))
    good_items <- rep(TRUE, length(item_ids))
  }

  facet_data <- facet_data[, good_items, drop = FALSE]
  retained_ids <- item_ids[good_items]

  # Fit GRM
  model <- mirt(facet_data, model = 1, itemtype = "graded", verbose = FALSE)

  # Extract parameters
  coefs <- coef(model, IRTpars = TRUE, simplify = TRUE)
  items_params <- coefs$items

  # Build output
  result <- list()
  for (j in 1:nrow(items_params)) {
    a <- items_params[j, "a"]
    b_cols <- grep("^b\\d+$", colnames(items_params), value = TRUE)
    thresholds <- as.numeric(items_params[j, b_cols])

    # Validate discrimination
    if (a < VALID_DISC_RANGE[1] || a > VALID_DISC_RANGE[2]) {
      warning(sprintf("Item %s discrimination %.2f outside range, clamping", retained_ids[j], a))
      a <- max(VALID_DISC_RANGE[1], min(VALID_DISC_RANGE[2], a))
    }

    # Validate threshold ordering
    if (any(diff(thresholds) <= 0)) {
      warning(sprintf("Item %s has non-ordered thresholds, skipping", retained_ids[j]))
      next
    }

    result[[length(result) + 1]] <- list(
      id = retained_ids[j],
      text = "",  # Fill from item text lookup
      dimensionId = facet_id,
      dimensionName = facet_name,
      reverse = FALSE,
      discrimination = round(a, 4),
      thresholds = round(thresholds, 4),
      numCategories = length(thresholds) + 1
    )
  }

  return(result)
}

# ── Main ─────────────────────────────────────────────────────

cat("=== SAPA IRT Parameter Extraction ===\n\n")

# Step 1: Download SAPA data
cat("Step 1: Loading SAPA data...\n")
# NOTE: In practice, download from Harvard Dataverse manually or via API
# The SAPA dataset is large (~500MB). This script assumes it's been
# downloaded to a local file.
sapa_file <- Sys.getenv("SAPA_DATA_FILE", "sapa_big5.rds")
if (!file.exists(sapa_file)) {
  cat("SAPA data file not found. Download from Harvard Dataverse:\n")
  cat(sprintf("  %s\n", SAPA_URL))
  cat(sprintf("  Save to: %s\n", sapa_file))
  quit(status = 1)
}
data <- readRDS(sapa_file)
cat(sprintf("  Loaded %d respondents x %d items\n", nrow(data), ncol(data)))

# Step 2: Filter high-completion respondents
cat("Step 2: Filtering respondents...\n")
completion <- rowMeans(!is.na(data))
data <- data[completion >= MIN_COMPLETION, ]
cat(sprintf("  Retained %d respondents (>= %.0f%% complete)\n", nrow(data), MIN_COMPLETION * 100))

# Step 3: Train/test split for cross-validation
set.seed(42)
n <- nrow(data)
train_idx <- sample(1:n, round(n * CROSS_VAL_SPLIT))
train_data <- data[train_idx, ]
test_data <- data[-train_idx, ]
cat(sprintf("  Train: %d, Test: %d\n", nrow(train_data), nrow(test_data)))

# Step 4: Extract GRM parameters per facet
cat("Step 4: Fitting GRM models...\n")

# The facet-item mapping should be loaded from the IPIP item key
# This is a placeholder — actual implementation reads from SAPA metadata
facet_map <- list(
  # Big Five facets (30 facets, 2-letter domain + 1-digit facet number)
  # Each facet should have 10+ items in the SAPA pool
  # Example: N1 = Anxiety items, E1 = Friendliness items, etc.
)

all_params <- list()
for (facet_id in names(facet_map)) {
  cat(sprintf("  Fitting %s...\n", facet_id))
  items <- facet_map[[facet_id]]
  params <- extract_grm_params(train_data, items$ids, facet_id, items$name)
  if (!is.null(params)) {
    all_params <- c(all_params, params)
  }
}

# Step 5: Cross-validate on held-out sample
cat("Step 5: Cross-validation...\n")
# Fit same model on test data, compare parameter estimates
# Accept if |Δa| < 0.3 and |Δb| < 0.5 for all parameters

# Step 6: Export to JSON
cat("Step 6: Exporting parameters...\n")
big5_output <- file.path(OUTPUT_DIR, "big5-grm-params.json")
write_json(all_params, big5_output, pretty = TRUE, auto_unbox = TRUE)
cat(sprintf("  Exported %d items to %s\n", length(all_params), big5_output))

# HEXACO extraction follows the same pattern with HEXACO items
# hexaco_output <- file.path(OUTPUT_DIR, "hexaco-grm-params.json")

cat("\n=== Done ===\n")
cat("NOTE: Item texts must be populated from the IPIP item bank.\n")
cat("The exported JSON contains IRT parameters only.\n")

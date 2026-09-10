/**
 * psy-9: localStorage quota handling + text-cap-on-write tests.
 */
import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import {
  usePsycheStore,
  MAX_TEXT_RESPONSE_LENGTH,
  STORE_KEY,
} from "../src/state/store";

// Register the full battery so "open-ended" (text responses) exists.
import "../src/instruments/init";

describe("psy-9: text response cap on write", () => {
  beforeEach(() => {
    localStorage.clear();
    usePsycheStore.setState({
      sessions: {},
      results: {},
      activeInstrumentId: null,
      currentItemIndex: 0,
      storageError: null,
      storageBytes: 0,
    });
  });

  it("truncates over-long text responses when recorded", () => {
    const store = usePsycheStore.getState();
    store.startInstrument("open-ended");
    const huge = "z".repeat(MAX_TEXT_RESPONSE_LENGTH + 5000);
    store.recordResponse({ itemId: "open-1", value: huge, timestamp: Date.now() });

    const session = usePsycheStore.getState().sessions["open-ended"];
    const recorded = session.responses.find((r) => r.itemId === "open-1");
    expect(typeof recorded?.value).toBe("string");
    expect((recorded!.value as string).length).toBe(MAX_TEXT_RESPONSE_LENGTH);
  });

  it("leaves in-bounds text responses unchanged", () => {
    const store = usePsycheStore.getState();
    store.startInstrument("open-ended");
    const text = "A perfectly reasonable answer.";
    store.recordResponse({ itemId: "open-2", value: text, timestamp: Date.now() });

    const session = usePsycheStore.getState().sessions["open-ended"];
    const recorded = session.responses.find((r) => r.itemId === "open-2");
    expect(recorded?.value).toBe(text);
  });
});

describe("psy-9: quota-aware storage adapter", () => {
  beforeEach(() => {
    localStorage.clear();
    usePsycheStore.setState({ storageError: null, storageBytes: 0 });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("surfaces QuotaExceededError to state instead of silently failing", () => {
    const spy = vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      const err = new DOMException("quota", "QuotaExceededError");
      throw err;
    });

    // Any state change triggers persist → setItem → throws. zustand/persist
    // catches the re-thrown error; our adapter has already set storageError.
    usePsycheStore.getState().setTier("heavy");

    expect(spy).toHaveBeenCalled();
    const err = usePsycheStore.getState().storageError;
    expect(err).toBeTruthy();
    expect(err).toMatch(/storage is full/i);
  });

  it("records approximate byte usage and clears error on a successful write", () => {
    // Seed an error, then a healthy write should clear it and set bytes.
    usePsycheStore.setState({ storageError: "stale error" });
    usePsycheStore.getState().setTier("lite");

    const state = usePsycheStore.getState();
    expect(state.storageError).toBeNull();
    expect(state.storageBytes).toBeGreaterThan(0);
    // The persisted blob actually landed in localStorage under STORE_KEY.
    expect(localStorage.getItem(STORE_KEY)).toBeTruthy();
  });

  it("clearStorageError resets the banner", () => {
    usePsycheStore.setState({ storageError: "Browser storage is full." });
    usePsycheStore.getState().clearStorageError();
    expect(usePsycheStore.getState().storageError).toBeNull();
  });

  it("does not persist transient storage-health fields", () => {
    usePsycheStore.getState().setTier("standard");
    const blob = localStorage.getItem(STORE_KEY);
    expect(blob).toBeTruthy();
    const parsed = JSON.parse(blob!);
    // partialize keeps only durable fields in the persisted state.
    expect(parsed.state).toBeDefined();
    expect(parsed.state.storageError).toBeUndefined();
    expect(parsed.state.storageBytes).toBeUndefined();
    expect(parsed.state.selectedTier).toBe("standard");
  });
});

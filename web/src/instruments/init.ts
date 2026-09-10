// Register ALL instruments via tier chain + Heavy-only additions.
// Lite and Standard instruments are registered by init-standard.ts (which chains init-lite.ts).
// Add new Heavy-only instruments below.

// Standard tier (includes Lite)
import "./init-standard";

// Heavy-only: upgraded instruments (replace Lite versions at registration time)
import "./ipip-neo-120";         // Replaces ipip-neo-60 item set (both registered, tiers.ts handles selection)
import "./hexaco-200";           // Heavy HEXACO
import "./grit-o";               // Heavy Grit (replaces grit-s)
import "./bpns-21";              // Heavy Needs (replaces bpns-9)
import "./levenson-ipc-24";      // Heavy LOC (replaces loc-ie4)
import "./snyder-sm-25";         // Heavy Self-Monitoring (replaces self-monitoring-18)
import "./phq9-gad7";            // Heavy/private ONLY: the full PHQ-9, including item 9.
                                 // Public tiers register phq8-gad7 instead (init-lite.ts), so
                                 // item 9's text never reaches a public bundle.

// Heavy-only: CAT adaptive instruments
import "./cat-big5";
import "./cat-hexaco";

// Heavy-only: Phase 6 extended battery
import "./aot-13";
import "./ius-12";
import "./scs-26";
import "./mfq-2";
import "./frost-mps";
import "./maas";
import "./authenticity";
import "./tangney-scs";
import "./maximization";
import "./ztpi";

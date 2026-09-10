# 🌍 Disaster Intelligence Platform — Project Roadmap

**Team:** Just us two 😂
**Project name:** Disaster Intelligence Platform (working name — pick a brand name whenever, it won't change the repo structure)
**Goal:** A disaster-risk intelligence system that predicts risk ahead of time (not just displays current state), with confidence scores and explainability — built hazard-by-hazard, starting with flood.
**Rule:** Check off a box only when it *actually runs*, not when it's "basically done."

---

## Why "flood first" doesn't mean "flood only"

We're building ONE architecture (ingestion → features → model → explainability → API → UI) that's hazard-agnostic by design. Flood is Phase 1's content because it has the best public data and fastest path to a real, backtested prediction. Wildfire/earthquake/storm get added later as new modules inside the same skeleton — no renaming, no rebuilding.

---

## Phase 0 — Setup & Scoping ✅ COMPLETE
- [x] Create folder structure
- [x] Set up Python virtual environment
- [x] Install base requirements (`requirements.txt`)
- [x] Pick the target region for the flood module → Bangladesh
- [x] Set up GitHub repo `disaster-intel-platform` + push initial skeleton (github.com/ArinolaDev/disaster-intel-platform)
- [ ] Pick a real brand name whenever inspiration strikes (doesn't block any code work — parked)

## Phase 1 — Flood Module: Data Ingestion
- [x] `ingestion/weather.py` — pull historical + forecast rainfall from Open-Meteo API (6 Bangladesh locations, 731 days historical + 168h forecast each — confirmed working)
- [ ] `ingestion/historical.py` — pull past flood events (EM-DAT / ReliefWeb / DFO Global Flood Database) for our region — this becomes our labels
- [ ] `ingestion/satellite.py` — (stretch) Sentinel Hub or NASA FIRMS pull for the region
- [x] Store raw pulls in `data/raw/flood/` as-is (never overwrite raw data)
- [ ] Write a data availability report — what date range, what resolution, what gaps

## Phase 2 — Geospatial Grid & Features
- [ ] `features/grid.py` — split region into H3 hexagons or lat/lon bins (hazard-agnostic, reused later)
- [ ] Pull elevation / drainage proxy per cell (DEM data, e.g. SRTM via OpenTopography)
- [ ] Pull population density per cell (WorldPop)
- [ ] `features/flood/engineer.py` — build feature table per cell per time window:
  - rainfall last 24h / 72h / 7d
  - rainfall intensity trend
  - elevation, slope
  - distance to nearest river
  - historical flood frequency in that cell
  - population exposed
- [ ] Join features to historical flood labels → build training dataset
- [ ] Exploratory notebook: sanity-check the joined dataset (`notebooks/01_flood_eda.ipynb`)

## Phase 3 — Flood Modeling
- [ ] Baseline model: XGBoost/LightGBM classifier → P(flood event in next 24h) per cell
- [ ] Train/test split by TIME, not randomly (never leak future into past)
- [ ] Evaluate: precision/recall, ROC-AUC, calibration curve (not just accuracy — imbalanced classes!)
- [ ] Stretch: LSTM/TFT on rainfall+water-level sequences for the time-series angle
- [ ] Save best model to `models_artifacts/flood/`
- [ ] Backtest against 2-3 real historical flood events — does it "predict" them if fed pre-event data?

## Phase 4 — Explainability Layer (hazard-agnostic)
- [ ] `explainability/shap_utils.py` — SHAP values per prediction, works for any hazard model
- [ ] Turn SHAP output into a plain-English reason string ("driven mainly by 72h rainfall + upstream saturation")
- [ ] Confidence score alongside every prediction (not just a raw probability — calibrated)

## Phase 5 — API (hazard-agnostic, hazard param on endpoints)
- [ ] FastAPI app (`api/main.py`) with endpoints:
  - [ ] `GET /risk/{hazard}/current` — current risk per grid cell for a given hazard
  - [ ] `GET /risk/{hazard}/cell/{id}` — detail + SHAP explanation for one cell
  - [ ] `POST /predict/{hazard}` — run prediction on-demand for a date/region
- [ ] Dockerize the API (stretch)
- [ ] Deploy somewhere free-tier (Render/Railway/Fly.io) once stable

## Phase 6 — Frontend
- [ ] Map UI (Mapbox or deck.gl) showing risk-colored grid cells, with a hazard selector even if only flood is live
- [ ] Click a cell → shows probability, confidence, "why" explanation
- [ ] Timeline slider (like SciFire's) to replay past predictions vs actual events
- [ ] Simple chatbot panel that answers questions by querying REAL model output (not generic LLM chat)

## Phase 7 — Polish & Story
- [ ] Write up the backtest results (this is your resume/portfolio proof — "predicted X of Y historical flood events with Z lead time")
- [ ] README with architecture diagram showing the full multi-hazard vision + "flood: implemented, others: planned"
- [ ] Demo video (2-3 min)
- [ ] Deploy live demo link
- [ ] Post/write-up for LinkedIn or portfolio site

## Phase 8 — Next Hazard Module (once flood is solid)
- [ ] Pick next hazard (wildfire is the strongest candidate — great public data via NASA FIRMS)
- [ ] Reuse ingestion/features/explainability/API skeleton, swap in hazard-specific logic
- [ ] Add to frontend hazard selector

---

## Decisions Log
*(update this every time we make a real choice, so we don't relitigate it later)*

- Project name: Disaster Intelligence Platform (generic, won't need renaming as hazards are added)
- First hazard module: Flood (chosen for data availability + tractability)
- Region: Bangladesh (Ganges-Brahmaputra-Meghna delta — best public flood data coverage globally, frequent well-documented events, strong validation sources via UNOSAT/DFO)
- Core model: XGBoost baseline, LSTM/TFT stretch
- Map library: TBD (Mapbox vs deck.gl)

## Parking Lot (ideas for later, not now)
- Wildfire spread module (Phase 8 candidate #1)
- Earthquake module
- Storm/extreme weather module
- Social media signal ingestion
- Multi-hazard fusion (combined risk score when hazards overlap)
- Mobile app
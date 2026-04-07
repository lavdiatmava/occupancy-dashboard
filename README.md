# 🏢 Occupancy Dashboard (COF Model)

## Overview

This project presents a **Building Occupancy Dashboard** powered by a custom
**Confidence-weighted Occupancy Fusion (COF)** model.

The goal is to estimate real occupancy levels by combining:

* Entry/Exit sensors (flow-based)
* Binary sensors (presence detection)
* Direct sensors (measured occupancy)

The solution integrates:

* Data cleaning & preprocessing
* Confidence scoring
* Kalman filtering for smoothing
* Interactive dashboard visualization

---

## Live Dashboard

https://dashboardpy-hpfu6btrb7s8jtxeg73qyj.streamlit.app/

---

## Key Results

### 1. Occupancy Levels

* Average occupancy remains relatively low (~13.5%), indicating **underutilization of spaces**
* Peak occupancy events are isolated rather than sustained

### 2. Sensor Confidence

* Average confidence is low (~0.15)
* This suggests **inconsistencies across sensor types**
* Results should be interpreted as **directional trends rather than exact counts**

### 3. Traffic vs Occupancy

* Weak correlation observed between traffic and occupancy
* Indicates that **movement does not always translate into sustained usage**

### 4. City Comparison

* Some cities show higher occupancy averages than others
* Variations suggest **different usage patterns or sensor reliability**

---

## Key Insights

* Buildings may be **underutilized**
* Sensor data quality is a **critical limitation**
* COF model helps stabilize noisy inputs but depends on input quality
* Opportunities exist to improve **sensor coverage and calibration**

---

## Methodology

### COF (Confidence-weighted Occupancy Fusion)

The model combines:

* **Kalman filtering** → smooths occupancy estimates
* **Confidence scoring** → weights sensor reliability
* **Normalization** → ensures comparable scale

Final metric:

* `COF Occupancy Rate (%) = normalized occupancy × confidence`

---

## Tech Stack

* Python (Pandas, NumPy)
* Streamlit (dashboard)
* Plotly (visualizations)
* GitHub (version control)
* Streamlit Cloud (deployment)

---

## Files

* `dashboard.py` → Streamlit app
* `cof_pipeline.py` → COF model logic
* `occupancy_cof.parquet` → processed dataset
* `requirements.txt` → dependencies

---

## Conclusion

This project demonstrates:

* Data engineering + analytics pipeline
* Custom metric design (COF)
* Real-time visualization
* Cloud deployment

---

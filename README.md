# 📦 Supply Chain Visibility System with Optimization Analytics



An enterprise-grade **Supply Chain Intelligence & Executive Control Tower** designed for real-time operational visibility, delivery performance diagnostics, supplier scorecards, and transportation cost optimization.

Developed as part of the **Infosys Springboard Virtual Internship** by **Team 5**.

---



---

## 🚀 Project Overview

In the consumer electronics retail distribution sector, fragmented data across regional warehouse hubs often causes stockouts, supplier delivery delays, and high freight expenses.

This project delivers a **centralized Executive Command Center** that simulates and optimizes the supply chain network for consumer electronics (Smartphones, Smartwatches, Headphones, and Accessories) across four major distribution hubs in India:
* 🏙️ **Delhi Warehouse** (North Hub)
* 🏙️ **Mumbai Warehouse** (West Hub)
* 🏙️ **Bangalore Warehouse** (South Hub)
* 🏙️ **Kolkata Warehouse** (East Hub)

---

## ⚡ How to Run This Project (Quick Start Guide)

Follow these simple steps to set up and run the dashboard locally on any computer:

### 📋 1. Prerequisites
* **Python 3.10 or higher** installed on your system ([Download Python](https://www.python.org/downloads/)).
* Terminal / Command Prompt (CMD) or VS Code.

---

### 📥 2. Step 1: Clone the Repository
Open your Terminal or Command Prompt and run:
```bash
git clone https://github.com/Ritika1210/Supplychain.git
cd Supplychain
```
### 📦 3. Step 2: Install Required Libraries
Install the required dependencies using pip:

bash


pip install streamlit pandas plotly numpy

### ▶️ 4. Step 3: Launch the Streamlit App
Run the following command in your terminal:

bash


streamlit run app.py
### 🌐 5. Access the Dashboard
Once launched, the dashboard will automatically open in your default web browser at: 👉 http://localhost:8501

(If it does not open automatically, copy and paste http://localhost:8501 into your Chrome/Edge browser).

### 🗂️ Dashboard Navigation & Features
Use the Left Sidebar to switch between dashboard pages:

### 📦 1. Inventory Analytics (Milestone 1):

Live stock tracking against Safety Stock and Reorder Points (ROP).
Inventory Asset Value and Carrying Holding Cost estimation.
Low-Stock Replenishment Action Grid with suggested reorder quantities.
### 🚚 2. Delivery & Operations (Milestone 2):

On-Time Delivery (OTD%) compliance against the 95% SLA target.
Monthly Lead Time trends vs. the 8-Day SLA benchmark.
Logistics Cost Savings Advisor: Recommends shifting non-urgent Air shipments to Road carriers.
### 📊 3. Executive Logistics Control (Milestone 3):

Supplier Composite Scorecards (Ranked / 100): Weighted by OTD, Quality, Speed, and Unit Cost.
Geographic Distribution Hubs Map: Interactive OpenStreetMap showing regional shipment volume.
### Fragile Electronics Optimization: Carrier damage audits and mode routing recommendations.
📈 4. Milestone 4 - Executive Summary:

CEO Financial Summary: Gadgets Sold, Gross Revenue, and Net Profit.
Product sales volume and profit margin leaderboards.
Transportation mode speed vs. cost efficiency comparison.
Automated CEO Strategic Risk & Action Plan.
### 👑 5. Final Dashboard (Power BI Style Control Tower):

A single-page, high-density executive command center bringing all 4 milestones into one unified view.
8-KPI Top Ribbon: Instant pulse of Revenue, Profit, Gadgets Sold, Orders, Lead Time, OTD%, Quality, and Inventory Health.
Interactive 4-Level Slicers: Drill down from Region ➔ Supplier ➔ Product ➔ Order ID with color-coded delivery status badges (🟢 On Time, 🟡 Moderate Delay, 🔴 Critical Delay).
### 📁 Repository Structure
text


├── app.py                     # Main Streamlit Dashboard Application
├── generate_data_std.py       # Data generation and standardization pipeline
├── inventory.csv              # Warehouse stock levels and safety thresholds
├── products.csv               # Product catalog, unit costs, and retail prices
├── supplier_orders.csv        # Purchase orders, delivery dates, and defect records
├── transportation.csv         # Shipping carriers, transit modes, costs, and distances
└── README.md                  # Comprehensive Project Documentation
### 🛠️ Architecture & Tech Stack
[Raw CSV Datasets] ➔ [Pandas ETL Pipeline] ➔ [Star Schema Modeling] ➔ [KPI & DAX Engine] ➔ [Streamlit Control Tower]
Frontend Framework: Streamlit
Data Processing & Analytics: Python, Pandas, NumPy
Interactive Visualizations: Plotly Express & Plotly Graph Objects (Gauges, Donut Charts, Grouped Bars)
Geospatial Intelligence: Plotly Scatter Mapbox & OpenStreetMap
❓ Troubleshooting
Port Already in Use: If port 8501 is busy, run:
```bash


streamlit run app.py --server.port 8502
```
Regenerate Clean Datasets: If you need to re-generate synthetic datasets:
bash


python generate_data_std.py
### 📜 License & Acknowledgements
Developed as part of the Infosys Springboard Virtual Internship.

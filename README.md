# 💧 AquaGuard AI
### Graph-Based Water Leakage Detection in Pipeline Networks

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)](https://streamlit.io)
[![NetworkX](https://img.shields.io/badge/NetworkX-3.3-green)](https://networkx.org)

---

## 🧠 What is AquaGuard AI?

AquaGuard AI models a pipeline network as a **directed graph** where:
- **Nodes** = Junctions (water distribution points)
- **Edges** = Pipes connecting junctions

Each pipe has an `expected_flow` and `actual_flow`. If the actual flow drops by more than **10%** below expected, AquaGuard flags that pipe as a **leak** and shows you exactly where it is.

---

## 📁 Project Structure

```
aquaguard/
├── app.py            # Streamlit UI (main app)
├── model.py          # Graph logic & leak detection
├── data.csv          # Sample pipeline dataset
├── requirements.txt  # Python dependencies
└── README.md
```

---

## ⚡ Run in 4 Steps

### Step 1 – Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/aquaguard-ai.git
cd aquaguard-ai
```

### Step 2 – Create virtual environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### Step 3 – Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 – Run the app
```bash
streamlit run app.py
```
Open your browser at **http://localhost:8501** 🎉

---

## 📊 CSV Format

Your CSV file must have these columns:

| pipe_id | from_node | to_node | expected_flow | actual_flow |
|---------|-----------|---------|---------------|-------------|
| P1      | A         | B       | 100           | 98          |
| P2      | B         | C       | 95            | 60          |

---

## 🔍 How Leak Detection Works

```
flow_loss  = expected_flow - actual_flow
loss_ratio = flow_loss / expected_flow

If loss_ratio > 10%  →  🚨 LEAK DETECTED
```

---

## 🛠️ Tech Stack

| Tool       | Purpose                         |
|------------|---------------------------------|
| Python     | Core programming language       |
| NetworkX   | Graph modeling of pipeline      |
| Streamlit  | Interactive web UI              |
| Pandas     | CSV data handling               |
| Matplotlib | Graph & chart visualization     |

---

## 🏆 Built for IIT Delhi Competition

AquaGuard AI demonstrates real-world graph analytics applied to infrastructure monitoring — a core problem in smart city and IoT domains.

---

*Made with 💧 by Vanshiv Garg


# app.py
# ─────────────────────────────────────────────────────────────────────────────
# AquaGuard AI – Main Streamlit Application
# Run with:  streamlit run app.py
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import io

# Import our own graph-logic module
from model import load_data, build_graph, detect_leaks, get_graph_summary

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AquaGuard AI",
    page_icon="💧",
    layout="wide"
)

# ── Custom CSS for a polished look ────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background: linear-gradient(135deg, #0a1628 0%, #0d2137 50%, #0a1628 100%); }

    /* Title styling */
    .main-title {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00d4ff, #0099cc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center;
        color: #7ecfed;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: rgba(0,180,255,0.08);
        border: 1px solid rgba(0,180,255,0.25);
        border-radius: 12px;
        padding: 1rem;
    }
    div[data-testid="metric-container"] label { color: #7ecfed !important; }
    div[data-testid="metric-container"] div   { color: #ffffff !important; }

    /* Section headers */
    .section-header {
        color: #00d4ff;
        font-size: 1.3rem;
        font-weight: 700;
        border-bottom: 2px solid rgba(0,212,255,0.3);
        padding-bottom: 0.3rem;
        margin: 1.5rem 0 1rem 0;
    }

    /* Leak alert box */
    .leak-alert {
        background: rgba(255,60,60,0.12);
        border: 1px solid rgba(255,80,80,0.5);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
    }
    .safe-alert {
        background: rgba(0,200,100,0.10);
        border: 1px solid rgba(0,200,100,0.4);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
    }
    /* DataFrame */
    .stDataFrame { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">💧 AquaGuard AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Graph-Based Water Leakage Detection in Pipeline Networks</div>',
    unsafe_allow_html=True
)

st.divider()


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR – File Upload
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/water.png", width=80)
    st.title("⚙️ Controls")
    st.markdown("---")

    uploaded_file = st.file_uploader(
        "📂 Upload Pipeline CSV",
        type=["csv"],
        help="CSV must have columns: pipe_id, from_node, to_node, expected_flow, actual_flow"
    )

    st.markdown("---")
    st.markdown("**Leak Detection Rule**")
    threshold_pct = st.slider(
        "Leak Threshold (%)", min_value=5, max_value=30, value=10, step=1,
        help="If flow drops by more than this %, it's flagged as a leak."
    )

    st.markdown("---")
    st.markdown("**About**")
    st.info(
        "AquaGuard AI models your pipeline network as a directed graph. "
        "Each pipe (edge) is checked for flow anomalies that indicate leakage."
    )


# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    # Use the default sample CSV if no file uploaded
    try:
        df = load_data("data.csv")
        st.info("ℹ️ Using default **data.csv**. Upload your own file in the sidebar.")
    except FileNotFoundError:
        st.error("❌ data.csv not found. Please upload a CSV file from the sidebar.")
        st.stop()

# Override threshold from slider
LEAK_THRESHOLD_OVERRIDE = threshold_pct / 100.0


# ─────────────────────────────────────────────────────────────────────────────
# BUILD GRAPH & DETECT LEAKS
# ─────────────────────────────────────────────────────────────────────────────
G       = build_graph(df)
summary = get_graph_summary(G)

# Re-run detection with user-selected threshold
import model as _model
_model.LEAK_THRESHOLD = LEAK_THRESHOLD_OVERRIDE
G2    = build_graph(df)
leaks = detect_leaks(G2)


# ─────────────────────────────────────────────────────────────────────────────
# TOP METRICS ROW
# ─────────────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("🔵 Total Junctions",  summary["total_nodes"])
c2.metric("🔗 Total Pipes",      summary["total_pipes"])
c3.metric("🚨 Leaks Detected",   len(leaks))
c4.metric(
    "✅ Safe Pipes",
    summary["total_pipes"] - len(leaks)
)


# ─────────────────────────────────────────────────────────────────────────────
# TWO COLUMNS – Left: Results  |  Right: Graph
# ─────────────────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1.4], gap="large")

# ── LEFT: Leak Results ────────────────────────────────────────────────────────
with left_col:
    st.markdown('<div class="section-header">🚨 Leak Detection Results</div>', unsafe_allow_html=True)

    if leaks:
        for leak in leaks:
            st.markdown(f"""
            <div class="leak-alert">
                <b>💧 Leak on Pipe {leak['pipe_id']}</b><br>
                📍 Location: <b>{leak['from_node']} → {leak['to_node']}</b><br>
                📉 Expected: <b>{leak['expected_flow']}</b> &nbsp;|&nbsp;
                   Actual: <b>{leak['actual_flow']}</b><br>
                🔴 Flow Lost: <b>{leak['flow_loss']} units ({leak['loss_pct']}%)</b>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="safe-alert">
            ✅ <b>No leaks detected!</b> All pipes are operating within safe flow limits.
        </div>
        """, unsafe_allow_html=True)

    # ── Raw Data Table ────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📋 Pipeline Data</div>', unsafe_allow_html=True)

    # Add a colour-coded status column
    df_display = df.copy()
    leak_pipes  = {l["pipe_id"] for l in leaks}
    df_display["Status"] = df_display["pipe_id"].apply(
        lambda pid: "🔴 LEAK" if pid in leak_pipes else "🟢 OK"
    )
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # Download button for leak report
    if leaks:
        leak_df = pd.DataFrame(leaks)
        csv_bytes = leak_df.to_csv(index=False).encode()
        st.download_button(
            "⬇️ Download Leak Report (CSV)",
            data=csv_bytes,
            file_name="leak_report.csv",
            mime="text/csv"
        )


# ── RIGHT: Graph Visualisation ────────────────────────────────────────────────
with right_col:
    st.markdown('<div class="section-header">🗺️ Pipeline Network Graph</div>', unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor("#0d2137")
    ax.set_facecolor("#0d2137")

    # Layout: spring layout gives a natural look
    pos = nx.spring_layout(G2, seed=42, k=1.8)

    # Separate edges into normal and leaking
    normal_edges = [(u, v) for u, v, d in G2.edges(data=True) if not d["leak_detected"]]
    leak_edges   = [(u, v) for u, v, d in G2.edges(data=True) if d["leak_detected"]]

    # Draw normal pipes (blue)
    nx.draw_networkx_edges(
        G2, pos, edgelist=normal_edges,
        edge_color="#00aaff", width=2.5,
        arrows=True, arrowsize=20,
        connectionstyle="arc3,rad=0.05",
        ax=ax
    )

    # Draw leaking pipes (red, thicker)
    nx.draw_networkx_edges(
        G2, pos, edgelist=leak_edges,
        edge_color="#ff4444", width=4,
        arrows=True, arrowsize=25,
        connectionstyle="arc3,rad=0.05",
        ax=ax
    )

    # Draw nodes
    nx.draw_networkx_nodes(
        G2, pos,
        node_color="#00d4ff", node_size=700,
        ax=ax, linewidths=2, edgecolors="#ffffff"
    )

    # Node labels
    nx.draw_networkx_labels(
        G2, pos,
        font_color="#0a1628", font_weight="bold", font_size=11, ax=ax
    )

    # Edge labels: show pipe_id
    edge_labels = {(u, v): d["pipe_id"] for u, v, d in G2.edges(data=True)}
    nx.draw_networkx_edge_labels(
        G2, pos, edge_labels=edge_labels,
        font_color="#cceeff", font_size=8, ax=ax,
        bbox=dict(boxstyle="round,pad=0.2", fc="#0d2137", ec="none", alpha=0.7)
    )

    # Legend
    legend_handles = [
        mpatches.Patch(color="#00aaff", label="Normal Pipe"),
        mpatches.Patch(color="#ff4444", label="Leaking Pipe"),
    ]
    ax.legend(handles=legend_handles, loc="upper left",
              facecolor="#0a1628", edgecolor="#00d4ff",
              labelcolor="white", fontsize=10)

    ax.set_title("Pipeline Network – AquaGuard AI", color="#00d4ff",
                 fontsize=14, fontweight="bold", pad=12)
    ax.axis("off")
    plt.tight_layout()

    st.pyplot(fig)

    # ── Bar Chart: expected vs actual flow ────────────────────────────────────
    st.markdown('<div class="section-header">📊 Flow Comparison per Pipe</div>', unsafe_allow_html=True)

    fig2, ax2 = plt.subplots(figsize=(8, 3.5))
    fig2.patch.set_facecolor("#0d2137")
    ax2.set_facecolor("#0d2137")

    x     = range(len(df))
    width = 0.38

    bars1 = ax2.bar([i - width/2 for i in x], df["expected_flow"],
                    width=width, color="#00aaff", label="Expected Flow", alpha=0.85)
    bars2 = ax2.bar([i + width/2 for i in x], df["actual_flow"],
                    width=width, color="#ff4444", label="Actual Flow", alpha=0.85)

    # Highlight leak bars
    for i, pid in enumerate(df["pipe_id"]):
        if pid in leak_pipes:
            bars2[i].set_edgecolor("#ffdd00")
            bars2[i].set_linewidth(2)

    ax2.set_xticks(list(x))
    ax2.set_xticklabels(df["pipe_id"], color="#cceeff", fontsize=9)
    ax2.set_ylabel("Flow (units)", color="#cceeff")
    ax2.tick_params(colors="#cceeff")
    ax2.spines[["top","right","left","bottom"]].set_color("#1e3a5f")
    ax2.legend(facecolor="#0a1628", edgecolor="#00d4ff", labelcolor="white", fontsize=9)
    ax2.set_title("Expected vs Actual Flow per Pipe", color="#00d4ff",
                  fontsize=12, fontweight="bold")

    plt.tight_layout()
    st.pyplot(fig2)


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<p style='text-align:center; color:#4a8fa8; font-size:0.85rem;'>"
    "AquaGuard AI &nbsp;|&nbsp; Graph-Based Pipeline Leak Detection &nbsp;|&nbsp; Built with NetworkX + Streamlit"
    "</p>",
    unsafe_allow_html=True
)

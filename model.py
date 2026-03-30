# model.py
# ─────────────────────────────────────────────────────────────────────────────
# AquaGuard AI – Graph Logic
# This file builds the pipeline network as a graph and detects water leaks.
# A "leak" is detected when actual_flow is much less than expected_flow.
# ─────────────────────────────────────────────────────────────────────────────

import networkx as nx   # For creating and managing graphs
import pandas as pd     # For reading CSV data


# ── Threshold ────────────────────────────────────────────────────────────────
# If actual_flow drops by more than LEAK_THRESHOLD % below expected_flow,
# we flag that pipe as a leak.
LEAK_THRESHOLD = 0.10   # 10 %


def load_data(filepath: str) -> pd.DataFrame:
    """
    Read the CSV file that contains pipe data.

    Each row describes one pipe:
        pipe_id | from_node | to_node | expected_flow | actual_flow

    Returns a pandas DataFrame.
    """
    df = pd.read_csv(filepath)
    return df


def build_graph(df: pd.DataFrame) -> nx.DiGraph:
    """
    Turn the DataFrame into a Directed Graph (DiGraph).

    • Nodes  → junctions / locations in the pipeline network
    • Edges  → pipes connecting two junctions

    Each edge carries three attributes:
        - pipe_id        : identifier of the pipe
        - expected_flow  : how much water *should* flow (litres/min, etc.)
        - actual_flow    : how much water *actually* flows
        - leak_detected  : True/False flag set later by detect_leaks()
    """
    G = nx.DiGraph()   # Directed graph (water flows one way)

    for _, row in df.iterrows():
        G.add_edge(
            row["from_node"],          # source junction
            row["to_node"],            # destination junction
            pipe_id=row["pipe_id"],
            expected_flow=float(row["expected_flow"]),
            actual_flow=float(row["actual_flow"]),
            leak_detected=False        # default – no leak
        )

    return G


def detect_leaks(G: nx.DiGraph) -> list[dict]:
    """
    Walk every edge in the graph and check whether flow has dropped.

    Rule:
        flow_loss  = expected_flow - actual_flow
        loss_ratio = flow_loss / expected_flow

        If loss_ratio > LEAK_THRESHOLD  →  LEAK DETECTED

    Returns a list of dictionaries, one per detected leak, e.g.:
        {
            "pipe_id"       : "P2",
            "from_node"     : "B",
            "to_node"       : "C",
            "expected_flow" : 95,
            "actual_flow"   : 60,
            "flow_loss"     : 35,
            "loss_pct"      : 36.84
        }
    """
    leaks = []

    for u, v, data in G.edges(data=True):          # u=from, v=to, data=attributes
        expected = data["expected_flow"]
        actual   = data["actual_flow"]
        loss     = expected - actual

        if expected > 0:                            # avoid division by zero
            loss_ratio = loss / expected
        else:
            loss_ratio = 0

        if loss_ratio > LEAK_THRESHOLD:             # threshold check
            data["leak_detected"] = True            # mark edge in graph

            leaks.append({
                "pipe_id"       : data["pipe_id"],
                "from_node"     : u,
                "to_node"       : v,
                "expected_flow" : expected,
                "actual_flow"   : actual,
                "flow_loss"     : round(loss, 2),
                "loss_pct"      : round(loss_ratio * 100, 2)
            })

    return leaks


def get_graph_summary(G: nx.DiGraph) -> dict:
    """
    Return basic statistics about the pipeline network.
    """
    return {
        "total_nodes" : G.number_of_nodes(),
        "total_pipes" : G.number_of_edges(),
        "node_list"   : list(G.nodes())
    }

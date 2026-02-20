# graph/conflict_graph.py — NetworkX graph builder + queries
import networkx as nx
import sqlite3
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import DB_PATH


def build_graph(db_path: str = None) -> nx.MultiDiGraph:
    """Build a NetworkX MultiDiGraph from entities and case_edges tables."""
    if db_path is None:
        db_path = DB_PATH

    G = nx.MultiDiGraph()
    conn = sqlite3.connect(db_path)

    # Add nodes from entities
    for row in conn.execute("SELECT id, name, type FROM entities"):
        G.add_node(row[0], label=row[1], entity_type=row[2], case_count=0)

    # Add edges from case_edges
    for row in conn.execute("SELECT case_id, entity_a, entity_b, edge_type FROM case_edges"):
        case_id, entity_a, entity_b, edge_type = row

        # Ensure nodes exist (even if not in entities table)
        if entity_a not in G:
            G.add_node(entity_a, label=entity_a, entity_type="unknown", case_count=0)
        if entity_b not in G:
            G.add_node(entity_b, label=entity_b, entity_type="unknown", case_count=0)

        G.add_edge(entity_a, entity_b, case_id=case_id, edge_type=edge_type)
        G.nodes[entity_a]["case_count"] = G.nodes[entity_a].get("case_count", 0) + 1
        G.nodes[entity_b]["case_count"] = G.nodes[entity_b].get("case_count", 0) + 1

    conn.close()
    return G


def detect_repeat_offenders(G: nx.MultiDiGraph, threshold: int = 3) -> list[dict]:
    """
    Find entities involved in more cases than the threshold.
    Returns sorted list by case_count descending.
    """
    offenders = [
        {
            "entity": n,
            "label": G.nodes[n].get("label", n),
            "case_count": G.nodes[n].get("case_count", 0),
            "entity_type": G.nodes[n].get("entity_type", "unknown"),
        }
        for n in G.nodes
        if G.nodes[n].get("case_count", 0) >= threshold
    ]
    return sorted(offenders, key=lambda x: x["case_count"], reverse=True)


def get_entity_history(G: nx.MultiDiGraph, entity_id: str) -> dict:
    """
    Get the full dispute history for an entity.
    Returns a dict with node_count, edge_count, and the subgraph.
    """
    if entity_id not in G:
        return {"node_count": 0, "edge_count": 0, "subgraph": nx.MultiDiGraph(), "edges": []}

    neighbors = list(set(list(G.neighbors(entity_id)) + list(G.predecessors(entity_id))))
    subgraph = G.subgraph([entity_id] + neighbors)

    edges = []
    for u, v, data in subgraph.edges(data=True):
        edges.append({
            "from": G.nodes[u].get("label", u),
            "to": G.nodes[v].get("label", v),
            "case_id": data.get("case_id", ""),
            "edge_type": data.get("edge_type", ""),
        })

    return {
        "node_count": subgraph.number_of_nodes(),
        "edge_count": subgraph.number_of_edges(),
        "subgraph": subgraph,
        "edges": edges,
    }


def detect_systematic_patterns(G: nx.MultiDiGraph) -> list[dict]:
    """
    Detect entities that have the same edge_type against different parties.
    Returns alerts for potential systematic filing patterns.
    """
    alerts = []
    for node in G.nodes:
        # Get all outgoing edges
        edge_types = {}
        for _, target, data in G.edges(node, data=True):
            etype = data.get("edge_type", "")
            if etype not in edge_types:
                edge_types[etype] = set()
            edge_types[etype].add(target)

        # Check for pattern: same edge type against 3+ different parties
        for etype, targets in edge_types.items():
            if len(targets) >= 3:
                alerts.append({
                    "entity": node,
                    "label": G.nodes[node].get("label", node),
                    "pattern": etype,
                    "target_count": len(targets),
                })

    return alerts

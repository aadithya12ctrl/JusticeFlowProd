# utils/seed_data.py — Demo data population script (India-contextualized)
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from db.database import (
    get_connection, init_db, insert_historical_case, insert_entity,
    insert_edge,
)


HISTORICAL_CASES = [
    # ─── Real Landmark Indian Cases ──────────────────────────────
    {
        "id": "LC-001", "summary": "Experion Developers Pvt. Ltd. vs Sushma Ashok Shiroor — Homebuyer challenged one-sided builder-buyer agreement after 4-year delay in flat possession. NCDRC directed refund with 9% interest. Supreme Court upheld consumer court's authority over RERA matters.",
        "category": "rera", "outcome": "SC upheld NCDRC order: Full refund with 9% p.a. interest to homebuyer. One-sided agreement clauses struck down. Consumer Protection Act and RERA held to operate harmoniously.",
        "dna_vector": [0.3, 0.95, 0.75, 0.9, 0.5, 0.4], "jurisdiction": "Supreme Court of India", "year": 2022,
    },
    {
        "id": "LC-002", "summary": "Indian Medical Association vs V.P. Shantha & Others — Whether medical services fall under Consumer Protection Act. Patients sought redress for negligence and deficiency in paid medical services.",
        "category": "consumer", "outcome": "SC held all paid medical services fall under Consumer Protection Act, 1986. Patients can seek redress for medical negligence through consumer forums. Landmark ruling expanding consumer rights.",
        "dna_vector": [0.6, 0.95, 0.5, 0.8, 0.4, 0.9], "jurisdiction": "Supreme Court of India", "year": 1995,
    },
    {
        "id": "LC-003", "summary": "Lucknow Development Authority vs M.K. Gupta — Homebuyer filed complaint against LDA for deficiency in service in construction and allotment of house. Question of whether government housing falls under CPA.",
        "category": "consumer", "outcome": "SC included housing construction by development authorities within 'services' under CPA. Government bodies held accountable. Compensation and corrective action ordered.",
        "dna_vector": [0.6, 0.9, 0.5, 0.7, 0.3, 0.8], "jurisdiction": "Supreme Court of India", "year": 1994,
    },
    {
        "id": "LC-004", "summary": "Sarla Verma & Ors vs Delhi Transport Corporation — Fatal motor accident case. Family of deceased sought enhanced compensation. Established standardized method for computing accident compensation.",
        "category": "motor_accident", "outcome": "SC established multiplier method for compensation based on age of deceased. Standardized heads of damages (loss of dependency, funeral expenses, consortium, estate). Foundational precedent for all MACT claims.",
        "dna_vector": [0.4, 0.95, 0.75, 0.85, 0.7, 0.8], "jurisdiction": "Supreme Court of India", "year": 2009,
    },
    {
        "id": "LC-005", "summary": "National Insurance Co. vs Pranay Sethi — Motor accident claim. Question on how to calculate future prospects addition for income of deceased in accident compensation cases.",
        "category": "motor_accident", "outcome": "SC fixed future prospects at 40% (below 40 yrs), 25% (40-50 yrs), 10% (above 50 yrs) for salaried. ₹15,000 for funeral, ₹15,000 for filial consortium, ₹40,000 for spousal consortium. Binding on all MACTs.",
        "dna_vector": [0.4, 0.9, 0.75, 0.9, 0.5, 0.7], "jurisdiction": "Supreme Court of India", "year": 2017,
    },
    {
        "id": "LC-006", "summary": "Satyawati Sharma vs Union of India — Challenged discriminatory provision in Delhi Rent Control Act that allowed landlord eviction only for residential but not commercial premises.",
        "category": "rent_control", "outcome": "SC struck down discriminatory DRC Act provision as violating Article 14. Landlords can seek eviction for both residential and commercial properties. Equalized tenant-landlord rights.",
        "dna_vector": [0.1, 0.95, 0.5, 0.85, 0.4, 0.9], "jurisdiction": "Supreme Court of India", "year": 2008,
    },
    {
        "id": "LC-007", "summary": "PUDR vs Union of India (Asiad Workers Case) — Public interest litigation challenging exploitation of Asiad construction workers paid below minimum wages. State argued no employer-employee relationship.",
        "category": "labour_industrial", "outcome": "SC expanded Article 23 (forced labour) to include payment below minimum wages. Payment less than minimum wage constitutes 'begar' (forced labour). Landmark expansion of fundamental rights for workers.",
        "dna_vector": [0.2, 0.95, 0.75, 0.85, 0.9, 0.95], "jurisdiction": "Supreme Court of India", "year": 1982,
    },
    {
        "id": "LC-008", "summary": "Cheque bounce case under NI Act §138. Business partner issued cheque of ₹15,00,000 that was dishonoured. Legal notice served, no payment within 15 days. Criminal complaint filed.",
        "category": "cheque_bounce", "outcome": "Accused convicted under NI Act §138. Ordered to pay cheque amount ₹15,00,000 with 9% interest, ₹1,00,000 compensation, ₹50,000 litigation costs. Karnataka HC upheld enhanced compensation of ₹22,10,000.",
        "dna_vector": [0.8, 0.9, 0.75, 0.9, 0.3, 0.2], "jurisdiction": "Karnataka High Court", "year": 2025,
    },
    {
        "id": "LC-009", "summary": "Ireo Grace Realtech vs Abhishek Khanna — Builder included one-sided clauses in buyer agreement. 5-year delay in handing over apartment. Buyer sought refund and compensation.",
        "category": "rera", "outcome": "SC held one-sided clauses in buyer agreements constitute unfair trade practice under CPA §2(1)(r). Buyer entitled to full refund with compensatory interest. Builder penalized.",
        "dna_vector": [0.3, 0.9, 0.75, 0.85, 0.6, 0.5], "jurisdiction": "Supreme Court of India", "year": 2021,
    },
    {
        "id": "LC-010", "summary": "DDA vs D.C. Sharma — Delhi Development Authority negligently allotted same plot to two different individuals. Second allottee discovered discrepancy after construction began.",
        "category": "consumer", "outcome": "NCDRC directed DDA to provide alternate plot or pay ₹30,00,000 for escalated market price. DDA held liable for gross negligence and deficiency in service.",
        "dna_vector": [0.6, 0.85, 0.75, 0.8, 0.5, 0.6], "jurisdiction": "NCDRC, New Delhi", "year": 2016,
    },
    {
        "id": "LC-011", "summary": "Mohd Ahmed Khan vs Shah Bano Begum — Divorced Muslim woman claimed maintenance under CrPC §125. Ex-husband argued Muslim personal law limits liability to iddat period only.",
        "category": "family_matrimonial", "outcome": "SC ruled Muslim women entitled to maintenance under CrPC §125 beyond iddat period. Landmark judgment on uniform civil code debate. Maintenance of ₹179.20/month ordered (1985). Led to Muslim Women (Protection of Rights) Act, 1986.",
        "dna_vector": [0.5, 0.95, 0.25, 0.7, 0.9, 0.95], "jurisdiction": "Supreme Court of India", "year": 1985,
    },
    {
        "id": "LC-012", "summary": "SC compensation for minor girl (age 7) who suffered 75% disability and moderate mental retardation after motor vehicle accident. Initial tribunal award of ₹5,90,750 challenged as grossly inadequate.",
        "category": "motor_accident", "outcome": "SC enhanced compensation from ₹5,90,750 to ₹50,80,000 considering 75% disability, mental retardation, future care needs, and loss of earning capacity for lifetime.",
        "dna_vector": [0.4, 0.95, 0.75, 0.9, 0.8, 0.6], "jurisdiction": "Supreme Court of India", "year": 2024,
    },
]

DEMO_ENTITIES = [
    # Real parties from landmark cases
    ("ENT-001", "Experion Developers Pvt. Ltd.", "company"),
    ("ENT-002", "Sushma Ashok Shiroor", "person"),
    ("ENT-003", "Indian Medical Association", "company"),
    ("ENT-004", "V.P. Shantha", "person"),
    ("ENT-005", "Lucknow Development Authority", "government"),
    ("ENT-006", "M.K. Gupta", "person"),
    ("ENT-007", "Sarla Verma", "person"),
    ("ENT-008", "Delhi Transport Corporation", "government"),
    ("ENT-009", "National Insurance Co. Ltd.", "company"),
    ("ENT-010", "Pranay Sethi", "person"),
    ("ENT-011", "Satyawati Sharma", "person"),
    ("ENT-012", "Union of India", "government"),
    ("ENT-013", "PUDR (People's Union for Democratic Rights)", "company"),
    ("ENT-014", "Ireo Grace Realtech Pvt. Ltd.", "company"),
    ("ENT-015", "Abhishek Khanna", "person"),
    ("ENT-016", "Delhi Development Authority", "government"),
    ("ENT-017", "D.C. Sharma", "person"),
    ("ENT-018", "Mohd Ahmed Khan", "person"),
    ("ENT-019", "Shah Bano Begum", "person"),
]

DEMO_EDGES = [
    # Experion vs Shiroor (RERA)
    ("LC-001", "ENT-002", "ENT-001", "plaintiff_vs_defendant"),
    # IMA vs V.P. Shantha (Consumer — medical services)
    ("LC-002", "ENT-004", "ENT-003", "plaintiff_vs_defendant"),
    # LDA vs M.K. Gupta (Consumer — govt housing)
    ("LC-003", "ENT-006", "ENT-005", "plaintiff_vs_defendant"),
    # Sarla Verma vs DTC (Motor Accident)
    ("LC-004", "ENT-007", "ENT-008", "plaintiff_vs_defendant"),
    # National Insurance vs Pranay Sethi (Motor Accident)
    ("LC-005", "ENT-010", "ENT-009", "plaintiff_vs_defendant"),
    # Satyawati Sharma vs UoI (Rent Control)
    ("LC-006", "ENT-011", "ENT-012", "plaintiff_vs_defendant"),
    # PUDR vs UoI (Labour — Asiad Workers)
    ("LC-007", "ENT-013", "ENT-012", "plaintiff_vs_defendant"),
    # Ireo Grace vs Abhishek Khanna (RERA)
    ("LC-009", "ENT-015", "ENT-014", "plaintiff_vs_defendant"),
    # DDA vs D.C. Sharma (Consumer)
    ("LC-010", "ENT-017", "ENT-016", "plaintiff_vs_defendant"),
    # Shah Bano case (Family)
    ("LC-011", "ENT-019", "ENT-018", "plaintiff_vs_defendant"),
    # Repeat pattern: Union of India in multiple cases (shows systemic litigation)
    ("LC-006", "ENT-011", "ENT-012", "settled"),
    ("LC-007", "ENT-013", "ENT-012", "settled"),
    # Govt bodies as repeat defendants
    ("LC-003", "ENT-006", "ENT-005", "settled"),
    ("LC-010", "ENT-017", "ENT-016", "settled"),
]


def seed_all():
    """Seed historical cases, demo entities, and edges into SQLite."""
    init_db()
    conn = get_connection()

    # Seed historical cases
    for case in HISTORICAL_CASES:
        insert_historical_case(
            case_id=case["id"],
            summary=case["summary"],
            category=case["category"],
            outcome=case["outcome"],
            dna_vector=case["dna_vector"],
            jurisdiction=case["jurisdiction"],
            year=case["year"],
        )

    # Seed entities
    for eid, name, etype in DEMO_ENTITIES:
        conn.execute(
            "INSERT OR IGNORE INTO entities (id, name, type) VALUES (?, ?, ?)",
            (eid, name, etype),
        )

    # Seed edges
    for case_id, ea, eb, etype in DEMO_EDGES:
        conn.execute(
            "INSERT OR IGNORE INTO case_edges (case_id, entity_a, entity_b, edge_type) VALUES (?, ?, ?, ?)",
            (case_id, ea, eb, etype),
        )

    conn.commit()
    conn.close()
    return len(HISTORICAL_CASES), len(DEMO_ENTITIES), len(DEMO_EDGES)


if __name__ == "__main__":
    cases, entities, edges = seed_all()
    print(f"Seeded {cases} historical cases, {entities} entities, {edges} edges.")

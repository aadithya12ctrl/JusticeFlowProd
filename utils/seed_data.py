# utils/seed_data.py — Demo data population script
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from db.database import (
    get_connection, init_db, insert_historical_case, insert_entity,
    insert_edge,
)


HISTORICAL_CASES = [
    {
        "id": "HC-001", "summary": "Tenant sued landlord for failure to repair heating system during winter months, causing health issues.",
        "category": "landlord_tenant", "outcome": "Awarded $8,400 to tenant. Landlord ordered to make repairs within 30 days.",
        "dna_vector": [0.1, 0.8, 0.5, 0.7, 0.6, 0.3], "jurisdiction": "Municipal Court", "year": 2023,
    },
    {
        "id": "HC-002", "summary": "Employee terminated without cause after 12 years. Claimed wrongful dismissal and unpaid severance.",
        "category": "employment", "outcome": "Settlement of $45,000. Employer required to provide neutral reference.",
        "dna_vector": [0.2, 0.7, 0.75, 0.8, 0.7, 0.4], "jurisdiction": "Superior Court", "year": 2023,
    },
    {
        "id": "HC-003", "summary": "Contractor failed to complete home renovation within agreed timeline. Homeowner seeks refund of $15,000 deposit.",
        "category": "contract", "outcome": "Contractor ordered to refund 70% of deposit ($10,500). Work partially credited.",
        "dna_vector": [0.3, 0.6, 0.5, 0.6, 0.4, 0.5], "jurisdiction": "Small Claims Court", "year": 2022,
    },
    {
        "id": "HC-004", "summary": "Car accident at intersection. Plaintiff sustained whiplash and missed 6 weeks of work.",
        "category": "personal_injury", "outcome": "Defendant found 80% at fault. Awarded $22,000 in damages.",
        "dna_vector": [0.4, 0.9, 0.5, 0.8, 0.5, 0.2], "jurisdiction": "District Court", "year": 2023,
    },
    {
        "id": "HC-005", "summary": "Custody dispute following divorce. Both parents seeking primary custody of two minor children.",
        "category": "family", "outcome": "Joint custody awarded. Primary residence with mother, visitation weekends for father.",
        "dna_vector": [0.5, 0.7, 0.25, 0.5, 0.9, 0.6], "jurisdiction": "Family Court", "year": 2022,
    },
    {
        "id": "HC-006", "summary": "Neighbor's tree fell on plaintiff's property, damaging roof and car valued at $4,500.",
        "category": "small_claims", "outcome": "Neighbor liable for damages. Awarded $4,200 after depreciation.",
        "dna_vector": [0.6, 0.8, 0.25, 0.9, 0.3, 0.2], "jurisdiction": "Small Claims Court", "year": 2024,
    },
    {
        "id": "HC-007", "summary": "Landlord refused to return security deposit despite property being left in good condition.",
        "category": "landlord_tenant", "outcome": "Landlord ordered to return full deposit of $2,800 plus $1,400 penalty.",
        "dna_vector": [0.1, 0.9, 0.25, 0.9, 0.5, 0.1], "jurisdiction": "Municipal Court", "year": 2024,
    },
    {
        "id": "HC-008", "summary": "Software company breached SLA agreement. Client lost $50,000 in revenue due to extended downtime.",
        "category": "contract", "outcome": "Partial liability found. Company ordered to pay $35,000 in damages.",
        "dna_vector": [0.3, 0.5, 0.75, 0.6, 0.3, 0.7], "jurisdiction": "Superior Court", "year": 2023,
    },
    {
        "id": "HC-009", "summary": "Employee harassed by supervisor over 8 months. Multiple HR complaints filed but not addressed.",
        "category": "employment", "outcome": "Company found liable. Awarded $65,000 in damages. Supervisor terminated.",
        "dna_vector": [0.2, 0.6, 0.75, 0.7, 0.9, 0.5], "jurisdiction": "Superior Court", "year": 2022,
    },
    {
        "id": "HC-010", "summary": "Slip and fall at grocery store due to unmarked wet floor. Plaintiff broke wrist.",
        "category": "personal_injury", "outcome": "Store found negligent. Awarded $12,500 for medical expenses and pain.",
        "dna_vector": [0.4, 0.8, 0.25, 0.7, 0.4, 0.3], "jurisdiction": "District Court", "year": 2024,
    },
    {
        "id": "HC-011", "summary": "Tenant organized rent strike due to months of unresolved mold issues affecting 12 units.",
        "category": "landlord_tenant", "outcome": "Landlord fined $25,000. Ordered to remediate mold within 60 days. Tenants awarded rent abatement.",
        "dna_vector": [0.1, 0.7, 0.5, 0.8, 0.8, 0.6], "jurisdiction": "Housing Court", "year": 2023,
    },
    {
        "id": "HC-012", "summary": "Freelance designer not paid for 3 months of completed work. Contract clearly states payment terms.",
        "category": "contract", "outcome": "Full payment of $9,600 ordered with 10% interest and attorney fees.",
        "dna_vector": [0.3, 0.8, 0.25, 0.9, 0.6, 0.2], "jurisdiction": "Small Claims Court", "year": 2024,
    },
]

DEMO_ENTITIES = [
    ("ENT-001", "Marcus Thompson", "person"),
    ("ENT-002", "Greenfield Properties LLC", "company"),
    ("ENT-003", "Sarah Chen", "person"),
    ("ENT-004", "TechCorp Industries", "company"),
    ("ENT-005", "James Rodriguez", "person"),
    ("ENT-006", "City Housing Authority", "government"),
    ("ENT-007", "Patricia Williams", "person"),
    ("ENT-008", "Downtown Realty Group", "company"),
    ("ENT-009", "David Kim", "person"),
    ("ENT-010", "Metro Contractors Inc", "company"),
]

DEMO_EDGES = [
    ("HC-001", "ENT-001", "ENT-002", "plaintiff_vs_defendant"),
    ("HC-002", "ENT-003", "ENT-004", "plaintiff_vs_defendant"),
    ("HC-003", "ENT-005", "ENT-010", "plaintiff_vs_defendant"),
    ("HC-007", "ENT-007", "ENT-008", "plaintiff_vs_defendant"),
    ("HC-011", "ENT-001", "ENT-002", "plaintiff_vs_defendant"),
    ("HC-011", "ENT-009", "ENT-002", "plaintiff_vs_defendant"),
    ("HC-012", "ENT-009", "ENT-004", "plaintiff_vs_defendant"),
    # Repeat offender edges — Greenfield Properties in multiple cases
    ("HC-001", "ENT-001", "ENT-002", "dismissed"),
    ("HC-007", "ENT-007", "ENT-002", "settled"),
    ("HC-011", "ENT-001", "ENT-002", "settled"),
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

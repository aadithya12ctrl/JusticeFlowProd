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
    {
        "id": "HC-001", "summary": "Tenant sued landlord for failure to repair water supply and sanitation in rented premises, causing health issues to family including minor children.",
        "category": "rent_control", "outcome": "Awarded ₹4,20,000 to tenant under Rent Control Act. Landlord ordered to make repairs within 30 days.",
        "dna_vector": [0.1, 0.8, 0.5, 0.7, 0.6, 0.3], "jurisdiction": "Rent Controller, Bangalore Urban", "year": 2023,
    },
    {
        "id": "HC-002", "summary": "Employee terminated without cause after 12 years of service. Claimed wrongful retrenchment under Industrial Disputes Act and unpaid gratuity under Payment of Gratuity Act, 1972.",
        "category": "labour_industrial", "outcome": "Settlement of ₹18,50,000. Employer ordered to pay full gratuity and issue experience certificate.",
        "dna_vector": [0.2, 0.7, 0.75, 0.8, 0.7, 0.4], "jurisdiction": "Labour Court, Karnataka", "year": 2023,
    },
    {
        "id": "HC-003", "summary": "Contractor failed to complete home renovation within agreed timeline under registered agreement. Homeowner seeks refund of ₹7,50,000 advance payment.",
        "category": "contract_civil", "outcome": "Contractor ordered to refund 70% of advance (₹5,25,000) under Indian Contract Act, 1872. Work partially credited.",
        "dna_vector": [0.3, 0.6, 0.5, 0.6, 0.4, 0.5], "jurisdiction": "Civil Court, Bangalore Urban", "year": 2022,
    },
    {
        "id": "HC-004", "summary": "Road accident at unregulated intersection. Claimant sustained fractures and missed 6 weeks of work. Filed claim before MACT.",
        "category": "motor_accident", "outcome": "Respondent found 80% at fault. Awarded ₹11,00,000 in compensation under Motor Vehicles Act, 1988 §166.",
        "dna_vector": [0.4, 0.9, 0.5, 0.8, 0.5, 0.2], "jurisdiction": "MACT, Bangalore Urban", "year": 2023,
    },
    {
        "id": "HC-005", "summary": "Custody dispute following divorce under Hindu Marriage Act. Both parents seeking primary custody of two minor children.",
        "category": "family_matrimonial", "outcome": "Joint custody awarded under Guardians and Wards Act, 1890. Primary residence with mother, visitation alternate weekends for father.",
        "dna_vector": [0.5, 0.7, 0.25, 0.5, 0.9, 0.6], "jurisdiction": "Family Court, Bangalore", "year": 2022,
    },
    {
        "id": "HC-006", "summary": "Defective washing machine delivered by e-commerce platform. Consumer filed complaint for product replacement and compensation under Consumer Protection Act, 2019.",
        "category": "consumer", "outcome": "Seller liable for deficiency of service. Awarded ₹75,000 replacement + ₹25,000 compensation under CPA 2019 §35.",
        "dna_vector": [0.6, 0.8, 0.25, 0.9, 0.3, 0.2], "jurisdiction": "District Consumer Forum, Bangalore Urban", "year": 2024,
    },
    {
        "id": "HC-007", "summary": "Landlord refused to return security deposit of ₹1,40,000 despite premises being left in original condition as per inventory.",
        "category": "rent_control", "outcome": "Landlord ordered to return full deposit of ₹1,40,000 plus ₹70,000 penalty under Karnataka Rent Act.",
        "dna_vector": [0.1, 0.9, 0.25, 0.9, 0.5, 0.1], "jurisdiction": "Rent Controller, Bangalore Urban", "year": 2024,
    },
    {
        "id": "HC-008", "summary": "IT services company breached SLA agreement. Client lost ₹25,00,000 in revenue due to extended server downtime affecting business operations.",
        "category": "contract_civil", "outcome": "Partial liability found under Indian Contract Act §73. Company ordered to pay ₹17,50,000 in damages.",
        "dna_vector": [0.3, 0.5, 0.75, 0.6, 0.3, 0.7], "jurisdiction": "Commercial Court, Bangalore", "year": 2023,
    },
    {
        "id": "HC-009", "summary": "Employee harassed by supervisor over 8 months at IT company. Multiple POSH Committee complaints filed but not addressed by management.",
        "category": "labour_industrial", "outcome": "Company found liable under POSH Act, 2013. Awarded ₹32,50,000 in damages. Supervisor terminated.",
        "dna_vector": [0.2, 0.6, 0.75, 0.7, 0.9, 0.5], "jurisdiction": "Labour Court, Karnataka", "year": 2022,
    },
    {
        "id": "HC-010", "summary": "Slip and fall at shopping mall due to unmarked wet floor. Complainant fractured wrist and filed claim for medical expenses.",
        "category": "consumer", "outcome": "Mall management found negligent under CPA 2019. Awarded ₹3,25,000 for medical expenses and mental agony.",
        "dna_vector": [0.4, 0.8, 0.25, 0.7, 0.4, 0.3], "jurisdiction": "District Consumer Forum, Bangalore Urban", "year": 2024,
    },
    {
        "id": "HC-011", "summary": "Tenants of 12-unit apartment organized collective complaint against landlord for unresolved seepage and mold issues affecting health.",
        "category": "rent_control", "outcome": "Landlord fined ₹12,50,000. Ordered to remediate issues within 60 days. Tenants awarded 3-month rent abatement.",
        "dna_vector": [0.1, 0.7, 0.5, 0.8, 0.8, 0.6], "jurisdiction": "Rent Controller, Bangalore Urban", "year": 2023,
    },
    {
        "id": "HC-012", "summary": "Freelance UI designer not paid for 3 months of completed work. Written contract clearly states payment terms and deliverables.",
        "category": "contract_civil", "outcome": "Full payment of ₹4,80,000 ordered with 18% interest under Indian Contract Act §73 and attorney fees.",
        "dna_vector": [0.3, 0.8, 0.25, 0.9, 0.6, 0.2], "jurisdiction": "Civil Court, Bangalore Urban", "year": 2024,
    },
    # Real Indian precedent
    {
        "id": "HC-013", "summary": "Homebuyer filed complaint against builder for 3-year delay in possession of RERA-registered flat. Builder cited COVID-19 force majeure. Based on Pioneer Urban Land vs Govindan Raghavan (2019) SC precedent.",
        "category": "rera", "outcome": "Builder ordered to refund full amount with 10% annual interest under RERA §18. Force majeure plea rejected as delay was pre-COVID. SC held buyer cannot be made to wait indefinitely.",
        "dna_vector": [0.3, 0.9, 0.75, 0.9, 0.6, 0.3], "jurisdiction": "K-RERA Authority, Bangalore", "year": 2024,
    },
]

DEMO_ENTITIES = [
    ("ENT-001", "Ramesh Gupta", "person"),
    ("ENT-002", "Greenfield Properties Pvt. Ltd.", "company"),
    ("ENT-003", "Priya Iyer", "person"),
    ("ENT-004", "TechCorp India Pvt. Ltd.", "company"),
    ("ENT-005", "Arjun Reddy", "person"),
    ("ENT-006", "BBMP (Bruhat Bengaluru Mahanagara Palike)", "government"),
    ("ENT-007", "Lakshmi Narayanan", "person"),
    ("ENT-008", "Downtown Realty Group Pvt. Ltd.", "company"),
    ("ENT-009", "Suresh Kumar", "person"),
    ("ENT-010", "Metro Contractors India Pvt. Ltd.", "company"),
]

DEMO_EDGES = [
    ("HC-001", "ENT-001", "ENT-002", "plaintiff_vs_defendant"),
    ("HC-002", "ENT-003", "ENT-004", "plaintiff_vs_defendant"),
    ("HC-003", "ENT-005", "ENT-010", "plaintiff_vs_defendant"),
    ("HC-007", "ENT-007", "ENT-008", "plaintiff_vs_defendant"),
    ("HC-011", "ENT-001", "ENT-002", "plaintiff_vs_defendant"),
    ("HC-011", "ENT-009", "ENT-002", "plaintiff_vs_defendant"),
    ("HC-012", "ENT-009", "ENT-004", "plaintiff_vs_defendant"),
    ("HC-013", "ENT-005", "ENT-002", "plaintiff_vs_defendant"),
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

-- schema.sql — JusticeFlow database tables

CREATE TABLE IF NOT EXISTS cases (
    id              TEXT PRIMARY KEY,       -- UUID
    title           TEXT NOT NULL,
    description     TEXT NOT NULL,
    category        TEXT,                   -- landlord-tenant, employment, contract, etc.
    jurisdiction    TEXT,
    claim_amount    REAL,
    plaintiff_id    TEXT,
    defendant_id    TEXT,
    status          TEXT DEFAULT 'intake',  -- intake, filtered, scored, negotiating, resolved, escalated, dismissed
    filed_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    dls_score       REAL,
    dls_reasons     TEXT,                   -- JSON array
    dna_vector      TEXT,                   -- JSON serialized float list
    emotional_temp  REAL,
    filter_result   TEXT,                   -- JSON: {passed, reason, routing}
    settlement_text TEXT,
    ai_outcome      TEXT,
    ai_confidence   REAL
);

CREATE TABLE IF NOT EXISTS entities (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    type            TEXT,                   -- person, company, court, government
    registered_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS case_edges (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id         TEXT,
    entity_a        TEXT,
    entity_b        TEXT,
    edge_type       TEXT,                   -- plaintiff, defendant, settled, dismissed
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS negotiation_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id         TEXT,
    turn            INTEGER,
    speaker         TEXT,                   -- 'agent_plaintiff' | 'agent_defendant' | 'system'
    message         TEXT,
    timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS historical_cases (
    id              TEXT PRIMARY KEY,
    summary         TEXT,
    category        TEXT,
    outcome         TEXT,
    dna_vector      TEXT,                   -- JSON float list for cosine similarity
    jurisdiction    TEXT,
    year            INTEGER
);

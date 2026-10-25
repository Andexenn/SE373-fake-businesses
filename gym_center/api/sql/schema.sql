-- Iron Việt Fitness database schema (SQLite)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS branches (
    branch_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    hours TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

CREATE TABLE IF NOT EXISTS members (
    member_id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    email TEXT,
    branch TEXT NOT NULL,
    goal TEXT,
    status TEXT NOT NULL CHECK (status IN ('active', 'suspended', 'inactive')),
    plan_id TEXT,
    joined_at TEXT NOT NULL,
    FOREIGN KEY (branch) REFERENCES branches(branch_id)
);

CREATE TABLE IF NOT EXISTS memberships (
    code TEXT PRIMARY KEY,
    member_id TEXT NOT NULL,
    plan_id TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    status TEXT NOT NULL,
    paid_vnd INTEGER NOT NULL DEFAULT 0 CHECK (paid_vnd >= 0),
    auto_renew INTEGER NOT NULL DEFAULT 0 CHECK (auto_renew IN (0, 1)),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

CREATE TABLE IF NOT EXISTS bookings (
    code TEXT PRIMARY KEY,
    member_id TEXT NOT NULL,
    activity_type TEXT NOT NULL CHECK (activity_type IN ('class', 'pt')),
    activity_id TEXT NOT NULL,
    coach_id TEXT,
    branch TEXT NOT NULL,
    start_at TEXT NOT NULL,
    status TEXT NOT NULL,
    fee_vnd INTEGER NOT NULL DEFAULT 0 CHECK (fee_vnd >= 0),
    FOREIGN KEY (member_id) REFERENCES members(member_id),
    FOREIGN KEY (branch) REFERENCES branches(branch_id)
);

CREATE TABLE IF NOT EXISTS requests (
    code TEXT PRIMARY KEY,
    member_id TEXT NOT NULL,
    request_type TEXT NOT NULL,
    reason TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    detail TEXT,
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

CREATE TABLE IF NOT EXISTS payments (
    code TEXT PRIMARY KEY,
    member_id TEXT NOT NULL,
    related_code TEXT NOT NULL,
    amount_vnd INTEGER NOT NULL CHECK (amount_vnd > 0),
    method TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

CREATE TABLE IF NOT EXISTS payment_methods (
    method_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1))
);

CREATE TABLE IF NOT EXISTS activity_types (
    activity_type TEXT PRIMARY KEY,
    display_name TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_members_branch_status ON members(branch, status);
CREATE INDEX IF NOT EXISTS idx_memberships_member_status ON memberships(member_id, status);
CREATE INDEX IF NOT EXISTS idx_bookings_start_branch ON bookings(start_at, branch);
CREATE INDEX IF NOT EXISTS idx_bookings_member ON bookings(member_id);
CREATE INDEX IF NOT EXISTS idx_requests_status_created ON requests(status, created_at);
CREATE INDEX IF NOT EXISTS idx_payments_member_created ON payments(member_id, created_at);

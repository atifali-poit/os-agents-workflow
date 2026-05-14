"""multi domain schema

Revision ID: 0004_multi_domain_schema
Revises: bf9ca9e3c2ff
Create Date: 2026-05-14
"""
from alembic import op
import sqlalchemy as sa


revision = "0004_multi_domain_schema"
down_revision = "bf9ca9e3c2ff"
branch_labels = None
depends_on = None


def _columns(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade():
    vendor_columns = _columns("vendors")
    if "status" not in vendor_columns:
        op.add_column("vendors", sa.Column("status", sa.String(40), nullable=True))
        op.execute("UPDATE vendors SET status = 'active' WHERE status IS NULL")
    if "created_at" not in vendor_columns:
        op.add_column("vendors", sa.Column("created_at", sa.DateTime(), nullable=True))
        op.execute("UPDATE vendors SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")

    employee_columns = _columns("employees")
    if "created_at" not in employee_columns:
        op.add_column("employees", sa.Column("created_at", sa.DateTime(), nullable=True))
        op.execute("UPDATE employees SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")

    leave_columns = _columns("leave_requests")
    if leave_columns and "employee_id" not in leave_columns:
        op.add_column("leave_requests", sa.Column("employee_id", sa.Integer(), nullable=True))
        op.execute("UPDATE leave_requests SET employee_id = 1 WHERE employee_id IS NULL")
    if leave_columns and "reason" not in leave_columns:
        op.add_column("leave_requests", sa.Column("reason", sa.String(160), nullable=True))
        op.execute("UPDATE leave_requests SET reason = 'Annual leave' WHERE reason IS NULL")

    pending_columns = _columns("pending_approvals")
    if pending_columns and "flags" not in pending_columns:
        op.add_column("pending_approvals", sa.Column("flags", sa.Text(), nullable=True))
        op.execute("UPDATE pending_approvals SET flags = '' WHERE flags IS NULL")


def downgrade():
    pending_columns = _columns("pending_approvals")
    if "flags" in pending_columns:
        op.drop_column("pending_approvals", "flags")
    leave_columns = _columns("leave_requests")
    if "reason" in leave_columns:
        op.drop_column("leave_requests", "reason")
    if "employee_id" in leave_columns:
        op.drop_column("leave_requests", "employee_id")
    employee_columns = _columns("employees")
    if "created_at" in employee_columns:
        op.drop_column("employees", "created_at")
    vendor_columns = _columns("vendors")
    if "created_at" in vendor_columns:
        op.drop_column("vendors", "created_at")
    if "status" in vendor_columns:
        op.drop_column("vendors", "status")

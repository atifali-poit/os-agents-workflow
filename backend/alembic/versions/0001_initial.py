"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-13
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("departments", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(100), nullable=False, unique=True))
    op.create_table("function_registry", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(120), nullable=False, unique=True), sa.Column("description", sa.Text(), nullable=False), sa.Column("version", sa.String(20), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False))
    op.create_table("rules", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(120), nullable=False, unique=True), sa.Column("description", sa.Text(), nullable=False), sa.Column("condition_expression", sa.String(240), nullable=False), sa.Column("action_name", sa.String(160), nullable=False), sa.Column("enabled", sa.Boolean(), nullable=False), sa.Column("created_by", sa.String(120), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("email", sa.String(160), nullable=False, unique=True), sa.Column("role", sa.String(80), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("vendors", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(160), nullable=False), sa.Column("country", sa.String(80), nullable=False), sa.Column("risk_level", sa.String(40), nullable=False))
    op.create_table("workflows", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(140), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("status", sa.String(40), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("audit_logs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("entity_type", sa.String(80), nullable=False), sa.Column("entity_id", sa.Integer(), nullable=False), sa.Column("action", sa.String(120), nullable=False), sa.Column("status", sa.String(40), nullable=False), sa.Column("message", sa.Text(), nullable=False), sa.Column("triggered_by", sa.String(120), nullable=False), sa.Column("timestamp", sa.DateTime(), nullable=False))
    op.create_table("employees", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("email", sa.String(160), nullable=False, unique=True), sa.Column("department_id", sa.Integer(), sa.ForeignKey("departments.id"), nullable=False), sa.Column("position", sa.String(120), nullable=False), sa.Column("manager_id", sa.Integer(), sa.ForeignKey("employees.id"), nullable=True))
    op.create_table("invoices", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("invoice_number", sa.String(80), nullable=False, unique=True), sa.Column("vendor_id", sa.Integer(), sa.ForeignKey("vendors.id"), nullable=False), sa.Column("amount", sa.Float(), nullable=False), sa.Column("status", sa.String(40), nullable=False), sa.Column("delay_days", sa.Integer(), nullable=False), sa.Column("requires_approval", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))


def downgrade():
    op.drop_table("invoices")
    op.drop_table("employees")
    op.drop_table("audit_logs")
    op.drop_table("workflows")
    op.drop_table("vendors")
    op.drop_table("users")
    op.drop_table("rules")
    op.drop_table("function_registry")
    op.drop_table("departments")


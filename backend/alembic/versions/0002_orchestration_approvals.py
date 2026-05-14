"""orchestration approvals

Revision ID: 0002_orchestration_approvals
Revises: 0001_initial
Create Date: 2026-05-14
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_orchestration_approvals"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "leave_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("employee_name", sa.String(120), nullable=False),
        sa.Column("days", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "approval_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("workflow_name", sa.String(140), nullable=False),
        sa.Column("workflow_run_id", sa.String(180), nullable=False, unique=True),
        sa.Column("entity_type", sa.String(80), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("approval_key", sa.String(120), nullable=False),
        sa.Column("approver_employee_id", sa.Integer(), sa.ForeignKey("employees.id"), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("pending_since", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("details", sa.Text(), nullable=False),
    )


def downgrade():
    op.drop_table("approval_requests")
    op.drop_table("leave_requests")

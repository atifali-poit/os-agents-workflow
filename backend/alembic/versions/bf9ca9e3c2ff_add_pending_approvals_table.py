"""add_pending_approvals_table

Revision ID: bf9ca9e3c2ff
Revises: 0003_workflow_ids
Create Date: 2026-05-14 19:47:54.260679
"""
from alembic import op
import sqlalchemy as sa


revision = 'bf9ca9e3c2ff'
down_revision = '0003_workflow_ids'
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    tables = inspector.get_table_names()
    if "pending_approvals" not in tables:
        op.create_table(
            "pending_approvals",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("workflow_id", sa.String(180), nullable=False),
            sa.Column("entity_type", sa.String(80), nullable=False),
            sa.Column("entity_id", sa.Integer(), nullable=False),
            sa.Column("required_role", sa.String(120), nullable=False),
            sa.Column("status", sa.String(40), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("approved_at", sa.DateTime(), nullable=True),
        )

    indexes = {index["name"] for index in inspector.get_indexes("pending_approvals")}
    for index_name, columns in {
        "ix_pending_approvals_id": ["id"],
        "ix_pending_approvals_workflow_id": ["workflow_id"],
        "ix_pending_approvals_entity_type": ["entity_type"],
        "ix_pending_approvals_entity_id": ["entity_id"],
        "ix_pending_approvals_required_role": ["required_role"],
        "ix_pending_approvals_status": ["status"],
    }.items():
        if index_name not in indexes:
            op.create_index(index_name, "pending_approvals", columns)


def downgrade():
    inspector = sa.inspect(op.get_bind())
    if "pending_approvals" not in inspector.get_table_names():
        return
    indexes = {index["name"] for index in inspector.get_indexes("pending_approvals")}
    for index_name in {
        "ix_pending_approvals_status",
        "ix_pending_approvals_required_role",
        "ix_pending_approvals_entity_id",
        "ix_pending_approvals_entity_type",
        "ix_pending_approvals_workflow_id",
        "ix_pending_approvals_id",
    }:
        if index_name in indexes:
            op.drop_index(index_name, table_name="pending_approvals")
    op.drop_table("pending_approvals")

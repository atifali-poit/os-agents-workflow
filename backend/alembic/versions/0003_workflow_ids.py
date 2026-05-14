"""workflow ids on approvals and audit logs

Revision ID: 0003_workflow_ids
Revises: 0002_orchestration_approvals
Create Date: 2026-05-14
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_workflow_ids"
down_revision = "0002_orchestration_approvals"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    approval_columns = {column["name"] for column in inspector.get_columns("approval_requests")}
    audit_columns = {column["name"] for column in inspector.get_columns("audit_logs")}
    indexes = {index["name"] for index in inspector.get_indexes("approval_requests")}

    if "workflow_id" not in approval_columns:
        op.add_column("approval_requests", sa.Column("workflow_id", sa.String(180), nullable=True))
    op.execute("UPDATE approval_requests SET workflow_id = workflow_run_id WHERE workflow_id IS NULL")
    if "ix_approval_requests_workflow_id" not in indexes:
        op.create_index("ix_approval_requests_workflow_id", "approval_requests", ["workflow_id"])
    if "workflow_id" not in audit_columns:
        op.add_column("audit_logs", sa.Column("workflow_id", sa.String(180), nullable=True))


def downgrade():
    op.drop_column("audit_logs", "workflow_id")
    op.drop_index("ix_approval_requests_workflow_id", table_name="approval_requests")
    op.drop_column("approval_requests", "workflow_id")

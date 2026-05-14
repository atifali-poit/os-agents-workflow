from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.models import ApprovalRequest, Employee, Invoice, Vendor


class GraphService:
    def __init__(self, db: Session):
        self.db = db

    def pending_approvals_for_employee(self, employee_id: int) -> dict:
        approvals = (
            self.db.query(ApprovalRequest)
            .options(joinedload(ApprovalRequest.approver).joinedload(Employee.department))
            .filter(ApprovalRequest.approver_employee_id == employee_id, ApprovalRequest.status == "pending")
            .all()
        )
        graph = self._sqlite_graph(employee_id, approvals)
        self._sync_to_neo4j(graph)
        return graph

    def sync_all_pending_approvals(self) -> None:
        employee_ids = [row[0] for row in self.db.query(ApprovalRequest.approver_employee_id).distinct().all()]
        for employee_id in employee_ids:
            self.pending_approvals_for_employee(employee_id)

    def _sqlite_graph(self, employee_id: int, approvals: list[ApprovalRequest]) -> dict:
        nodes: dict[str, dict] = {}
        relationships: list[dict] = []

        def node(node_id: str, label: str, node_type: str) -> None:
            nodes[node_id] = {"id": node_id, "label": label, "type": node_type}

        employee = self.db.get(Employee, employee_id)
        if employee:
            node(f"employee:{employee.id}", employee.name, "Employee")
            if employee.department:
                node(f"department:{employee.department.id}", employee.department.name, "Department")
                relationships.append(
                    {
                        "source": f"employee:{employee.id}",
                        "target": f"department:{employee.department.id}",
                        "type": "BELONGS_TO",
                    }
                )

        for approval in approvals:
            workflow_id = f"workflow:{approval.workflow_id}"
            approval_id = f"approval:{approval.id}"
            rule_id = f"rule:{approval.approval_key}"
            node(workflow_id, approval.workflow_name, "Workflow")
            node(approval_id, approval.approval_key.replace("_", " ").title(), "Approval")
            node(rule_id, approval.approval_key.replace("_", " ").title(), "Rule")
            node(f"agent:{approval.approval_key}", approval.approval_key.replace("_", " ").title(), "Agent")
            relationships.append({"source": f"agent:{approval.approval_key}", "target": workflow_id, "type": "EXECUTES"})
            relationships.append({"source": workflow_id, "target": rule_id, "type": "USES_RULE"})
            relationships.append({"source": workflow_id, "target": approval_id, "type": "REQUIRES_APPROVAL"})
            relationships.append(
                {"source": approval_id, "target": f"employee:{approval.approver_employee_id}", "type": "REQUIRES_APPROVAL_FROM"}
            )

            if approval.entity_type == "invoice":
                invoice = self.db.get(Invoice, approval.entity_id)
                if invoice:
                    invoice_id = f"invoice:{invoice.id}"
                    vendor_id = f"vendor:{invoice.vendor_id}"
                    node(invoice_id, invoice.invoice_number, "Invoice")
                    if invoice.vendor:
                        node(vendor_id, invoice.vendor.name, "Vendor")
                    relationships.append({"source": invoice_id, "target": vendor_id, "type": "FROM"})
                    relationships.append({"source": invoice_id, "target": workflow_id, "type": "HAS_WORKFLOW"})
                    relationships.append({"source": vendor_id, "target": workflow_id, "type": "HAS_WORKFLOW"})
            elif approval.entity_type == "vendor":
                vendor = self.db.get(Vendor, approval.entity_id)
                if vendor:
                    node(f"vendor:{vendor.id}", vendor.name, "Vendor")
                    relationships.append({"source": f"vendor:{vendor.id}", "target": workflow_id, "type": "HAS_WORKFLOW"})

        return {"employee_id": employee_id, "nodes": list(nodes.values()), "relationships": relationships}

    def _sync_to_neo4j(self, graph: dict) -> None:
        if not settings.neo4j_enabled:
            return
        try:
            from neo4j import GraphDatabase

            allowed_labels = {"Invoice", "Vendor", "Employee", "Department", "Workflow", "Rule", "Agent", "Approval"}
            allowed_relationships = {
                "FROM",
                "HAS_WORKFLOW",
                "REQUIRES_APPROVAL",
                "REQUIRES_APPROVAL_FROM",
                "EXECUTES",
                "BELONGS_TO",
                "USES_RULE",
            }
            driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))
            with driver.session() as session:
                for node in graph["nodes"]:
                    label = node["type"] if node["type"] in allowed_labels else "GraphNode"
                    session.run(
                        f"MERGE (n:{label} {{id: $id}}) SET n.label = $label, n.type = $type",
                        id=node["id"],
                        label=node["label"],
                        type=node["type"],
                    )
                for rel in graph["relationships"]:
                    rel_type = rel["type"] if rel["type"] in allowed_relationships else "RELATED"
                    session.run(
                        f"""
                        MATCH (source {{id: $source}})
                        MATCH (target {{id: $target}})
                        MERGE (source)-[r:{rel_type}]->(target)
                        """,
                        source=rel["source"],
                        target=rel["target"],
                    )
            driver.close()
        except Exception:
            return

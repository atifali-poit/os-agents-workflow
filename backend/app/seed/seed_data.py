from app.database import Base, SessionLocal, engine
from app.models import Department, Employee, FunctionRegistry, Invoice, LeaveRequest, Rule, User, Vendor, Workflow


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        departments = {
            name: Department(name=name)
            for name in ["Finance", "Procurement", "HR", "IT", "Operations", "Sales", "Legal"]
        }
        db.add_all(departments.values())
        db.flush()

        employee_rows = [
            ("Sarah Ahmed", "sarah@igate.com", "Finance", "Finance Director", None),
            ("Khalid Al Saud", "khalid@igate.com", "Finance", "Finance Manager", 1),
            ("Fatima Hassan", "fatima@igate.com", "Procurement", "Procurement Director", None),
            ("Omar Al Rashid", "omar@igate.com", "Procurement", "Procurement Officer", 3),
            ("Noura Abdullah", "noura@igate.com", "HR", "HR Director", None),
            ("Ahmed Al Qahtani", "ahmed@igate.com", "HR", "HR Manager", 5),
            ("Faisal Al Otaibi", "faisal@igate.com", "IT", "IT Manager", None),
            ("Layla Al Shamri", "layla@igate.com", "Operations", "Ops Director", None),
            ("Mohammed Al Ghamdi", "mohammed@igate.com", "Sales", "Sales Director", None),
            ("Hessa Al Khalifa", "hessa@igate.com", "Legal", "Legal Advisor", None),
        ]
        employees = []
        for name, email, department, position, manager_id in employee_rows:
            employees.append(
                Employee(
                    name=name,
                    email=email,
                    department_id=departments[department].id,
                    position=position,
                    manager_id=manager_id,
                )
            )
        db.add_all(employees)
        db.flush()

        db.add_all(
            [
                User(name=employee.name, email=employee.email, role=employee.position.lower().replace(" ", "_"))
                for employee in employees
            ]
        )

        vendor_rows = [
            ("Gulf Industrial Supplies", "low", "Saudi Arabia", "active"),
            ("Desert Technologies", "medium", "UAE", "active"),
            ("Riyadh Medical Group", "high", "Saudi Arabia", "active"),
            ("Small Supplies Co", "low", "Saudi Arabia", "active"),
            ("Saudi Telecom", "low", "Saudi Arabia", "active"),
            ("Oil Corp", "critical", "Saudi Arabia", "active"),
            ("International Logistics", "high", "Yemen", "watch"),
            ("European Parts Ltd", "medium", "Germany", "active"),
            ("Asian Electronics", "high", "China", "active"),
            ("Local Contractors", "low", "Saudi Arabia", "active"),
        ]
        vendors = [Vendor(name=name, risk_level=risk, country=country, status=status) for name, risk, country, status in vendor_rows]
        db.add_all(vendors)
        db.flush()
        vendor_by_name = {vendor.name: vendor for vendor in vendors}

        invoice_rows = [
            ("INV-001", 75000, 0, "Gulf Industrial Supplies", "pending"),
            ("INV-002", 12000, 2, "Desert Technologies", "pending"),
            ("INV-003", 250000, 0, "Saudi Telecom", "pending"),
            ("INV-004", 5000, 45, "Small Supplies Co", "overdue"),
            ("INV-005", 180000, 0, "Riyadh Medical Group", "pending"),
            ("INV-006", 35000, 8, "Gulf Industrial Supplies", "pending"),
            ("INV-007", 52000, 0, "Desert Technologies", "pending"),
            ("INV-008", 89000, 16, "Saudi Telecom", "delayed"),
            ("INV-009", 1500000, 0, "Oil Corp", "pending"),
            ("INV-010", 8000, 3, "Small Supplies Co", "pending"),
        ]
        db.add_all(
            [
                Invoice(
                    invoice_number=number,
                    amount=amount,
                    delay_days=delay_days,
                    vendor_id=vendor_by_name[vendor_name].id,
                    status=status,
                    requires_approval=False,
                )
                for number, amount, delay_days, vendor_name, status in invoice_rows
            ]
        )

        leave_rows = [
            (3, 5, "pending", "Annual leave"),
            (6, 12, "pending", "Hajj leave"),
            (2, 3, "pending", "Sick leave"),
            (5, 8, "pending", "Annual leave"),
            (4, 22, "pending", "Emergency leave"),
            (8, 6, "pending", "Annual leave"),
            (9, 15, "pending", "Medical leave"),
            (10, 4, "pending", "Training"),
            (7, 18, "pending", "Parental leave"),
            (1, 25, "pending", "Sabbatical"),
        ]
        db.add_all([LeaveRequest(employee_id=employee_id, days=days, status=status, reason=reason) for employee_id, days, status, reason in leave_rows])

        db.add_all(
            [
                Rule(name="finance_high_value_invoice", description="Invoices over 50000 require finance director approval.", condition_expression="invoice.amount > 50000", action_name="require_approval(finance_director)", created_by="system"),
                Rule(name="finance_delayed_invoice", description="Invoices delayed over 14 days require finance manager escalation.", condition_expression="invoice.delay_days > 14", action_name="require_approval(finance_manager,escalation)", created_by="system"),
                Rule(name="finance_cfo_invoice", description="Invoices over 100000 require CFO approval.", condition_expression="invoice.amount > 100000", action_name="require_approval(cfo)", created_by="system"),
                Rule(name="procurement_high_risk_vendor", description="High-risk vendors require procurement officer approval.", condition_expression='vendor.risk_level == "high"', action_name="require_approval(procurement_officer)", created_by="system"),
                Rule(name="procurement_critical_vendor", description="Critical-risk vendors require procurement director approval and block flag.", condition_expression='vendor.risk_level == "critical"', action_name="require_approval(procurement_director,block)", created_by="system"),
                Rule(name="procurement_medium_risk_vendor", description="Medium-risk vendors require procurement analyst review.", condition_expression='vendor.risk_level == "medium"', action_name="require_approval(procurement_analyst)", created_by="system"),
                Rule(name="hr_leave_manager_review", description="Leave over 10 days requires HR manager approval.", condition_expression="leave.days > 10", action_name="require_approval(hr_manager)", created_by="system"),
                Rule(name="hr_leave_director_review", description="Leave over 20 days requires HR director approval.", condition_expression="leave.days > 20", action_name="require_approval(hr_director)", created_by="system"),
                Rule(name="hr_leave_executive_review", description="Leave over 30 days requires executive committee approval.", condition_expression="leave.days > 30", action_name="require_approval(executive_committee)", created_by="system"),
            ]
        )

        db.add_all(
            [
                FunctionRegistry(name="require_approval", description="Create a pending approval for a required business role."),
                FunctionRegistry(name="notify", description="Create a notification event."),
                FunctionRegistry(name="escalate", description="Escalate an entity to an operating team."),
                FunctionRegistry(name="approve_invoice", description="Approve an invoice deterministically."),
                FunctionRegistry(name="reject_invoice", description="Reject an invoice deterministically."),
            ]
        )
        db.add_all(
            [
                Workflow(name="Finance Invoice Governance", description="Invoice rule evaluation and approval routing.", status="ready"),
                Workflow(name="Procurement Vendor Governance", description="Vendor risk rule evaluation and approval routing.", status="ready"),
                Workflow(name="HR Leave Governance", description="Leave request rule evaluation and approval routing.", status="ready"),
            ]
        )
        db.commit()
        print("Seeded iGate OS multi-domain POC database.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import AuditLog, Department, Employee, LeaveRequest
from app.schemas import EmployeeCreate, EmployeeOut, EmployeeUpdate

router = APIRouter(prefix="/api/employees", tags=["employees"])


def _department(db: Session, name: str) -> Department:
    department = db.query(Department).filter(Department.name == name).one_or_none()
    if department is None:
        department = Department(name=name)
        db.add(department)
        db.flush()
    return department


@router.get("", response_model=list[EmployeeOut])
def list_employees(db: Session = Depends(get_db)):
    return db.query(Employee).options(joinedload(Employee.department)).order_by(Employee.id).all()


@router.post("", response_model=EmployeeOut)
def create_employee(employee_in: EmployeeCreate, db: Session = Depends(get_db)):
    department = _department(db, employee_in.department)
    employee = Employee(
        name=employee_in.name,
        email=employee_in.email,
        department_id=department.id,
        position=employee_in.position,
        manager_id=employee_in.manager_id,
    )
    db.add(employee)
    db.flush()
    db.add(AuditLog(entity_type="employee", entity_id=employee.id, action="created", status="success", message=f"Employee {employee.name} created.", triggered_by="employee_screen"))
    db.commit()
    db.refresh(employee)
    return employee


@router.put("/{employee_id}", response_model=EmployeeOut)
def update_employee(employee_id: int, employee_in: EmployeeUpdate, db: Session = Depends(get_db)):
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    department = _department(db, employee_in.department)
    employee.name = employee_in.name
    employee.email = employee_in.email
    employee.department_id = department.id
    employee.position = employee_in.position
    employee.manager_id = employee_in.manager_id
    db.add(AuditLog(entity_type="employee", entity_id=employee.id, action="updated", status="success", message=f"Employee {employee.name} updated.", triggered_by="employee_screen"))
    db.commit()
    db.refresh(employee)
    return employee


@router.delete("/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.query(Employee).filter(Employee.manager_id == employee.id).update({"manager_id": None})
    db.query(LeaveRequest).filter(LeaveRequest.employee_id == employee.id).delete()
    db.add(AuditLog(entity_type="employee", entity_id=employee.id, action="deleted", status="success", message=f"Employee {employee.name} deleted.", triggered_by="employee_screen"))
    db.delete(employee)
    db.commit()
    return {"deleted": True}

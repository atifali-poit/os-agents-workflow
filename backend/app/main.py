from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import agents, approvals, audit_logs, dashboard, employees, graph, health, invoices, leave_requests, rules, runtime, vendors, workflows

try:
    print("Starting app")
    app = FastAPI(
        title="iGate OS POC",
        description="A deterministic workflow operating system prototype with governed AI rule translation.",
        version="0.1.0",
    )
    print("App created")
except Exception as e:
    print(f"Error creating app: {e}")
    raise

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(rules.router)
app.include_router(runtime.router)
app.include_router(invoices.router)
app.include_router(vendors.router)
app.include_router(employees.router)
app.include_router(leave_requests.router)
app.include_router(audit_logs.router)
app.include_router(dashboard.router)
app.include_router(agents.router)
app.include_router(approvals.router)
app.include_router(graph.router)
app.include_router(workflows.router)

@app.get("/")
def root():
    return {"message": "Hello World"}


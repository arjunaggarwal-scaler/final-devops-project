"""API tests for the TaskBoard backend.

These tests run against an isolated SQLite database (configured in conftest.py)
so they never touch the production PostgreSQL database. They cover the health,
root, stats, and full CRUD lifecycle of the /api/tasks resource.
"""


def test_health(client):
    """GET /health returns the liveness status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_root_service_identity(client):
    """GET / returns the service identity banner."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "TaskBoard API"


def test_ready_checks_database(client):
    """GET /ready performs a real DB query and returns READY."""
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "READY"}


def test_create_task(client):
    """POST /api/tasks creates a task and returns 201 with the persisted body."""
    payload = {"title": "Deploy application", "priority": "HIGH", "assignee": "Arjun"}
    response = client.post("/api/tasks", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Deploy application"
    assert body["priority"] == "HIGH"
    assert body["status"] == "TODO"
    assert "id" in body


def test_create_task_validation_rejects_empty_title(client):
    """POST /api/tasks rejects an empty title with 422."""
    response = client.post("/api/tasks", json={"title": ""})
    assert response.status_code == 422


def test_list_tasks_returns_created_task(client):
    """GET /api/tasks returns previously created tasks."""
    client.post("/api/tasks", json={"title": "Write Terraform", "priority": "MEDIUM"})
    response = client.get("/api/tasks")
    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert "Write Terraform" in titles


def test_update_task_status(client):
    """PUT /api/tasks/{id} updates an existing task."""
    created = client.post("/api/tasks", json={"title": "Configure CI", "priority": "LOW"}).json()
    task_id = created["id"]
    response = client.put(f"/api/tasks/{task_id}", json={"status": "IN_PROGRESS"})
    assert response.status_code == 200
    assert response.json()["status"] == "IN_PROGRESS"


def test_get_single_task_and_404(client):
    """GET /api/tasks/{id} returns a task, or 404 when it does not exist."""
    created = client.post("/api/tasks", json={"title": "Monitor cluster"}).json()
    ok = client.get(f"/api/tasks/{created['id']}")
    assert ok.status_code == 200
    missing = client.get("/api/tasks/999999")
    assert missing.status_code == 404


def test_delete_task(client):
    """DELETE /api/tasks/{id} removes the task and a second GET returns 404."""
    created = client.post("/api/tasks", json={"title": "Clean up"}).json()
    task_id = created["id"]
    deleted = client.delete(f"/api/tasks/{task_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/tasks/{task_id}").status_code == 404


def test_stats_endpoint(client):
    """GET /api/tasks/stats returns aggregated counts by status."""
    response = client.get("/api/tasks/stats")
    assert response.status_code == 200
    body = response.json()
    for key in ("total", "todo", "inProgress", "done"):
        assert key in body
    assert body["total"] >= 0


def test_metrics_endpoint_is_prometheus(client):
    """GET /metrics returns Prometheus-formatted text."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_request" in response.text or "python_info" in response.text

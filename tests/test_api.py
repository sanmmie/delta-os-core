import asyncio

from api.main import health_check, readiness_check, root


def test_root_reports_runtime_metadata():
    response = asyncio.run(root())
    assert response["status"] == "operational"
    assert response["version"] == "1.0.0"


def test_health_and_readiness_are_dynamic_and_healthy():
    health = asyncio.run(health_check())
    readiness = asyncio.run(readiness_check())

    assert health["status"] == "healthy"
    assert health["service"] == "api"
    assert health["timestamp"].endswith("+00:00")
    assert readiness["status"] == "ready"

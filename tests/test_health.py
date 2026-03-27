"""
Health check endpoint tests
"""


def test_health_check(test_client):
    """Test the health check endpoint returns OK"""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version_endpoint(test_client):
    """Test the version endpoint returns correct info"""
    response = test_client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "service_version" in data
    assert "api_version" in data

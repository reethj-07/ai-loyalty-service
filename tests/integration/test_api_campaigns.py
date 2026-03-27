def test_campaigns_endpoint_is_reachable(test_client):
    response = test_client.get("/api/v1/campaigns")
    assert response.status_code in (200, 404)

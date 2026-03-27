def test_members_list_endpoint_returns_200(test_client):
    response = test_client.get("/api/v1/members")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body

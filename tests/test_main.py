def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_openapi_docs_available(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "AI Knowledge API"


def test_signup_and_login(client):
    email = "dev@example.com"
    signup = client.post(
        "/auth/signup",
        json={
            "first_name": "Dev",
            "email": email,
            "password": "securepass123",
        },
    )
    assert signup.status_code == 200
    assert "access_token" in signup.json()

    login = client.post("/auth/login", json={"email": email, "password": "securepass123"})
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"


def test_query_requires_auth(client):
    response = client.post("/query/", json={"query": "What is FastAPI?"})
    assert response.status_code == 403


def test_query_with_auth(client, auth_headers):
    response = client.post(
        "/query/",
        json={"query": "Summarize my documents"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert "answer" in body
    assert isinstance(body["sources"], list)

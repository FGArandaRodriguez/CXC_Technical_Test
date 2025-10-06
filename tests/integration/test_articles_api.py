from fastapi.testclient import TestClient

def test_create_and_get_article(client: TestClient):
    """
    Prueba el flujo completo de crear un artículo y luego obtenerlo.
    El 'client' es proporcionado por el fixture en conftest.py, garantizando un entorno limpio.
    """
    # 1. Crear un artículo
    response = client.post(
        "/api/v1/articles/",
        json={"title": "Integration Test Title", "body": "This is a valid test body.", "author": "Tester"},
    )
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["title"] == "Integration Test Title"
    assert "id" in data
    article_id = data["id"]

    # 2. Obtener el artículo creado
    response = client.get(f"/api/v1/articles/{article_id}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["title"] == "Integration Test Title"
    assert data["id"] == article_id

def test_get_non_existent_article(client: TestClient):
    """
    Prueba que se obtiene un error 404 para un artículo que no existe.
    """
    response = client.get(f"/api/v1/articles/9999")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"

def test_delete_article(client: TestClient):
    """
    Prueba el flujo de crear y luego eliminar un artículo.
    """
    # 1. Crear un artículo para poder eliminarlo
    response = client.post(
        "/api/v1/articles/",
        json={"title": "To Be Deleted", "body": "This body is long enough.", "author": "Deleter"},
    )
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    article_id = response.json()["id"]

    # 2. Eliminar el artículo
    response = client.delete(f"/api/v1/articles/{article_id}")
    assert response.status_code == 204, f"Expected 204, got {response.status_code}: {response.text}"

    # 3. Verificar que el artículo ya no se puede obtener (debe dar 404)
    response = client.get(f"/api/v1/articles/{article_id}")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
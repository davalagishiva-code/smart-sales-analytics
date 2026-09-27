from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_products_catalog_endpoint_returns_inventory_data():
    response = client.get('/api/products')
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload['message'] in {'Product catalog loaded', 'Product report loaded'}
    assert isinstance(payload['data'], list)
    assert len(payload['data']) >= 1
    product = payload['data'][0]
    assert 'id' in product
    assert 'name' in product
    assert 'category' in product
    assert 'stock' in product


def test_product_can_be_created_and_deleted():
    payload = {
        'name': 'Test Product Alpha',
        'sku': 'TEST-ALPHA-001',
        'category': 'Electronics',
        'price': 299.99,
        'cost_price': 180.0,
        'stock': 12,
        'min_stock': 5,
        'description': 'Temporary product for test',
        'status': 'active',
    }

    create_response = client.post('/api/products', json=payload)
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()['data']
    product_id = created['id']

    delete_response = client.delete(f'/api/products/{product_id}')
    assert delete_response.status_code == 200, delete_response.text
    assert delete_response.json()['deleted'] is True

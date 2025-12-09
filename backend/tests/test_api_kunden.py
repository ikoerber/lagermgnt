import pytest

def test_get_kunden_returns_list(client):
    response = client.get('/api/kunden')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_create_kunde_success(client):
    data = {
        'name': 'Firma ABC GmbH',
        'kontakt': 'info@firma-abc.de'
    }
    response = client.post('/api/kunden', json=data)
    assert response.status_code == 201
    
    response_data = response.get_json()
    assert 'id' in response_data
    assert response_data['name'] == data['name']
    assert response_data['kontakt'] == data['kontakt']

def test_create_kunde_without_name(client):
    data = {'kontakt': 'test@test.de'}
    response = client.post('/api/kunden', json=data)
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_create_kunde_minimal_data(client):
    data = {'name': 'Minimaler Kunde'}
    response = client.post('/api/kunden', json=data)
    assert response.status_code == 201
    
    response_data = response.get_json()
    assert response_data['name'] == 'Minimaler Kunde'
    assert response_data['kontakt'] == ''

def test_get_kunden_after_create(client):
    # Mehrere Kunden anlegen
    kunden_data = [
        {'name': 'Kunde A', 'kontakt': 'a@test.de'},
        {'name': 'Kunde B', 'kontakt': 'b@test.de'},
        {'name': 'Kunde C'}
    ]
    
    for kunde in kunden_data:
        response = client.post('/api/kunden', json=kunde)
        assert response.status_code == 201
    
    response = client.get('/api/kunden')
    assert response.status_code == 200
    
    kunden = response.get_json()
    kunden_namen = [k['name'] for k in kunden]
    assert 'Kunde A' in kunden_namen
    assert 'Kunde B' in kunden_namen
    assert 'Kunde C' in kunden_namen

def test_create_kunde_empty_body(client):
    response = client.post('/api/kunden', json={})
    assert response.status_code == 400

def test_create_kunde_no_json(client):
    response = client.post('/api/kunden')
    assert response.status_code == 400
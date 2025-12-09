import pytest

def test_get_kunden_returns_list(auth_client):
    response = auth_client.get('/api/kunden', headers=auth_client.auth_headers)
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_create_kunde_success(auth_client):
    data = {
        'name': 'Firma ABC GmbH',
        'kontakt': 'info@firma-abc.de'
    }
    response = auth_client.post('/api/kunden', json=data, headers=auth_client.auth_headers)
    assert response.status_code == 201
    
    response_data = response.get_json()
    assert 'id' in response_data
    assert response_data['name'] == data['name']
    assert response_data['kontakt'] == data['kontakt']

def test_create_kunde_without_name(auth_client):
    data = {'kontakt': 'test@test.de'}
    response = auth_client.post('/api/kunden', json=data, headers=auth_client.auth_headers)
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_create_kunde_minimal_data(auth_client):
    data = {'name': 'Minimaler Kunde'}
    response = auth_client.post('/api/kunden', json=data, headers=auth_client.auth_headers)
    assert response.status_code == 201
    
    response_data = response.get_json()
    assert response_data['name'] == 'Minimaler Kunde'
    assert response_data['kontakt'] == ''

def test_get_kunden_after_create(auth_client):
    # Mehrere Kunden anlegen
    kunden_data = [
        {'name': 'Kunde A', 'kontakt': 'a@test.de'},
        {'name': 'Kunde B', 'kontakt': 'b@test.de'},
        {'name': 'Kunde C'}
    ]
    
    for kunde in kunden_data:
        response = auth_client.post('/api/kunden', json=kunde, headers=auth_client.auth_headers)
        assert response.status_code == 201
    
    response = auth_client.get('/api/kunden', headers=auth_client.auth_headers)
    assert response.status_code == 200
    
    kunden = response.get_json()
    kunden_namen = [k['name'] for k in kunden]
    assert 'Kunde A' in kunden_namen
    assert 'Kunde B' in kunden_namen
    assert 'Kunde C' in kunden_namen

def test_create_kunde_empty_body(auth_client):
    response = auth_client.post('/api/kunden', json={}, headers=auth_client.auth_headers)
    assert response.status_code == 400

def test_create_kunde_no_json(auth_client):
    response = auth_client.post('/api/kunden', headers=auth_client.auth_headers)
    assert response.status_code == 400
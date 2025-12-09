import pytest

def test_get_lagerbestand_bericht_returns_list(client):
    response = client.get('/api/berichte/lagerbestand')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_get_lagerbestand_bericht_zusammenfassung(client, sample_data):
    # Lagereingang
    client.post('/api/lager/eingang', json={
        'artikelnummer': sample_data['artikelnummer'],
        'menge': 10,
        'einkaufspreis': 49.99
    })
    
    response = client.get('/api/berichte/lagerbestand')
    assert response.status_code == 200
    
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['artikelnummer'] == sample_data['artikelnummer']
    assert 'gesamtmenge' in data[0]
    assert 'durchschnittspreis' in data[0]
    assert 'gesamtwert' in data[0]

def test_get_lagerbestand_bericht_detailliert(client, sample_data):
    # Mehrere Eingänge
    eingaenge = [
        {'menge': 10, 'einkaufspreis': 45.00, 'einlagerungsdatum': '2024-01-10'},
        {'menge': 5, 'einkaufspreis': 50.00, 'einlagerungsdatum': '2024-01-15'}
    ]
    
    for eingang in eingaenge:
        client.post('/api/lager/eingang', json={
            'artikelnummer': sample_data['artikelnummer'],
            **eingang
        })
    
    response = client.get('/api/berichte/lagerbestand?detailliert=true')
    assert response.status_code == 200
    
    data = response.get_json()
    assert len(data) == 2  # Zwei separate Lagerbestände
    
    for eintrag in data:
        assert 'lager_id' in eintrag
        assert 'artikelnummer' in eintrag
        assert 'bezeichnung' in eintrag
        assert 'lieferant' in eintrag
        assert 'menge' in eintrag
        assert 'einkaufspreis' in eintrag
        assert 'einlagerungsdatum' in eintrag
        assert 'gesamtwert' in eintrag

def test_get_projekte_bericht_returns_list(client):
    response = client.get('/api/berichte/projekte')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_get_projekte_bericht_with_data(client, sample_data):
    # Lagereingang und Verkauf
    client.post('/api/lager/eingang', json={
        'artikelnummer': sample_data['artikelnummer'],
        'menge': 10,
        'einkaufspreis': 49.99
    })
    
    client.post('/api/verkauf', json={
        'projekt_id': sample_data['projekt_id'],
        'artikelnummer': sample_data['artikelnummer'],
        'verkaufte_menge': 3,
        'verkaufspreis': 79.99
    })
    
    response = client.get('/api/berichte/projekte')
    assert response.status_code == 200
    
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['projekt_id'] == sample_data['projekt_id']
    assert data[0]['projektname'] == 'Test Projekt'
    assert data[0]['kunde'] == 'Test Kunde GmbH'
    assert data[0]['anzahl_verkaeufe'] == 1
    assert abs(data[0]['gesamtumsatz'] - 239.97) < 0.01  # 3 * 79.99, mit Rundungstoleranz

def test_get_gewinn_analyse_empty(client):
    response = client.get('/api/berichte/gewinn')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'artikel_analyse' in data
    assert data['artikel_analyse'] == []
    assert data['gesamtumsatz'] == 0
    assert data['gesamtkosten'] == 0
    assert data['gesamtgewinn'] == 0

def test_get_gewinn_analyse_with_sales(client, sample_data):
    # Lagereingang
    client.post('/api/lager/eingang', json={
        'artikelnummer': sample_data['artikelnummer'],
        'menge': 10,
        'einkaufspreis': 50.00
    })
    
    # Verkauf
    client.post('/api/verkauf', json={
        'projekt_id': sample_data['projekt_id'],
        'artikelnummer': sample_data['artikelnummer'],
        'verkaufte_menge': 4,
        'verkaufspreis': 80.00
    })
    
    response = client.get('/api/berichte/gewinn')
    assert response.status_code == 200
    
    data = response.get_json()
    assert len(data['artikel_analyse']) == 1
    
    analyse = data['artikel_analyse'][0]
    assert analyse['artikelnummer'] == sample_data['artikelnummer']
    assert analyse['verkaufte_menge'] == 4
    assert analyse['durchschnitt_verkaufspreis'] == 80.00
    assert analyse['durchschnitt_einkaufspreis'] == 50.00
    assert analyse['umsatz'] == 320.00  # 4 * 80
    assert analyse['kosten'] == 200.00  # 4 * 50
    assert analyse['gewinn'] == 120.00  # 320 - 200
    assert analyse['gewinnmarge'] == 37.5  # 120/320 * 100
    
    assert data['gesamtumsatz'] == 320.00
    assert data['gesamtkosten'] == 200.00
    assert data['gesamtgewinn'] == 120.00
    assert data['gesamtgewinnmarge'] == 37.5

def test_get_gewinn_analyse_specific_projekt(client, sample_data):
    # Setup für zwei Projekte
    kunde2_response = client.post('/api/kunden', json={'name': 'Kunde 2'})
    kunde2_id = kunde2_response.get_json()['id']
    
    projekt2_response = client.post('/api/projekte', json={
        'projektname': 'Projekt 2',
        'kunde_id': kunde2_id
    })
    projekt2_id = projekt2_response.get_json()['id']
    
    # Lagereingang
    client.post('/api/lager/eingang', json={
        'artikelnummer': sample_data['artikelnummer'],
        'menge': 20,
        'einkaufspreis': 50.00
    })
    
    # Verkäufe in beiden Projekten
    client.post('/api/verkauf', json={
        'projekt_id': sample_data['projekt_id'],
        'artikelnummer': sample_data['artikelnummer'],
        'verkaufte_menge': 3,
        'verkaufspreis': 80.00
    })
    
    client.post('/api/verkauf', json={
        'projekt_id': projekt2_id,
        'artikelnummer': sample_data['artikelnummer'],
        'verkaufte_menge': 5,
        'verkaufspreis': 85.00
    })
    
    # Gewinn-Analyse nur für erstes Projekt
    response = client.get(f'/api/berichte/gewinn?projekt_id={sample_data["projekt_id"]}')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['gesamtumsatz'] == 240.00  # Nur erstes Projekt: 3 * 80
    
    # Gewinn-Analyse für alle Projekte
    response = client.get('/api/berichte/gewinn')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['gesamtumsatz'] == 665.00  # 3*80 + 5*85 = 240 + 425

def test_get_lagerumschlag_returns_list(client):
    response = client.get('/api/berichte/lagerumschlag')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_get_lagerumschlag_with_data(client, sample_data):
    # Lagereingang
    client.post('/api/lager/eingang', json={
        'artikelnummer': sample_data['artikelnummer'],
        'menge': 20,
        'einkaufspreis': 50.00
    })
    
    # Verkauf
    client.post('/api/verkauf', json={
        'projekt_id': sample_data['projekt_id'],
        'artikelnummer': sample_data['artikelnummer'],
        'verkaufte_menge': 8,
        'verkaufspreis': 80.00
    })
    
    response = client.get('/api/berichte/lagerumschlag')
    assert response.status_code == 200
    
    data = response.get_json()
    assert len(data) == 1
    
    umschlag = data[0]
    assert umschlag['artikelnummer'] == sample_data['artikelnummer']
    assert umschlag['lagerbestand'] == 12  # 20 - 8
    assert umschlag['verkaufte_menge'] == 8
    assert umschlag['anzahl_verkaeufe'] == 1
    assert umschlag['umschlagrate'] == 8/12  # verkauft/lager

def test_api_status(client):
    response = client.get('/api/status')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'ok'
    assert 'message' in data
    assert 'version' in data
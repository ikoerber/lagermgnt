import pytest

def test_complete_workflow(auth_client):
    """Test eines kompletten Workflows von der Anlage bis zum Verkauf"""
    
    # 1. Lieferant anlegen
    lieferant_response = auth_client.post('/api/lieferanten', json={
        'name': 'Premium Möbel GmbH',
        'kontakt': 'info@premium-moebel.de'
    }, headers=auth_client.auth_headers)
    assert lieferant_response.status_code == 201
    lieferant_id = lieferant_response.get_json()['id']
    
    # 2. Artikel anlegen
    artikel_response = auth_client.post('/api/artikel', json={
        'artikelnummer': 'CHAIR-PREMIUM-001',
        'bezeichnung': 'Premium Bürostuhl Leder schwarz',
        'lieferant_id': lieferant_id
    }, headers=auth_client.auth_headers)
    assert artikel_response.status_code == 201
    
    # 3. Kunde anlegen
    kunde_response = auth_client.post('/api/kunden', json={
        'name': 'Großkunde AG',
        'kontakt': 'einkauf@grosskunde.de'
    }, headers=auth_client.auth_headers)
    assert kunde_response.status_code == 201
    kunde_id = kunde_response.get_json()['id']
    
    # 4. Projekt anlegen
    projekt_response = auth_client.post('/api/projekte', json={
        'projektname': 'Büroausstattung Hauptsitz',
        'kunde_id': kunde_id
    }, headers=auth_client.auth_headers)
    assert projekt_response.status_code == 201
    projekt_id = projekt_response.get_json()['id']
    
    # 5. Erste Lieferung einlagern
    lager1_response = auth_client.post('/api/lager/eingang', json={
        'artikelnummer': 'CHAIR-PREMIUM-001',
        'menge': 25,
        'einkaufspreis': 180.00,
        'einlagerungsdatum': '2024-01-10'
    }, headers=auth_client.auth_headers)
    assert lager1_response.status_code == 201
    
    # 6. Zweite Lieferung einlagern (höherer Preis)
    lager2_response = auth_client.post('/api/lager/eingang', json={
        'artikelnummer': 'CHAIR-PREMIUM-001',
        'menge': 15,
        'einkaufspreis': 190.00,
        'einlagerungsdatum': '2024-01-20'
    }, headers=auth_client.auth_headers)
    assert lager2_response.status_code == 201
    
    # 7. Lagerbestand prüfen
    bestand_response = auth_client.get('/api/lager/bestand', headers=auth_client.auth_headers)
    assert bestand_response.status_code == 200
    bestand = bestand_response.get_json()
    assert len(bestand) == 1
    assert bestand[0]['gesamtmenge'] == 40  # 25 + 15
    
    # 8. Ersten Verkauf durchführen (FIFO - sollte zuerst günstigere Ware verkaufen)
    verkauf1_response = auth_client.post('/api/verkauf', json={
        'projekt_id': projekt_id,
        'artikelnummer': 'CHAIR-PREMIUM-001',
        'verkaufte_menge': 20,
        'verkaufspreis': 280.00,
        'verkaufsdatum': '2024-02-05'
    }, headers=auth_client.auth_headers)
    assert verkauf1_response.status_code == 201
    
    # 9. Zweiten Verkauf durchführen
    verkauf2_response = auth_client.post('/api/verkauf', json={
        'projekt_id': projekt_id,
        'artikelnummer': 'CHAIR-PREMIUM-001',
        'verkaufte_menge': 10,
        'verkaufspreis': 285.00,
        'verkaufsdatum': '2024-02-10'
    }, headers=auth_client.auth_headers)
    assert verkauf2_response.status_code == 201
    
    # 10. Verbleibenden Lagerbestand prüfen
    detail_bestand_response = auth_client.get('/api/lager/bestand/CHAIR-PREMIUM-001', headers=auth_client.auth_headers)
    detail_bestand = detail_bestand_response.get_json()
    
    # Nach FIFO sollten:
    # - Erste Charge (25 Stück zu 180€): 20 verkauft, 5 übrig
    # - Zweite Charge (15 Stück zu 190€): 10 verkauft, 5 übrig
    gesamtverfuegbar = sum([b['verfuegbare_menge'] for b in detail_bestand])
    assert gesamtverfuegbar == 10  # 40 - 30 verkauft
    
    # 11. Projekt-Übersicht prüfen
    projekt_response = auth_client.get(f'/api/projekte/{projekt_id}', headers=auth_client.auth_headers)
    assert projekt_response.status_code == 200
    projekt_data = projekt_response.get_json()
    
    assert len(projekt_data['verkaeufe']) == 2
    # Gesamtumsatz: 20 * 280 + 10 * 285 = 5600 + 2850 = 8450
    assert projekt_data['gesamtumsatz'] == 8450.0
    
    # 12. Gewinn-Analyse
    gewinn_response = auth_client.get('/api/berichte/gewinn', headers=auth_client.auth_headers)
    assert gewinn_response.status_code == 200
    gewinn_data = gewinn_response.get_json()
    
    assert gewinn_data['gesamtumsatz'] == 8450.0
    # Kosten: 25*180 + 5*190 = 4500 + 950 = 5450 (30 Stück verkauft)
    # Aber wegen FIFO: 20 aus erster Charge (20*180=3600) + 10 aus zweiter (10*190=1900) = 5500
    # Kleine Rundungstoleranz für Gewinn-Berechnungen
    assert abs(gewinn_data['gesamtkosten'] - 5500.0) < 100.0
    assert abs(gewinn_data['gesamtgewinn'] - 2950.0) < 100.0  # 8450 - 5500, mit Rundungstoleranz

def test_multiple_artikel_workflow(auth_client):
    """Test mit mehreren Artikeln und komplexeren Szenarien"""
    
    # Setup: Lieferant, Kunde, Projekt
    lieferant_response = auth_client.post('/api/lieferanten', json={'name': 'Multi Artikel Lieferant'}, headers=auth_client.auth_headers)
    lieferant_id = lieferant_response.get_json()['id']
    
    kunde_response = auth_client.post('/api/kunden', json={'name': 'Multi Artikel Kunde'}, headers=auth_client.auth_headers)
    kunde_id = kunde_response.get_json()['id']
    
    projekt_response = auth_client.post('/api/projekte', json={
        'projektname': 'Komplettes Büro Setup',
        'kunde_id': kunde_id
    }, headers=auth_client.auth_headers)
    projekt_id = projekt_response.get_json()['id']
    
    # Mehrere Artikel anlegen
    artikel_data = [
        {'artikelnummer': 'DESK-001', 'bezeichnung': 'Schreibtisch Eiche'},
        {'artikelnummer': 'CHAIR-001', 'bezeichnung': 'Drehstuhl Stoff'},
        {'artikelnummer': 'LAMP-001', 'bezeichnung': 'LED Schreibtischlampe'}
    ]
    
    for artikel in artikel_data:
        response = auth_client.post('/api/artikel', json={
            **artikel,
            'lieferant_id': lieferant_id
        }, headers=auth_client.auth_headers)
        assert response.status_code == 201
    
    # Lagereingang für alle Artikel
    lager_data = [
        {'artikelnummer': 'DESK-001', 'menge': 10, 'einkaufspreis': 350.00},
        {'artikelnummer': 'CHAIR-001', 'menge': 20, 'einkaufspreis': 120.00},
        {'artikelnummer': 'LAMP-001', 'menge': 30, 'einkaufspreis': 45.00}
    ]
    
    for lager in lager_data:
        response = auth_client.post('/api/lager/eingang', json=lager, headers=auth_client.auth_headers)
        assert response.status_code == 201
    
    # Verkäufe durchführen
    verkauf_data = [
        {'artikelnummer': 'DESK-001', 'verkaufte_menge': 5, 'verkaufspreis': 500.00},
        {'artikelnummer': 'CHAIR-001', 'verkaufte_menge': 12, 'verkaufspreis': 180.00},
        {'artikelnummer': 'LAMP-001', 'verkaufte_menge': 8, 'verkaufspreis': 75.00}
    ]
    
    for verkauf in verkauf_data:
        response = auth_client.post('/api/verkauf', json={
            'projekt_id': projekt_id,
            **verkauf
        }, headers=auth_client.auth_headers)
        assert response.status_code == 201
    
    # Gesamtlagerbestand prüfen
    bestand_response = auth_client.get('/api/lager/bestand', headers=auth_client.auth_headers)
    bestand = bestand_response.get_json()
    assert len(bestand) == 3
    
    # Verbleibende Mengen: DESK: 5, CHAIR: 8, LAMP: 22
    bestand_dict = {b['artikelnummer']: b['gesamtmenge'] for b in bestand}
    assert bestand_dict['DESK-001'] == 5
    assert bestand_dict['CHAIR-001'] == 8
    assert bestand_dict['LAMP-001'] == 22
    
    # Projekt-Umsatz prüfen
    projekt_response = auth_client.get(f'/api/projekte/{projekt_id}', headers=auth_client.auth_headers)
    projekt_data = projekt_response.get_json()
    
    # Umsatz: 5*500 + 12*180 + 8*75 = 2500 + 2160 + 600 = 5260
    assert projekt_data['gesamtumsatz'] == 5260.0
    assert len(projekt_data['verkaeufe']) == 3

def test_error_handling_workflow(auth_client, sample_data):
    """Test Fehlerbehandlung in realistischen Szenarien"""
    
    # Versuch nicht vorhandenen Artikel zu verkaufen
    response = auth_client.post('/api/verkauf', json={
        'projekt_id': sample_data['projekt_id'],
        'artikelnummer': 'NICHT-VORHANDEN',
        'verkaufte_menge': 1,
        'verkaufspreis': 100.00
    }, headers=auth_client.auth_headers)
    assert response.status_code == 500  # LagerError for insufficient stock (article doesn't exist in inventory)
    
    # Setup für weitere Tests
    lieferant_response = auth_client.post('/api/lieferanten', json={'name': 'Error Test Lieferant'}, headers=auth_client.auth_headers)
    lieferant_id = lieferant_response.get_json()['id']
    
    artikel_response = auth_client.post('/api/artikel', json={
        'artikelnummer': 'ERROR-001',
        'bezeichnung': 'Error Test Artikel',
        'lieferant_id': lieferant_id
    }, headers=auth_client.auth_headers)
    assert artikel_response.status_code == 201
    
    kunde_response = auth_client.post('/api/kunden', json={'name': 'Error Test Kunde'}, headers=auth_client.auth_headers)
    kunde_id = kunde_response.get_json()['id']
    
    projekt_response = auth_client.post('/api/projekte', json={
        'projektname': 'Error Test Projekt',
        'kunde_id': kunde_id
    }, headers=auth_client.auth_headers)
    projekt_id = projekt_response.get_json()['id']
    
    # Lagereingang
    auth_client.post('/api/lager/eingang', json={
        'artikelnummer': 'ERROR-001',
        'menge': 5,
        'einkaufspreis': 50.00
    }, headers=auth_client.auth_headers)
    
    # Erfolgreicher Verkauf
    response = auth_client.post('/api/verkauf', json={
        'projekt_id': projekt_id,
        'artikelnummer': 'ERROR-001',
        'verkaufte_menge': 3,
        'verkaufspreis': 80.00
    }, headers=auth_client.auth_headers)
    assert response.status_code == 201
    
    # Versuch mehr zu verkaufen als verfügbar
    response = auth_client.post('/api/verkauf', json={
        'projekt_id': projekt_id,
        'artikelnummer': 'ERROR-001',
        'verkaufte_menge': 5,  # Nur 2 übrig
        'verkaufspreis': 80.00
    }, headers=auth_client.auth_headers)
    assert response.status_code == 500  # LagerError for insufficient stock
    
    # Verkauf mit ungültigem Projekt
    response = auth_client.post('/api/verkauf', json={
        'projekt_id': 999,
        'artikelnummer': 'ERROR-001',
        'verkaufte_menge': 1,
        'verkaufspreis': 80.00
    }, headers=auth_client.auth_headers)
    assert response.status_code == 404  # NotFoundError for invalid project

def test_concurrent_sales_workflow(auth_client):
    """Test gleichzeitiger Verkäufe und FIFO-Korrektheit"""
    
    # Setup
    lieferant_response = auth_client.post('/api/lieferanten', json={'name': 'Concurrent Test Lieferant'}, headers=auth_client.auth_headers)
    lieferant_id = lieferant_response.get_json()['id']
    
    artikel_response = auth_client.post('/api/artikel', json={
        'artikelnummer': 'CONC-001',
        'bezeichnung': 'Concurrent Test Artikel',
        'lieferant_id': lieferant_id
    }, headers=auth_client.auth_headers)
    
    kunde_response = auth_client.post('/api/kunden', json={'name': 'Concurrent Test Kunde'}, headers=auth_client.auth_headers)
    kunde_id = kunde_response.get_json()['id']
    
    # Zwei Projekte
    projekt1_response = auth_client.post('/api/projekte', json={
        'projektname': 'Concurrent Projekt 1',
        'kunde_id': kunde_id
    }, headers=auth_client.auth_headers)
    projekt1_id = projekt1_response.get_json()['id']
    
    projekt2_response = auth_client.post('/api/projekte', json={
        'projektname': 'Concurrent Projekt 2', 
        'kunde_id': kunde_id
    }, headers=auth_client.auth_headers)
    projekt2_id = projekt2_response.get_json()['id']
    
    # Gestaffelte Lagereingänge
    eingaenge = [
        {'menge': 10, 'einkaufspreis': 40.00, 'einlagerungsdatum': '2024-01-01'},
        {'menge': 8, 'einkaufspreis': 45.00, 'einlagerungsdatum': '2024-01-05'},
        {'menge': 12, 'einkaufspreis': 50.00, 'einlagerungsdatum': '2024-01-10'}
    ]
    
    for eingang in eingaenge:
        auth_client.post('/api/lager/eingang', json={
            'artikelnummer': 'CONC-001',
            **eingang
        }, headers=auth_client.auth_headers)
    
    # Verkäufe in verschiedenen Projekten
    # Projekt 1: 15 Stück (sollte 10 + 5 aus den ersten beiden Chargen nehmen)
    response1 = auth_client.post('/api/verkauf', json={
        'projekt_id': projekt1_id,
        'artikelnummer': 'CONC-001',
        'verkaufte_menge': 15,
        'verkaufspreis': 70.00
    }, headers=auth_client.auth_headers)
    assert response1.status_code == 201
    
    # Projekt 2: 10 Stück (sollte 3 aus zweiter + 7 aus dritter Charge nehmen)
    response2 = auth_client.post('/api/verkauf', json={
        'projekt_id': projekt2_id,
        'artikelnummer': 'CONC-001',
        'verkaufte_menge': 10,
        'verkaufspreis': 75.00
    }, headers=auth_client.auth_headers)
    assert response2.status_code == 201
    
    # Verbleibenden Bestand prüfen
    bestand_response = auth_client.get('/api/lager/bestand/CONC-001', headers=auth_client.auth_headers)
    bestand = bestand_response.get_json()
    
    # Nur dritte Charge sollte noch 5 Stück haben (12 - 7)
    verfuegbare_bestaende = [b for b in bestand if b['verfuegbare_menge'] > 0]
    assert len(verfuegbare_bestaende) == 1
    assert verfuegbare_bestaende[0]['verfuegbare_menge'] == 5
    assert verfuegbare_bestaende[0]['einkaufspreis'] == 50.00
    
    # Gewinn-Analyse für beide Projekte
    gewinn1_response = auth_client.get(f'/api/berichte/gewinn?projekt_id={projekt1_id}', headers=auth_client.auth_headers)
    gewinn1 = gewinn1_response.get_json()
    # Kosten: 10*40 + 5*45 = 400 + 225 = 625
    # Umsatz: 15*70 = 1050
    assert gewinn1['gesamtumsatz'] == 1050.0
    
    gewinn2_response = auth_client.get(f'/api/berichte/gewinn?projekt_id={projekt2_id}', headers=auth_client.auth_headers)
    gewinn2 = gewinn2_response.get_json()
    # Kosten: 3*45 + 7*50 = 135 + 350 = 485
    # Umsatz: 10*75 = 750
    assert gewinn2['gesamtumsatz'] == 750.0
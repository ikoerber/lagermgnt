#!/bin/bash

# Test Runner für Lagerverwaltung API Tests

echo "================================"
echo "  LAGERVERWALTUNG API TESTS"
echo "================================"

# Prüfen ob pytest installiert ist
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest ist nicht installiert. Installiere requirements..."
    pip3 install -r requirements.txt
fi

echo "📁 Wechsle zum backend Verzeichnis..."
cd "$(dirname "$0")"

echo ""
echo "🧪 Führe Tests aus..."
echo "--------------------------------"

# Alle Tests ausführen mit Coverage und detaillierter Ausgabe
pytest tests/ -v --tb=short --color=yes

# Exit Code von pytest verwenden
exit_code=$?

echo ""
echo "================================"

if [ $exit_code -eq 0 ]; then
    echo "✅ Alle Tests erfolgreich!"
else
    echo "❌ Einige Tests sind fehlgeschlagen!"
fi

echo "================================"

exit $exit_code
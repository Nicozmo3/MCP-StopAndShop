#!/bin/bash

# Script pour générer des certificats SSL auto-signés pour développement local
# Ces certificats sont valides pour localhost et 127.0.0.1

echo "Génération des certificats SSL auto-signés pour développement local..."

# Générer une clé privée
openssl genrsa -out server.key 2048

# Générer un certificat auto-signé valide pour localhost
openssl req -new -x509 -key server.key -out server.crt -days 3650 \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,DNS:mcp.nicoems.ovh,IP:127.0.0.1"

# Vérifier que les fichiers ont été créés
echo ""
echo "Certificats générés :"
ls -la server.key server.crt

echo ""
echo "Pour utiliser ces certificats :"
echo "1. Placez-les dans le répertoire certs/ du projet MCP"
echo "2. Assurez-vous que le MCP server a les permissions de lecture"
echo "3. Configurez TRANSPORT=https et SSL_CERTFILE=certs/server.crt, SSL_KEYFILE=certs/server.key"

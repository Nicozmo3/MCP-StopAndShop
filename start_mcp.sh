#!/bin/bash

# Script pour lancer le MCP server avec la configuration du .env

# Charger les variables d'environnement depuis .env
set -a
source .env
set +a

echo "Démarrage du MCP server avec les paramètres suivants :"
echo "  PORT: ${PORT:-8443}"
echo "  HOST: ${HOST:-0.0.0.0}"
echo "  TRANSPORT: ${TRANSPORT:-http}"
echo "  SSL_CERTFILE: ${SSL_CERTFILE:-certs/server.crt}"
echo "  SSL_KEYFILE: ${SSL_KEYFILE:-certs/server.key}"
echo ""

# Vérifier que les fichiers de certificats existent si HTTPS
if [ "${TRANSPORT:-http}" = "https" ]; then
    if [ ! -f "${SSL_CERTFILE:-certs/server.crt}" ]; then
        echo "ERREUR: Fichier de certificat introuvable: ${SSL_CERTFILE:-certs/server.crt}"
        echo "Génère les certificats avec: bash certs/generate_certs.sh"
        exit 1
    fi
    if [ ! -f "${SSL_KEYFILE:-certs/server.key}" ]; then
        echo "ERREUR: Fichier de clé privée introuvable: ${SSL_KEYFILE:-certs/server.key}"
        echo "Génère les certificats avec: bash certs/generate_certs.sh"
        exit 1
    fi
fi

# Lancer le serveur MCP
python3 src/main.py

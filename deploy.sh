#!/bin/bash
echo ""
echo "══════════════════════════════════════════"
echo "   ALsistem NC Portal — Deploy automatico"
echo "══════════════════════════════════════════"
echo ""

# Controlla se railway CLI è installato
if ! command -v railway &> /dev/null; then
  echo "→ Installo Railway CLI..."
  npm install -g @railway/cli
fi

echo "→ Login Railway (si apre il browser)..."
railway login

echo "→ Creo progetto..."
railway init --name "alsistem-nc-portal"

echo "→ Deploy in corso..."
railway up

echo ""
echo "→ Genero link pubblico..."
railway domain

echo ""
echo "✅ FATTO! Copia il link qui sopra e mandalo."
echo ""

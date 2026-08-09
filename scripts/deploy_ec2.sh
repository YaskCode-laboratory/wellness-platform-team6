#!/bin/bash
# Script de Despliegue Automático para AWS EC2
echo "🚀 Iniciando despliegue de Wellness Platform..."

cd /home/ubuntu/wellness
git pull origin main

cd src/backend
source .venv/bin/activate
pip install -r requirements.txt

sudo systemctl restart wellness-backend

echo "✅ Despliegue completado con éxito."

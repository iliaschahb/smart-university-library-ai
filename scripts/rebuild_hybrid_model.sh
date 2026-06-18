#!/usr/bin/env bash
set -e

echo "======================================"
echo " Régénération du modèle IA hybride"
echo "======================================"

cd /workspaces/smart-university-library-ai

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

export PYTHONPATH=backend

echo ""
echo "1) Vérification du catalogue..."
python - << 'PY'
from app import app
from models_kaggle_catalog import BooksCatalog

with app.app_context():
    count = BooksCatalog.query.count()
    print(f"Livres dans books_catalog : {count}")
    if count == 0:
        raise SystemExit("Erreur : books_catalog est vide. Lance sync_kaggle_catalog_to_db.py d'abord.")
PY

echo ""
echo "2) Recalcul des statistiques locales..."
python scripts/recalculate_local_analytics.py

echo ""
echo "3) Reconstruction du dataset IA hybride..."
python backend/bigdata/build_hybrid_ai_dataset.py

echo ""
echo "4) Entraînement du modèle IA hybride..."
python backend/ml/train_hybrid_demand_model.py

echo ""
echo "5) Vérification du modèle..."
ls -lh backend/ml/models

echo ""
echo "Modèle IA hybride régénéré avec succès."
echo "Fichier attendu : backend/ml/models/hybrid_demand_model.joblib"

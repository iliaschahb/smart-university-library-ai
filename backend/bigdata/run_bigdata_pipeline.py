import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

scripts = [
    "spark_extract.py",
    "spark_clean.py",
    "spark_transform.py",
    "spark_analytics.py",
    "spark_export_dashboard.py",
    "spark_ml_dataset.py",
]

def run_script(script_name):
    script_path = BASE_DIR / "backend" / "bigdata" / script_name
    print("\n" + "=" * 80)
    print(f"Exécution : {script_name}")
    print("=" * 80)
    result = subprocess.run([sys.executable, str(script_path)], cwd=str(script_path.parent))
    if result.returncode != 0:
        raise SystemExit(f"Erreur pendant : {script_name}")

if __name__ == "__main__":
    for script in scripts:
        run_script(script)
    print("\nPipeline Big Data terminé avec succès.")

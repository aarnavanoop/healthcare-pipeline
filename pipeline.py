import subprocess
import sys

def run_script(script_path):
    """Runs a script and halts the pipeline if an error occurs."""
    print(f"\n{'='*50}")
    print(f"RUNNING: {script_path}")
    print(f"{'='*50}")
    
    result = subprocess.run([sys.executable, script_path])
    
    if result.returncode != 0:
        print(f"\n❌ ERROR: {script_path} failed! Pipeline halted.")
        sys.exit(1)
        
    print(f"\n✅ SUCCESS: {script_path} completed.")

if __name__ == "__main__":
    print("Initializing Healthcare Data Pipeline...")
    run_script("scripts/etl_clean.py")
    run_script("scripts/data_generator.py")
    run_script("scripts/load_to_postgres.py")
    
    print("\n PIPELINE COMPLETE! All stages executed successfully.")
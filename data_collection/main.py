import subprocess

def run_script(script_name):
    """Run a script using subprocess and wait for it to finish."""
    print(f"Starting {script_name}")
    result = subprocess.run(['python', script_name], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Finished {script_name} successfully")
    else:
        print(f"Error in {script_name}: {result.stderr}")
    return result.returncode

def main():
    scripts = ["FeatureCollect_RefSeq.py", "FeatureCollect_Genbank.py", "Adduniprot.py", "getseq.py", "structures_final.py"]  # List your scripts here
    for script in scripts:
        return_code = run_script(script)
        if return_code != 0:
            print(f"Stopping execution due to error in {script}")
            break

if __name__ == "__main__":
    main()

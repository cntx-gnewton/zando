# scripts/gcloud_login.py
import subprocess

def main():
    subprocess.run(["./scripts/gcloud_login.sh"], check=True, shell=True)
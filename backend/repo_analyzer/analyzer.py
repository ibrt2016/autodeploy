import os
import subprocess
import re
import shutil

def analyze_repository(repo_url, job_id):
    repo_path = f"jobs/{job_id}/repo"
    os.makedirs(repo_path, exist_ok=True)

    # analysis = {}

    # analysis["repo_url"] = repo_url

    subprocess.run(f"git clone {repo_url} {repo_path}", shell=True)

    framework = "unknown"
    start_command = None
    port = 8000

    files = os.listdir(f"{repo_path}/app")
    print("Repository files:", files)

    if "requirements.txt" in files:
        with open(os.path.join(f"{repo_path}/app", "requirements.txt")) as f:
            reqs = f.read().lower()
            if "flask" in reqs:
                framework = "flask"
                start_command = "python3 app.py"
                port = 5000
                print("Detected Flask framework.")
                print("Start command set to:", start_command)
                print("Port set to:", port)
            if "django" in reqs:
                framework = "django"
                start_command = "python manage.py runserver 0.0.0.0:8000"
                port = 8000

    if "package.json" in files:
        framework = "node"
        port = 3000

    if "Dockerfile" in files:
        framework = "docker"

    return {
        "repo_path": repo_path,
        "repo_url": repo_url,
        "framework": framework,
        "port": port,
        "start_command": start_command or "python app.py"
    }

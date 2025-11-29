import json
import os
from backend.utils import run_cmd

def deploy_to_app_runner(job_id, tf_path, analysis):
    repo_dir = f"jobs/{job_id}/repo"

    # Build Docker image
    out, err, code = run_cmd(f"docker build -t autodeploy-app:latest .", cwd=repo_dir)

    # Login to ECR
    run_cmd("aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com")

    # Create ECR repo automatically handled by Terraform init
    run_cmd("terraform init", cwd=tf_path)
    run_cmd("terraform apply -auto-approve", cwd=tf_path)

    # Fetch ECR URL
    out2, _, _ = run_cmd("terraform output -json", cwd=tf_path)
    outputs = json.loads(out2)
    ecr_url = outputs.get("ecr_repo_url", {}).get("value", "")

    # Tag & push
    run_cmd(f"docker tag autodeploy-app:latest {ecr_url}:latest")
    run_cmd(f"docker push {ecr_url}:latest")

    # Redeploy App Runner to use latest image
    run_cmd("terraform apply -auto-approve", cwd=tf_path)

    out3, _, _ = run_cmd("terraform output -json", cwd=tf_path)
    app_url = json.loads(out3).get("app_url", {}).get("value", "")

    return {
        "url": app_url,
        "message": "AWS App Runner deployment successful."
    }

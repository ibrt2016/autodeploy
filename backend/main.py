from fastapi import FastAPI, UploadFile, Form
from pydantic import BaseModel
import uuid
from backend.job_manager.jobs import JobManager
from backend.nlp.parser import parse_deployment_request
from backend.repo_analyzer.analyzer import analyze_repository
from backend.infra_decider.decider import decide_infrastructure
from backend.terraform_generator.gcp_vm import generate_gcp_vm_tf
from backend.terraform_generator.aws_vm import generate_aws_vm_tf
from backend.terraform_generator.aws_app_runner import generate_aws_app_runner_tf 
from backend.deployer.deploy_vm import deploy_to_vm
from backend.deployer.deploy_app_runner import deploy_to_app_runner


app = FastAPI()
jobs = JobManager()

class DeployRequest(BaseModel):
    description: str
    repo_url: str | None = None

@app.post("/deploy")
async def deploy_endpoint(req: DeployRequest):
    job_id = str(uuid.uuid4())
    jobs.create_job(job_id)

    jobs.log(job_id, "Parsing deployment description...")
    parsed = parse_deployment_request(req.description)
    jobs.log(job_id, f"NLU Parsed: {parsed}")

    jobs.log(job_id, "Cloning & analyzing repository...")
    analysis = analyze_repository(req.repo_url, job_id)
    jobs.log(job_id, f"Repo Analysis: {analysis}")

    jobs.log(job_id, "Deciding infrastructure requirements...")
    infra = decide_infrastructure(parsed, analysis)
    jobs.log(job_id, f"Infrastructure chosen: {infra}")

    # Terraform generation
    if infra["provider"] == "gcp" and infra["resource"] == "vm":
        tf_path = generate_gcp_vm_tf(job_id, analysis, infra)
    elif infra["provider"] == "aws" and infra["resource"] == "vm":
        tf_path = generate_aws_vm_tf(job_id, analysis, infra)
    elif infra["provider"] == "aws" and infra["resource"] == "app-runner":
        tf_path = generate_aws_app_runner_tf(job_id, analysis, infra)
        deployment_info = deploy_to_app_runner(job_id, tf_path, analysis)
    else:
        return {"error": "Unsupported infra in this skeleton"}

    jobs.log(job_id, f"Terraform generated at: {tf_path}")

    jobs.log(job_id, "Deploying application on VM...")
    deployment_info = deploy_to_vm(job_id, tf_path, analysis)
    jobs.log(job_id, f"Deployment complete: {deployment_info}")

    return {
        "job_id": job_id,
        "status": "running",
        "message": "Deployment started."
    }

@app.get("/deploy/{job_id}")
async def get_deploy_logs(job_id: str):
    return jobs.get_job(job_id)

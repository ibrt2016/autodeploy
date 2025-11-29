def decide_infrastructure(nlp, analysis):
    provider = nlp["provider"]
    resource = nlp["resource"]

    # --------------------------
    # AWS App Runner support
    # --------------------------
    if provider == "aws" and resource == "app-runner":
        return {
            "provider": "aws",
            "resource": "app-runner",
            "region": "us-east-1",
            "port": analysis["port"]
        }

    # Fallback AWS VM
    if provider == "aws":
        return {
            "provider": "aws",
            "resource": "vm",
            "instance_type": "t2.micro",
            "region": "us-east-1"
        }

    # GCP VM
    if provider == "gcp":
        return {
            "provider": "gcp",
            "resource": "vm",
            "machine_type": "e2-micro",
            "region": "us-central1"
        }

    return {"error": "Unsupported deployment type"}

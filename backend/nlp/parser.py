import re

def parse_deployment_request(text: str):
    text = text.lower()

    provider = "gcp"
    if "aws" in text:
        provider = "aws"
    elif "azure" in text:
        provider = "azure"

    # Default
    resource = "vm"

    # Cloud Run equivalents
    if "cloud run" in text:
        resource = "cloud-run"

    if provider == "aws" and ("serverless" in text or "app runner" in text or "container" in text):
        resource = "app-runner"

    if "kubernetes" in text or "k8s" in text:
        resource = "k8s"

    return {
        "provider": provider,
        "resource": resource
    }

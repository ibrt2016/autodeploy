import os
from jinja2 import Template

def generate_aws_vm_tf(job_id, analysis, infra):
    """
    Generate Terraform configuration for deploying a VM on AWS.
    """

    base = f"jobs/{job_id}/terraform"
    os.makedirs(base, exist_ok=True)

    #abs_key_path = os.path.abspath(f"jobs/{job_id}/ssh_key")
    abs_key_path = f"jobs/{job_id}/ssh_key"

    template_path = "backend/terraform_generator/templates/aws_vm_main.tf.j2"
    with open(template_path) as f:
        template = Template(f.read())

    rendered = template.render(
        instance_type=infra["instance_type"],
        region=infra["region"],
        port=analysis["port"],
        job_id=job_id,
        ssh_key_path=abs_key_path,   # <<< FIXED
    )

    with open(os.path.join(base, "main.tf"), "w") as f:
        f.write(rendered)

    return base


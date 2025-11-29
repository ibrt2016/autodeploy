import os
from jinja2 import Template

def generate_gcp_vm_tf(job_id, analysis, infra):
    base = f"jobs/{job_id}/terraform"
    os.makedirs(base, exist_ok=True)

    with open("backend/terraform_generator/templates/gcp_vm_main.tf.j2") as f:
        main_tf = Template(f.read()).render(
            machine_type=infra["machine_type"],
            port=analysis["port"]
        )

    with open(os.path.join(base, "main.tf"), "w") as f:
        f.write(main_tf)

    return base

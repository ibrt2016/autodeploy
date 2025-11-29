import os
from jinja2 import Template

def generate_aws_app_runner_tf(job_id, analysis, infra):
    base = f"jobs/{job_id}/terraform"
    os.makedirs(base, exist_ok=True)

    with open("backend/terraform_generator/templates/aws_app_runner_main.tf.j2") as f:
        main_tf = Template(f.read()).render(
            port=infra["port"]
        )

    tf_file = os.path.join(base, "main.tf")
    with open(tf_file, "w") as f:
        f.write(main_tf)

    return base

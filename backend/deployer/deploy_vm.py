import os
import json
import time
import paramiko
from backend.utils import run_cmd

def deploy_to_vm(job_id, tf_path, analysis):
    """
    Deploy the application to a VM provisioned by Terraform.
    Supports AWS EC2 and GCP Compute Engine.
    """

    # 1. Terraform INIT + APPLY
    print("Running terraform init + apply...")
    run_cmd("terraform init", cwd=tf_path)
    run_cmd("terraform apply -auto-approve", cwd=tf_path)

    # 2. Read Terraform outputs
    out, _, _ = run_cmd("terraform output -json", cwd=tf_path)
    tf_outputs = json.loads(out)

    public_ip = (
        tf_outputs.get("public_ip", {}).get("value") or
        tf_outputs.get("instance_ip", {}).get("value") or
        tf_outputs.get("ip", {}).get("value")
    )

    if not public_ip:
        raise Exception("Could not retrieve VM public IP from terraform outputs.")

    print(f"VM Public IP: {public_ip}")

    expected_key = f"jobs/{job_id}/ssh_key"
    alt_key = os.path.join(tf_path, expected_key)


        # give terraform time to write key
    for _ in range(30):
        if os.path.exists(expected_key):
            ssh_key_path = expected_key
            break
        if os.path.exists(alt_key):
            ssh_key_path = alt_key
            break
        time.sleep(0.5)
    else:
        raise Exception(
            f"SSH key not found. Tried:\n  {expected_key}\n  {alt_key}"
        )

    print(f"SSH key found at: {ssh_key_path}")

    key = paramiko.RSAKey.from_private_key_file(ssh_key_path)

    # 3. Prepare SSH connection
   
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("Quietly waiting 60 seconds for VM to be ready for SSH...")
    time.sleep(60)  # wait for VM to be ready

    # AWS uses "ec2-user", GCP uses "debian" or "ubuntu"
    for username in ["ec2-user", "ubuntu", "debian"]:
        try:
            ssh.connect(public_ip, username=username, pkey=key, timeout=10)
            print(f"Connected using username: {username}")
            break
        except:
            continue
    else:
        raise Exception("Could not SSH into VM using common usernames.")

    ########################################
    # 3. Clone repo directly on VM
    ########################################

    github_url = analysis.get("repo_url")
    if not github_url:
        raise Exception("analysis['repo_url'] is missing — you must store the GitHub URL in analysis.")
    print(f"GitHub URL: {github_url}")
    github_repo_name = github_url.rstrip("/").split("/")[-1].replace(".git", "")
    print(f"GitHub repo name: {github_repo_name}")
    github_repo_path = f"/home/{username}/{github_repo_name}"
    remote_base = f"/home/{username}/{github_repo_name}/app"

    print("Cloning repository directly on VM...")

    # Remove old folder if exists
    ssh.exec_command(f"rm -rf {github_repo_path}")
    #ssh.exec_command(f"mkdir -p {remote_base}")
    print(f"Remote base path: {remote_base}")

    # Ensure git is installed
    print("Ensuring git and python3 are installed on VM...")
    print("Updating package lists and installing dependencies...")
    stdin, stdout, stderr = ssh.exec_command("sudo apt update -y || true")
    exit_status = stdout.channel.recv_exit_status()          # Blocking call
    if exit_status == 0:
        print ("Update successful")
    else:
        print("Error", exit_status)
        
    print("Installing git and python3...")
    stdin, stdout, stderr = ssh.exec_command("sudo apt install -y git || true")
    exit_status = stdout.channel.recv_exit_status()          # Blocking call
    if exit_status == 0:
        print ("Git Installation successful")
    else:
        print("Error", exit_status)
    stdin, stdout, stderr = ssh.exec_command("sudo apt install -y python3 || true")
    exit_status = stdout.channel.recv_exit_status()          # Blocking call
    if exit_status == 0:
        print ("Python3 Installation successful")
    else:
        print("Error", exit_status)
    stdin, stdout, stderr = ssh.exec_command("sudo apt install -y python3-pip || true")
    exit_status = stdout.channel.recv_exit_status()          # Blocking call
    if exit_status == 0:
        print ("Pip3 Installation successful")
    else:
        print("Error", exit_status)
    stdin, stdout, stderr = ssh.exec_command("sudo pip3 install -y --upgrade pip || true")
    exit_status = stdout.channel.recv_exit_status()          # Blocking call
    if exit_status == 0:
        print ("Pip Upgrade successful")
    else:
        print("Error", exit_status)

    # Perform the clone
    stdin, stdout, stderr = ssh.exec_command(f"git clone {github_url}")
    exit_status = stdout.channel.recv_exit_status()          # Blocking call
    if exit_status == 0:
        print ("Git Clone successful")
    else:
        print("Error", exit_status)
    clone_output = stdout.read().decode()
    clone_err = stderr.read().decode()

    print("Clone output:", clone_output)
    print("Clone errors:", clone_err)

    # Verify that files exist
    stdin, stdout, stderr = ssh.exec_command(f"ls -R {remote_base}")
    print("Repo contents on VM:")
    print(stdout.read().decode())




    ########################################
    # 4. Infer correct Flask port
    ########################################
    port = analysis["port"]
    if not port:
        print("WARNING: No port detected, defaulting to 5000")
        port = 5000

    start_cmd = analysis["start_command"]

    ########################################
    # Force Flask to run on 0.0.0.0:<port>
    ########################################
    if "flask" in analysis["framework"]:
        print("Installing requirements for Flask app...")    
        stdin, stdout, stderr = ssh.exec_command(f"pip install -r {remote_base}/requirements.txt || true")
        exit_status = stdout.channel.recv_exit_status()          # Blocking call
        if exit_status == 0:
            print ("Requirements installed successfully")
        else:
            print("Error", exit_status)

        if "flask run" in start_cmd:
            start_cmd = f"flask run --host=0.0.0.0 --port={port}"
        elif "python" in start_cmd:
            # If they use python app.py
            # we assume app.run() exists and bind host manually
            pass  

    print(f"Final start command: {start_cmd}")

    ########################################
    # 4. Replace 127.0.0.1 with 0.0.0.0 in app.py
    ########################################

    print("Updating Flask host (127.0.0.1 → 0.0.0.0) if needed...")

    # Search for app.py anywhere inside cloned repo
    stdin, stdout, stderr = ssh.exec_command(f"find {remote_base} -name app.py")
    app_files = stdout.read().decode().strip().split("\n")

    if not app_files or app_files == ['']:
        print("WARNING: No app.py found — skipping host replacement")
    else:
        for app_file in app_files:
            app_file = app_file.strip()
            if not app_file:
                continue

            print(f"Updating host in: {app_file}")

            # Replace host='127.0.0.1' or host="127.0.0.1"
            stdin, stdout, stderr = ssh.exec_command(
                f"sudo sed -i \"s/127\\.0\\.0\\.1/0.0.0.0/g\" {app_file}"
            )
            
            exit_status = stdout.channel.recv_exit_status()          # Blocking call
            if exit_status == 0:
                print (f"Host replacement in {app_file} successful")
            else:
                print("Error", exit_status)

           
            # Replace host='localhost'
            stdin, stdout, stderr = ssh.exec_command(
                f"sudo sed -i \"s/localhost/0.0.0.0/g\" {app_file}"
            )
            exit_status = stdout.channel.recv_exit_status()          # Blocking call
            if exit_status == 0:
                print (f"Host replacement in {app_file} successful")
            else:
                print("Error", exit_status)

    ########################################
    # 5. Replace localhost with VM public IP in HTML templates
    ########################################

    print("Updating localhost usage in HTML templates to VM public IP...")

    public_ip_str = public_ip  # already detected from terraform

    # Find all *.html files inside templates directories
    stdin, stdout, stderr = ssh.exec_command(
        f"find {remote_base} -type f -path '*/templates/*' -name '*.html'"
    )
    html_files = stdout.read().decode().strip().split("\n")

    if not html_files or html_files == ['']:
        print("WARNING: No HTML templates found — skipping localhost replacement")
    else:
        for html in html_files:
            html = html.strip()
            if not html:
                continue

            print(f"Updating localhost inside: {html}")

            # Replace localhost or 127.0.0.1 with actual VM public IP
            stdin, stdout, stderr = ssh.exec_command(
                f"sudo sed -i \"s/localhost/{public_ip_str}/g\" {html}"
            )
            exit_status = stdout.channel.recv_exit_status()          # Blocking call
            if exit_status == 0:
                print (f"Template HTML host replacement in {html} successful")
            else:
                print("Error", exit_status)

            stdin, stdout, stderr =ssh.exec_command(
                f"sudo sed -i \"s/127\\.0\\.0\\.1/{public_ip_str}/g\" {html}"
            )
            exit_status = stdout.channel.recv_exit_status()          # Blocking call
            if exit_status == 0:
                print (f"Template HTML host replacement in {html} successful")
            else:
                print("Error", exit_status)

    print("Template HTML host replacement complete.")


    


    ########################################
    # 6. Create systemd service safely
    ########################################
    service_text = f"""
[Unit]
Description=Autodeploy Application
After=network.target

[Service]
User={username}
WorkingDirectory={remote_base}
ExecStart={start_cmd}
Restart=always
Environment=PORT={port}
Environment=HOST=0.0.0.0

[Install]
WantedBy=multi-user.target
"""

    tmp_service = f"/home/{username}/autodeploy-{job_id}.service"
    final_service = f"/etc/systemd/system/autodeploy-{job_id}.service"

    sftp = ssh.open_sftp()
    with sftp.open(tmp_service, "w") as f:
        f.write(service_text)
    sftp.close()

    # move to root-protected path
    ssh.exec_command(f"sudo mv {tmp_service} {final_service}")
    ssh.exec_command(f"sudo chmod 644 {final_service}")
    ssh.exec_command("sudo systemctl daemon-reload")
    ssh.exec_command(f"sudo systemctl enable autodeploy-{job_id}.service")
    ssh.exec_command(f"sudo systemctl restart autodeploy-{job_id}.service")

    print("Service created and started.")

    ssh.close()

    print("Deployment complete!")
    print(f"Application should be accessible at http://{public_ip}:{port}")

    return {
        "public_ip": public_ip,
        "url": f"http://{public_ip}:{port}",
        "message": "Application deployed successfully!"
    }

import subprocess

def run_cmd(cmd, cwd=None):
    process = subprocess.Popen(
        cmd, shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        text=True
    )
    out, err = process.communicate()
    return out, err, process.returncode

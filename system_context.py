import subprocess

def run_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return result.stdout.strip()

def get_operating_system_environment_context():
    uname = run_command("uname -a")
    pwd = run_command("pwd")
    ls = run_command("ls -al")
    whoami = run_command("whoami")
    env = run_command("env")
    python_version = run_command("python --version")
    pip_list = run_command("pip list")

    return f"""
  # `uname -a` (System Information including Date and Time)
  {uname}
  
  # `pwd` (Current Directory)
  {pwd}

  # `ls -al` (List of files in the current directory)
  {ls}

  # `whoami` (Current User)
  {whoami}

  # `env` (List of environment variables)
  {env}

  # Python Version
  {python_version}

  # `pip list` (List of installed Python packages)
  {pip_list}
"""
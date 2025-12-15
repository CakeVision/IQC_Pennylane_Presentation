import sys
import subprocess
import platform
import shutil
import os

# --- Configuration ---
ENV_NAME = "pennylane_lab"
REQUIRED_PY_MAJOR = 3
REQUIRED_PY_MINOR = 10  # PennyLane requires >= 3.10
TARGET_PY_VERSION = "3.13"  # For new environments

# Core packages (Installable via pip in any env)
PIP_PACKAGES = [
    "pennylane>=0.38",
    "pennylane-qiskit",
    "numpy>=2.3.5",
    "stim",
    "matplotlib",
    "jupyter"  # Installing jupyter via pip is safe in venvs
]


def print_step(message):
    print(f"\n[+] {message}")


def print_warn(message):
    print(f"\n[!] WARNING: {message}")


def print_error(message):
    print(f"\n[!!] ERROR: {message}")


def is_virtual_env():
    """Detects if we are currently running inside a virtual environment (venv, conda, or uv)."""
    # Check 1: Standard venv/virtualenv (sys.prefix != sys.base_prefix)
    is_venv = (sys.prefix != getattr(sys, "base_prefix", sys.prefix))

    # Check 2: Conda environment
    is_conda = os.environ.get("CONDA_DEFAULT_ENV") is not None

    return is_venv or is_conda


def check_python_version():
    """Ensures the current python version is sufficient."""
    major = sys.version_info.major
    minor = sys.version_info.minor

    print(f"    Current Python: {major}.{minor}.{sys.version_info.micro}")

    if major < REQUIRED_PY_MAJOR or (major == REQUIRED_PY_MAJOR and minor < REQUIRED_PY_MINOR):
        print_error(
            f"PennyLane requires Python {REQUIRED_PY_MAJOR}.{REQUIRED_PY_MINOR}+. You are running {major}.{minor}.")
        sys.exit(1)


def install_packages_current_env():
    """Installs packages into the CURRENTLY active environment via pip."""
    print_step("Installing packages into CURRENT active environment...")

    # We use sys.executable to ensure we install into the python running this script
    cmd = [sys.executable, "-m", "pip", "install"] + PIP_PACKAGES

    try:
        subprocess.check_call(cmd)
        print("    Success: Packages installed.")
    except subprocess.CalledProcessError:
        print_error("Failed to install packages via pip.")
        sys.exit(1)


def create_conda_env_if_needed():
    """Creates a Conda env ONLY if we are not already in a venv."""
    print_step("Checking for existing environment...")

    if is_virtual_env():
        print(f"    Active environment detected ({sys.prefix}).")
        print("    Skipping new environment creation.")
        return False  # We did not create a new env, we are using the current one

    print("    No active virtual environment detected.")

    # Check if Conda is installed
    if not shutil.which("conda"):
        print_error("No active venv found AND Conda is not installed.")
        print("    Please either:")
        print("    1. Create a venv (PyCharm/uv) and run this script inside it.")
        print("    2. Install Anaconda/Miniconda.")
        sys.exit(1)

    # Proceed with Conda creation
    print_step(f"Creating fresh Conda environment '{ENV_NAME}' with Python {TARGET_PY_VERSION}...")
    try:
        subprocess.check_call([
            "conda", "create", "-n", ENV_NAME,
            f"python={TARGET_PY_VERSION}", "-y"
        ])
    except subprocess.CalledProcessError:
        print_error("Failed to create Conda environment.")
        sys.exit(1)

    return True  # We created a new env


def install_packages_conda_env():
    """Installs packages into the newly created Conda env."""
    print_step(f"Installing packages into Conda env '{ENV_NAME}'...")

    # Note: We install everything via pip inside conda for consistency with the venv method
    # Getting the pip path for the new env is tricky cross-platform, so we use 'conda run'
    pip_cmd = ["conda", "run", "-n", ENV_NAME, "pip", "install"] + PIP_PACKAGES

    try:
        subprocess.check_call(pip_cmd)
    except subprocess.CalledProcessError:
        print_error("Failed to install packages into Conda env.")
        sys.exit(1)


def create_verification_script():
    print_step("Creating verification script (verify_install.py)...")
    code = """
import pennylane as qml
import matplotlib.pyplot as plt
import sys

print(f"\\nPython Version: {sys.version.split()[0]}")
print(f"PennyLane Version: {qml.version()}")
def main():
    # 1. Device Creation Check
    try:
        dev = qml.device("default.qubit", wires=2)
        print("Device created successfully.")
    except Exception as e:
        print(f"Error creating device: {e}")
        sys.exit(1)

    # 2. Circuit Execution Check
    @qml.qnode(dev)
    def circuit(theta):
        qml.RX(theta, wires=0)
        qml.CNOT(wires=[0, 1])
        return qml.expval(qml.PauliZ(0))

    try:
        result = circuit(0.5)
        print(f"Circuit execution result: {result}")
        print("SUCCESS: Environment is ready for the lab.")
    except Exception as e:
        print(f"Error running circuit: {e}")
if __name__ == "__main__":
    main()
"""
    with open("verify_install.py", "w") as f:
        f.write(code)


def main():
    print("=========================================")
    print("   PennyLane Lab Setup (Smart Mode)")
    print("=========================================")

    # 1. If we are already in a venv (PyCharm, uv, active conda), just install there.
    if is_virtual_env():
        print("Status: Running inside an active virtual environment.")
        check_python_version()
        install_packages_current_env()
        create_verification_script()
        print_step("SETUP COMPLETE (In current environment)")
        print("Run: python verify_install.py")

    # 2. If not, fallback to creating a Conda environment (for colleagues without venvs)
    else:
        print("Status: System python detected (unsafe). initializing Conda flow.")
        check_python_version()  # Checks system python, but we will create new one anyway
        created_new = create_conda_env_if_needed()

        if created_new:
            install_packages_conda_env()
            create_verification_script()
            print_step("SETUP COMPLETE (New Conda Env Created)")
            if platform.system() == "Windows":
                print(f"Run: conda activate {ENV_NAME}")
            else:
                print(f"Run: conda activate {ENV_NAME}")
            print(f"Then: python verify_install.py")


if __name__ == "__main__":
    main()
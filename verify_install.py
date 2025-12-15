
import pennylane as qml
import matplotlib.pyplot as plt
import sys

print(f"\nPython Version: {sys.version.split()[0]}")
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

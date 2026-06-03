# Transverse Field Ising Model to Demo Primitives

from qiskit import QuantumCircuit
import numpy as np
from qiskit.circuit.library import YGate

# Manually create the SQRT(Y) and SQRT(Y) dagger gates
SYGate = YGate().power(0.5)
SYGate.name = "SY"

SYdgGate = YGate().power(-0.5)
SYdgGate.name = "SY†"

def generate_1d_tfim_circuit(num_qubits, num_trotter_steps, rx_angle, trotter_barriers = False, layer_barriers = False):
    qc = QuantumCircuit(num_qubits)
    
    for trotter_step in range(num_trotter_steps):
        add_1d_tfim_trotter_layer(qc, rx_angle, layer_barriers)
        if trotter_barriers:
            qc.barrier()

    return qc

def add_1d_tfim_trotter_layer(qc, rx_angle, layer_barriers = False):
    # Adding the Rzz gates between even layers
    for i in range(0, qc.num_qubits - 1, 2):
        qc.sdg([i, i+1])
        qc.append(SYGate, [i+1])
        qc.cx(i, i+1)
        qc.append(SYdgGate, [i+1])
    if layer_barriers:
        qc.barrier()
        
    # Adding the Rzz gates between odd layers
    for i in range(1, qc.num_qubits - 1, 2):  # Note: changed 0 to 1 for odd layers!
        qc.sdg([i, i+1])
        qc.append(SYGate, [i+1])
        qc.cx(i, i+1)
        qc.append(SYdgGate, [i+1])
    if layer_barriers:
        qc.barrier()
        
    qc.rx(rx_angle, list(range(qc.num_qubits)))
    if layer_barriers:
        qc.barrier()

num_qubits = 6
num_trotter_steps = 1
rx_angle = 0.5 * np.pi

qc = generate_1d_tfim_circuit(num_qubits, num_trotter_steps, rx_angle, trotter_barriers = True, layer_barriers = True)

fig = qc.draw(output='mpl')
fig.savefig("my_circuit.png")
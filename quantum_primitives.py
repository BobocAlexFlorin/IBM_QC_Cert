"""
Quantum Primitives Module
=========================

This module provides reusable quantum circuit generation functions extracted from
the IBM Quantum Certification notebooks. It includes primitives for the Transverse
Field Ising Model (TFIM), kernel circuits, and related quantum operations.

Key Components:
    - TFIM circuit generation with Trotter decomposition
    - Quantum kernel feature maps
    - Error mitigation circuit patterns
"""

from typing import Optional, List, Tuple
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter, ParameterVector
from qiskit.circuit.library import YGate


def _create_sqrt_y_gates() -> Tuple:
    """
    Create custom SQRT(Y) and SQRT(Y)† gates for TFIM circuits.
    
    Returns:
        Tuple[Gate, Gate]: A tuple containing (SY_gate, SY_dagger_gate)
        
    Note:
        These are used in the TFIM Trotter layer implementation to build
        the transverse field Ising model interactions.
    """
    sy_gate = YGate().power(0.5)
    sy_gate.name = "SY"
    
    sy_dagger_gate = YGate().power(-0.5)
    sy_dagger_gate.name = "SY†"
    
    return sy_gate, sy_dagger_gate


def add_1d_tfim_trotter_layer(
    qc: QuantumCircuit,
    rx_angle: float,
    layer_barriers: bool = False,
    sy_gate: Optional = None,
    sy_dagger_gate: Optional = None
) -> None:
    """
    Add a single Trotter layer of the 1D TFIM to a quantum circuit.
    
    Implements a Trotter decomposition step for the Transverse Field Ising Model.
    The layer consists of:
    - Even-layer TFIM interactions (between qubits 0-1, 2-3, etc.)
    - Odd-layer TFIM interactions (between qubits 1-2, 3-4, etc.)
    - Global RX rotation with the specified angle
    
    Args:
        qc: The quantum circuit to modify in-place.
        rx_angle: The rotation angle for RX gates (in radians).
        layer_barriers: If True, add barriers between sublayers for visualization.
        sy_gate: Optional pre-computed SQRT(Y) gate. If None, created internally.
        sy_dagger_gate: Optional pre-computed SQRT(Y)† gate. If None, created internally.
        
    Raises:
        ValueError: If rx_angle is not a real number.
        
    Example:
        >>> qc = QuantumCircuit(4)
        >>> add_1d_tfim_trotter_layer(qc, np.pi / 4)
        >>> qc.draw()
    """
    if sy_gate is None or sy_dagger_gate is None:
        sy_gate, sy_dagger_gate = _create_sqrt_y_gates()
    
    # Even-layer interactions (qubits 0-1, 2-3, ...)
    for i in range(0, qc.num_qubits - 1, 2):
        qc.sdg([i, i + 1])
        qc.append(sy_gate, [i + 1])
        qc.cx(i, i + 1)
        qc.append(sy_dagger_gate, [i + 1])
    
    if layer_barriers:
        qc.barrier()
    
    # Odd-layer interactions (qubits 1-2, 3-4, ...)
    for i in range(1, qc.num_qubits - 1, 2):
        qc.sdg([i, i + 1])
        qc.append(sy_gate, [i + 1])
        qc.cx(i, i + 1)
        qc.append(sy_dagger_gate, [i + 1])
    
    if layer_barriers:
        qc.barrier()
    
    # Global transverse field (RX rotation)
    qc.rx(rx_angle, list(range(qc.num_qubits)))
    if layer_barriers:
        qc.barrier()


def generate_1d_tfim_circuit(
    num_qubits: int,
    num_trotter_steps: int,
    rx_angle: float,
    num_cl_bits: int = 0,
    trotter_barriers: bool = False,
    layer_barriers: bool = False
) -> QuantumCircuit:
    """
    Generate a complete 1D TFIM circuit with multiple Trotter steps.
    
    This function creates a quantum circuit implementing the Transverse Field
    Ising Model using Trotter decomposition. The circuit can be used to study
    quantum dynamics, test primitives, or serve as an ansatz for variational algorithms.
    
    Args:
        num_qubits: Number of qubits in the circuit.
        num_trotter_steps: Number of Trotter decomposition steps.
        rx_angle: The rotation angle for RX gates in each step (radians).
        num_cl_bits: Number of classical bits for measurements (default: 0).
        trotter_barriers: If True, add barriers between Trotter steps.
        layer_barriers: If True, add barriers between sublayers within each step.
        
    Returns:
        QuantumCircuit: The constructed TFIM circuit.
        
    Raises:
        ValueError: If num_qubits < 2 or num_trotter_steps < 1.
        
    Example:
        >>> qc = generate_1d_tfim_circuit(num_qubits=6, num_trotter_steps=2, rx_angle=np.pi/4)
        >>> print(f"Circuit depth: {qc.depth()}")
    """
    if num_qubits < 2:
        raise ValueError("num_qubits must be at least 2")
    if num_trotter_steps < 1:
        raise ValueError("num_trotter_steps must be at least 1")
    
    qc = QuantumCircuit(num_qubits, num_cl_bits)
    
    sy_gate, sy_dagger_gate = _create_sqrt_y_gates()
    
    for _ in range(num_trotter_steps):
        add_1d_tfim_trotter_layer(
            qc,
            rx_angle,
            layer_barriers=layer_barriers,
            sy_gate=sy_gate,
            sy_dagger_gate=sy_dagger_gate
        )
        if trotter_barriers:
            qc.barrier()
    
    return qc


def add_mirrored_1d_tfim_trotter_layer(
    qc: QuantumCircuit,
    rx_angle: float,
    layer_barriers: bool = False,
    sy_gate: Optional = None,
    sy_dagger_gate: Optional = None
) -> None:
    """
    Add the inverse/mirrored Trotter layer for uncomputing or error mitigation.
    
    This function adds the reverse operation of a standard TFIM Trotter layer,
    which is useful for:
    - Verifying circuit correctness through uncompute patterns
    - Implementing error mitigation techniques
    - Building symmetric circuits for observable measurement
    
    Args:
        qc: The quantum circuit to modify in-place.
        rx_angle: The rotation angle (negated internally for uncompute).
        layer_barriers: If True, add barriers between sublayers.
        sy_gate: Optional pre-computed SQRT(Y) gate.
        sy_dagger_gate: Optional pre-computed SQRT(Y)† gate.
        
    Example:
        >>> qc = QuantumCircuit(4)
        >>> add_1d_tfim_trotter_layer(qc, np.pi / 4)
        >>> add_mirrored_1d_tfim_trotter_layer(qc, np.pi / 4)
        >>> # Circuit should now approximately return to |0...0>
    """
    if sy_gate is None or sy_dagger_gate is None:
        sy_gate, sy_dagger_gate = _create_sqrt_y_gates()
    
    # Reverse rotation (negative angle)
    qc.rx(-rx_angle, list(range(qc.num_qubits)))
    if layer_barriers:
        qc.barrier()
    
    # Reverse odd-layer interactions (must be done before even-layer)
    for i in range(1, qc.num_qubits - 1, 2):
        qc.append(sy_gate, [i + 1])
        qc.cx(i, i + 1)
        qc.append(sy_dagger_gate, [i + 1])
        qc.s([i, i + 1])
    
    if layer_barriers:
        qc.barrier()
    
    # Reverse even-layer interactions
    for i in range(0, qc.num_qubits - 1, 2):
        qc.append(sy_gate, [i + 1])
        qc.cx(i, i + 1)
        qc.append(sy_dagger_gate, [i + 1])
        qc.s([i, i + 1])
    
    if layer_barriers:
        qc.barrier()


def create_quantum_kernel_feature_map(
    num_qubits: int,
    num_features: int,
    entangler_map: Optional[List[List[int]]] = None,
    training_param: Optional[Parameter] = None
) -> QuantumCircuit:
    """
    Create a parameterized quantum feature map for kernel methods.
    
    This function generates a feature map circuit suitable for quantum kernel
    estimation, combining rotation gates and controlled-Z entanglement.
    
    Args:
        num_qubits: Number of qubits in the feature map.
        num_features: Number of input features (typically 2 * num_qubits).
        entangler_map: List of [control, target] pairs for CZ gates.
                       If None, uses a default connectivity pattern.
        training_param: Optional tunable Parameter. If None, π/2 is used.
        
    Returns:
        QuantumCircuit: Parameterized feature map circuit.
        
    Raises:
        ValueError: If num_features != 2 * num_qubits.
        
    Example:
        >>> fm = create_quantum_kernel_feature_map(num_qubits=7, num_features=14)
        >>> print(f"Number of parameters: {fm.num_parameters}")
    """
    if num_features != 2 * num_qubits:
        raise ValueError(f"num_features must be 2 * num_qubits, got {num_features} and {num_qubits}")
    
    fm = QuantumCircuit(num_qubits)
    
    if training_param is None:
        training_param = Parameter("θ")
    
    feature_params = ParameterVector("x", num_features)
    
    # Initial RY rotation with training parameter
    fm.ry(training_param, fm.qubits)
    
    # Default entangler map if not provided
    if entangler_map is None:
        entangler_map = _generate_default_entangler_map(num_qubits)
    
    # Apply CZ entanglement
    for control, target in entangler_map:
        if 0 <= control < num_qubits and 0 <= target < num_qubits:
            fm.cz(control, target)
    
    # Apply feature encoding RZ and RX rotations
    for i in range(num_qubits):
        fm.rz(-2 * feature_params[2 * i + 1], i)
        fm.rx(-2 * feature_params[2 * i], i)
    
    return fm


def _generate_default_entangler_map(num_qubits: int) -> List[List[int]]:
    """
    Generate a default entangler map based on qubit count.
    
    Args:
        num_qubits: Number of qubits.
        
    Returns:
        List of [control, target] pairs for CZ gates.
    """
    if num_qubits == 7:
        return [[0, 2], [3, 4], [2, 5], [1, 4], [2, 3], [4, 6]]
    else:
        # Generic nearest-neighbor pattern
        return [[i, i + 1] for i in range(num_qubits - 1)]


def append_mirrored_1d_tfim_circuit(
    qc: QuantumCircuit,
    num_qubits: int,
    num_trotter_steps: int,
    rx_angle: float,
    trotter_barriers: bool = False,
    layer_barriers: bool = False
) -> QuantumCircuit:
    """
    Append a mirrored TFIM circuit (for uncompute or error mitigation).
    
    This is a legacy wrapper that appends mirrored layers to an existing circuit.
    
    Args:
        qc: Quantum circuit to append to (modified in-place).
        num_qubits: Number of qubits (for validation).
        num_trotter_steps: Number of mirrored Trotter steps to append.
        rx_angle: The rotation angle.
        trotter_barriers: If True, add barriers between steps.
        layer_barriers: If True, add barriers between sublayers.
        
    Returns:
        QuantumCircuit: The modified circuit (same as qc).
        
    Note:
        This function modifies qc in-place and also returns it for convenience.
    """
    sy_gate, sy_dagger_gate = _create_sqrt_y_gates()
    
    for _ in range(num_trotter_steps):
        add_mirrored_1d_tfim_trotter_layer(
            qc,
            rx_angle,
            layer_barriers=layer_barriers,
            sy_gate=sy_gate,
            sy_dagger_gate=sy_dagger_gate
        )
        if trotter_barriers:
            qc.barrier()
    
    return qc

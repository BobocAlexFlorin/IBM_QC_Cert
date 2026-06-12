"""
Visualization Utilities Module
===============================

This module provides plotting and visualization functions for quantum computing results,
including measurement distributions, expectation values, and comparative analysis plots.

Key Functions:
    - visualize_counts: Plot measurement outcome distributions
    - plot_expectation_values: Compare expectation values across experiments
    - plot_survival_probability: Visualize state survival probabilities
    - plot_mitigation_comparison: Compare error mitigation techniques
"""

from typing import Dict, List, Tuple, Optional, Union
import numpy as np
import matplotlib.pyplot as plt


def visualize_counts(
    counts: Dict[int, int],
    num_qubits: int,
    num_shots: int,
    top_n: int = 10,
    show: bool = True,
    figsize: Tuple[float, float] = (10, 6),
    title: str = "Sampling Results"
) -> plt.Figure:
    """
    Visualize measurement outcome distribution as a bar chart.
    
    Creates a bar plot showing the measurement probabilities for quantum circuit
    outcomes. Displays the top N outcomes plus the |0...0> state probability.
    
    Args:
        counts: Dictionary mapping bitstring integers to occurrence counts.
        num_qubits: Number of qubits (for formatting bitstrings).
        num_shots: Total number of measurement shots.
        top_n: Number of top outcomes to display (default: 10).
        show: If True, call plt.show() before returning.
        figsize: Figure size as (width, height) in inches.
        title: Title for the plot.
        
    Returns:
        plt.Figure: The matplotlib figure object.
        
    Raises:
        ValueError: If num_shots <= 0 or num_qubits < 1.
        
    Example:
        >>> counts = {0: 500, 1: 300, 3: 200}
        >>> fig = visualize_counts(counts, num_qubits=2, num_shots=1000)
    """
    if num_shots <= 0:
        raise ValueError("num_shots must be positive")
    if num_qubits < 1:
        raise ValueError("num_qubits must be at least 1")
    
    # Get probability for |0...0> state
    zero_prob = counts.get(0, 0)
    
    # Get top N outcomes by count
    top_outcomes = dict(
        sorted(counts.items(), key=lambda item: item[1], reverse=True)[:top_n]
    )
    
    # Always include zero state
    top_outcomes.update({0: zero_prob})
    
    # Sort by bitstring value for display
    sorted_outcomes = dict(sorted(top_outcomes.items(), key=lambda item: item[0]))
    
    # Convert to bitstrings and probabilities
    bitstrings = [bin(x)[2:].zfill(num_qubits) for x in sorted_outcomes.keys()]
    probabilities = [count / num_shots for count in sorted_outcomes.values()]
    
    # Create figure and plot
    fig, ax = plt.subplots(figsize=figsize)
    ax.bar(bitstrings, probabilities)
    ax.set_xticks(range(len(bitstrings)))
    ax.set_xticklabels(bitstrings, rotation=75)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel("Measured Bitstring", fontsize=12)
    ax.set_ylabel("Probability", fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    if show:
        plt.show()
    
    return fig


def plot_expectation_values(
    labels: List[str],
    expectation_values: Union[List[float], np.ndarray],
    errors: Optional[Union[List[float], np.ndarray]] = None,
    show: bool = True,
    figsize: Tuple[float, float] = (10, 6),
    title: str = "Expectation Values",
    ylabel: str = "Expectation Value"
) -> plt.Figure:
    """
    Plot expectation values with optional error bars.
    
    Useful for comparing results across different configurations or error mitigation
    techniques.
    
    Args:
        labels: Labels for each data point (typically technique names).
        expectation_values: Computed expectation values.
        errors: Optional standard errors or uncertainties for each value.
        show: If True, call plt.show() before returning.
        figsize: Figure size as (width, height) in inches.
        title: Title for the plot.
        ylabel: Label for the y-axis.
        
    Returns:
        plt.Figure: The matplotlib figure object.
        
    Raises:
        ValueError: If lengths don't match or arrays are empty.
        
    Example:
        >>> labels = ["No mitigation", "+ DD", "+ TREX"]
        >>> values = [0.85, 0.92, 0.95]
        >>> errors = [0.05, 0.03, 0.02]
        >>> fig = plot_expectation_values(labels, values, errors)
    """
    if len(labels) != len(expectation_values):
        raise ValueError("labels and expectation_values must have same length")
    if len(labels) == 0:
        raise ValueError("Must provide at least one data point")
    
    expectation_values = np.asarray(expectation_values)
    
    if errors is not None:
        errors = np.asarray(errors)
        if len(errors) != len(labels):
            raise ValueError("errors must have same length as labels and expectation_values")
    
    fig, ax = plt.subplots(figsize=figsize)
    
    x_pos = np.arange(len(labels))
    ax.bar(x_pos, expectation_values, yerr=errors, capsize=5, alpha=0.7)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    if show:
        plt.show()
    
    return fig


def plot_survival_probability(
    trotter_steps: Union[List[int], np.ndarray],
    survival_probs: Union[List[float], np.ndarray],
    show: bool = True,
    figsize: Tuple[float, float] = (10, 6),
    title: str = "State Survival Probability",
    xlabel: str = "2Q Gate Depth",
    ylabel: str = "Survival Probability of |0...0>"
) -> plt.Figure:
    """
    Plot survival probability as a function of circuit depth or time.
    
    This is commonly used to study state decay or the dynamics of quantum systems,
    particularly in TFIM or similar studies.
    
    Args:
        trotter_steps: X-axis values (typically gate depth or Trotter steps).
        survival_probs: Measured survival probabilities.
        show: If True, call plt.show() before returning.
        figsize: Figure size as (width, height) in inches.
        title: Title for the plot.
        xlabel: Label for the x-axis.
        ylabel: Label for the y-axis.
        
    Returns:
        plt.Figure: The matplotlib figure object.
        
    Example:
        >>> steps = [0, 4, 8, 12, 16]
        >>> probs = [1.0, 0.95, 0.85, 0.72, 0.60]
        >>> fig = plot_survival_probability(steps, probs)
    """
    trotter_steps = np.asarray(trotter_steps)
    survival_probs = np.asarray(survival_probs)
    
    if len(trotter_steps) != len(survival_probs):
        raise ValueError("trotter_steps and survival_probs must have same length")
    if len(trotter_steps) == 0:
        raise ValueError("Must provide at least one data point")
    
    fig, ax = plt.subplots(figsize=figsize)
    
    ax.plot(trotter_steps, survival_probs, 'o--', linewidth=2, markersize=8)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([-0.05, 1.05])
    
    plt.tight_layout()
    
    if show:
        plt.show()
    
    return fig


def plot_mitigation_comparison(
    techniques: List[str],
    noiseless_value: float,
    mitigated_values: Dict[str, float],
    errors: Optional[Dict[str, float]] = None,
    show: bool = True,
    figsize: Tuple[float, float] = (10, 6),
    title: str = "Error Mitigation Comparison"
) -> plt.Figure:
    """
    Compare mitigated expectation values against theoretical ideal value.
    
    Visualizes how different error mitigation techniques improve results
    relative to the unmitigated and ideal values.
    
    Args:
        techniques: Names of mitigation techniques in order.
        noiseless_value: The theoretical ideal (noiseless) expectation value.
        mitigated_values: Dictionary mapping technique names to their results.
        errors: Optional dictionary of errors for each technique.
        show: If True, call plt.show() before returning.
        figsize: Figure size as (width, height) in inches.
        title: Title for the plot.
        
    Returns:
        plt.Figure: The matplotlib figure object.
        
    Example:
        >>> techniques = ["None", "DD", "TREX", "Twirling", "ZNE"]
        >>> mitigated = {"None": 0.82, "DD": 0.88, "TREX": 0.92, "Twirling": 0.94, "ZNE": 0.98}
        >>> fig = plot_mitigation_comparison(techniques, 1.0, mitigated)
    """
    if not all(t in mitigated_values for t in techniques):
        raise ValueError("All techniques must be in mitigated_values dict")
    
    values = [mitigated_values[t] for t in techniques]
    errs = [errors[t] if errors else None for t in techniques] if errors else None
    
    fig, ax = plt.subplots(figsize=figsize)
    
    x_pos = np.arange(len(techniques))
    ax.bar(x_pos, values, yerr=errs, capsize=5, alpha=0.7, label="Mitigated")
    ax.axhline(y=noiseless_value, color="gray", linestyle="--", linewidth=2, label="Ideal")
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(techniques, rotation=45, ha='right')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_ylabel("Expectation Value", fontsize=12)
    ax.legend(loc="lower right")
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    if show:
        plt.show()
    
    return fig


def plot_parameter_sweep(
    parameter_values: Union[List[float], np.ndarray],
    results: Union[List[float], np.ndarray],
    param_name: str = "Parameter",
    show: bool = True,
    figsize: Tuple[float, float] = (10, 6),
    title: Optional[str] = None
) -> plt.Figure:
    """
    Plot results from a parameter sweep (variational algorithm results, etc).
    
    Args:
        parameter_values: The swept parameter values.
        results: Corresponding result values (expectation values, energies, etc).
        param_name: Name of the parameter being swept.
        show: If True, call plt.show() before returning.
        figsize: Figure size as (width, height) in inches.
        title: Optional custom title. If None, auto-generated.
        
    Returns:
        plt.Figure: The matplotlib figure object.
    """
    parameter_values = np.asarray(parameter_values)
    results = np.asarray(results)
    
    if len(parameter_values) != len(results):
        raise ValueError("parameter_values and results must have same length")
    
    fig, ax = plt.subplots(figsize=figsize)
    
    ax.plot(parameter_values, results, 'o--', linewidth=2, markersize=6)
    ax.set_xlabel(param_name, fontsize=12)
    ax.set_ylabel("Result", fontsize=12)
    
    if title is None:
        title = f"{param_name} vs Result"
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if show:
        plt.show()
    
    return fig

"""
Error Mitigation Configuration Module
======================================

This module provides configuration classes and functions for various error mitigation
techniques used in quantum computing. It encapsulates settings for dynamical decoupling,
readout error mitigation, gate twirling, and zero-noise extrapolation.

Key Components:
    - ErrorMitigationConfig: Base configuration class
    - DynamicalDecouplingConfig: DD sequence configuration
    - ReadoutMitigationConfig: Readout error mitigation settings
    - ZeroNoiseExtrapolationConfig: ZNE parameters
    - MitigationLevel: Enum for predefined mitigation levels
"""

from typing import Tuple, List, Literal, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class MitigationLevel(Enum):
    """
    Enumeration of predefined error mitigation levels.
    
    Levels:
        NONE: No error mitigation techniques applied.
        BASIC: Dynamical decoupling only.
        STANDARD: DD + readout error mitigation (TREX).
        ADVANCED: DD + TREX + gate twirling.
        FULL: DD + TREX + gate twirling + zero-noise extrapolation.
    """
    NONE = 0
    BASIC = 1
    STANDARD = 2
    ADVANCED = 3
    FULL = 4


@dataclass
class DynamicalDecouplingConfig:
    """
    Configuration for Dynamical Decoupling error mitigation.
    
    Dynamical decoupling uses carefully timed pulse sequences to reduce decoherence
    errors during idle periods on qubits.
    
    Attributes:
        enable: Whether to enable DD.
        sequence_type: The type of DD sequence ('XX', 'XY4', 'XpXm', etc).
        
    Example:
        >>> dd_config = DynamicalDecouplingConfig(enable=True, sequence_type='XY4')
        >>> print(dd_config)
    """
    enable: bool = False
    sequence_type: Literal['XX', 'XY4', 'XpXm'] = 'XY4'
    
    def __post_init__(self):
        """Validate configuration parameters."""
        valid_sequences = ['XX', 'XY4', 'XpXm']
        if self.sequence_type not in valid_sequences:
            raise ValueError(
                f"sequence_type must be one of {valid_sequences}, "
                f"got {self.sequence_type}"
            )
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return asdict(self)


@dataclass
class ReadoutMitigationConfig:
    """
    Configuration for Readout Error Mitigation.
    
    Also known as TREX (Tensor Response eXpansion), this technique characterizes
    and corrects for measurement errors using calibration data.
    
    Attributes:
        enable: Whether to enable readout error mitigation.
        
    Example:
        >>> ro_config = ReadoutMitigationConfig(enable=True)
    """
    enable: bool = False
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return asdict(self)


@dataclass
class GateTwirlingConfig:
    """
    Configuration for Gate Twirling error mitigation.
    
    Gate twirling adds random single-qubit gates before and after two-qubit gates
    to make errors more uniform and easier to characterize.
    
    Attributes:
        enable_gates: Whether to enable gate-level twirling.
        num_randomizations: Number of random configurations ('auto' or integer).
        
    Example:
        >>> twirl_config = GateTwirlingConfig(enable_gates=True, num_randomizations='auto')
    """
    enable_gates: bool = False
    num_randomizations: str | int = 'auto'
    
    def __post_init__(self):
        """Validate configuration parameters."""
        if isinstance(self.num_randomizations, int) and self.num_randomizations <= 0:
            raise ValueError("num_randomizations must be positive integer or 'auto'")
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return asdict(self)


@dataclass
class ZeroNoiseExtrapolationConfig:
    """
    Configuration for Zero-Noise Extrapolation (ZNE).
    
    ZNE amplifies noise during execution and extrapolates back to the zero-noise limit,
    providing an estimate of the noiseless expectation value.
    
    Attributes:
        enable: Whether to enable ZNE.
        noise_factors: Tuple of noise scaling factors (e.g., (1, 3, 5)).
        extrapolator: Type(s) of extrapolation ('exponential', 'linear', or tuple).
        
    Example:
        >>> zne_config = ZeroNoiseExtrapolationConfig(
        ...     enable=True,
        ...     noise_factors=(1, 3, 5),
        ...     extrapolator='exponential'
        ... )
    """
    enable: bool = False
    noise_factors: Tuple[float, ...] = (1, 3, 5)
    extrapolator: Literal['exponential', 'linear'] | Tuple[str, ...] = 'exponential'
    
    def __post_init__(self):
        """Validate configuration parameters."""
        if len(self.noise_factors) < 2:
            raise ValueError("noise_factors must contain at least 2 values")
        
        if self.noise_factors[0] != 1:
            raise ValueError("First noise factor must be 1 (unscaled)")
        
        if isinstance(self.extrapolator, str):
            valid = ['exponential', 'linear']
            if self.extrapolator not in valid:
                raise ValueError(f"extrapolator must be one of {valid}")
        elif isinstance(self.extrapolator, tuple):
            for ext in self.extrapolator:
                if ext not in ['exponential', 'linear']:
                    raise ValueError("All extrapolators must be 'exponential' or 'linear'")
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return asdict(self)


@dataclass
class ErrorMitigationConfig:
    """
    Comprehensive error mitigation configuration combining all techniques.
    
    This class aggregates all error mitigation settings and provides methods
    to create predefined configurations or convert to various formats.
    
    Attributes:
        resilience_level: Integer level (0-4) controlling automatic mitigation.
        dd_config: Dynamical decoupling configuration.
        readout_config: Readout error mitigation configuration.
        twirling_config: Gate twirling configuration.
        zne_config: Zero-noise extrapolation configuration.
        default_shots: Default number of shots for circuits.
        
    Example:
        >>> config = ErrorMitigationConfig.from_level(MitigationLevel.ADVANCED)
        >>> print(config)
    """
    resilience_level: int = 0
    dd_config: DynamicalDecouplingConfig = None
    readout_config: ReadoutMitigationConfig = None
    twirling_config: GateTwirlingConfig = None
    zne_config: ZeroNoiseExtrapolationConfig = None
    default_shots: int = 100_000
    
    def __post_init__(self):
        """Initialize default configurations if not provided."""
        if self.dd_config is None:
            self.dd_config = DynamicalDecouplingConfig()
        if self.readout_config is None:
            self.readout_config = ReadoutMitigationConfig()
        if self.twirling_config is None:
            self.twirling_config = GateTwirlingConfig()
        if self.zne_config is None:
            self.zne_config = ZeroNoiseExtrapolationConfig()
    
    @classmethod
    def from_level(cls, level: MitigationLevel) -> 'ErrorMitigationConfig':
        """
        Create an ErrorMitigationConfig from a predefined mitigation level.
        
        Args:
            level: A MitigationLevel enum value.
            
        Returns:
            ErrorMitigationConfig: Configured for the specified level.
            
        Example:
            >>> config = ErrorMitigationConfig.from_level(MitigationLevel.FULL)
        """
        if level == MitigationLevel.NONE:
            return cls(resilience_level=0)
        
        elif level == MitigationLevel.BASIC:
            return cls(
                resilience_level=1,
                dd_config=DynamicalDecouplingConfig(enable=True, sequence_type='XY4')
            )
        
        elif level == MitigationLevel.STANDARD:
            return cls(
                resilience_level=2,
                dd_config=DynamicalDecouplingConfig(enable=True, sequence_type='XY4'),
                readout_config=ReadoutMitigationConfig(enable=True)
            )
        
        elif level == MitigationLevel.ADVANCED:
            return cls(
                resilience_level=3,
                dd_config=DynamicalDecouplingConfig(enable=True, sequence_type='XY4'),
                readout_config=ReadoutMitigationConfig(enable=True),
                twirling_config=GateTwirlingConfig(enable_gates=True, num_randomizations='auto')
            )
        
        elif level == MitigationLevel.FULL:
            return cls(
                resilience_level=4,
                dd_config=DynamicalDecouplingConfig(enable=True, sequence_type='XY4'),
                readout_config=ReadoutMitigationConfig(enable=True),
                twirling_config=GateTwirlingConfig(enable_gates=True, num_randomizations='auto'),
                zne_config=ZeroNoiseExtrapolationConfig(
                    enable=True,
                    noise_factors=(1, 3, 5),
                    extrapolator=('exponential', 'linear')
                )
            )
        
        else:
            raise ValueError(f"Unknown mitigation level: {level}")
    
    def to_dict(self) -> dict:
        """
        Convert the entire configuration to a nested dictionary.
        
        Returns:
            dict: Nested dictionary representation of the configuration.
        """
        return {
            'resilience_level': self.resilience_level,
            'dd_config': self.dd_config.to_dict(),
            'readout_config': self.readout_config.to_dict(),
            'twirling_config': self.twirling_config.to_dict(),
            'zne_config': self.zne_config.to_dict(),
            'default_shots': self.default_shots
        }
    
    def __repr__(self) -> str:
        """Return a detailed string representation."""
        lines = [
            f"ErrorMitigationConfig(resilience_level={self.resilience_level})",
            f"  DD: {self.dd_config}",
            f"  Readout: {self.readout_config}",
            f"  Twirling: {self.twirling_config}",
            f"  ZNE: {self.zne_config}",
            f"  Default shots: {self.default_shots}"
        ]
        return '\n'.join(lines)


def get_mitigation_config(level: int | MitigationLevel) -> ErrorMitigationConfig:
    """
    Convenience function to get a mitigation configuration.
    
    Args:
        level: Integer (0-4) or MitigationLevel enum.
        
    Returns:
        ErrorMitigationConfig: The requested configuration.
        
    Raises:
        ValueError: If level is not in valid range or type.
        
    Example:
        >>> config = get_mitigation_config(3)  # ADVANCED level
    """
    if isinstance(level, int):
        if not 0 <= level <= 4:
            raise ValueError("level must be integer between 0 and 4")
        level = MitigationLevel(level)
    elif not isinstance(level, MitigationLevel):
        raise ValueError("level must be int or MitigationLevel")
    
    return ErrorMitigationConfig.from_level(level)


# Predefined configurations for common use cases
BASIC_MITIGATION = ErrorMitigationConfig.from_level(MitigationLevel.BASIC)
STANDARD_MITIGATION = ErrorMitigationConfig.from_level(MitigationLevel.STANDARD)
ADVANCED_MITIGATION = ErrorMitigationConfig.from_level(MitigationLevel.ADVANCED)
FULL_MITIGATION = ErrorMitigationConfig.from_level(MitigationLevel.FULL)

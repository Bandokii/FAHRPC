"""
Hardware Module for FAHRPC
=========================

Handles GPU detection and real-time monitoring for both Nvidia and AMD graphics cards.

Features:
    - Automatic detection of all installed GPUs
    - Real-time temperature monitoring
    - GPU utilization percentage tracking
    - Multi-GPU support (mixed Nvidia/AMD configurations)
    - Graceful fallback when GPU libraries unavailable

Supported Hardware:
    - Nvidia GPUs via pynvml (NVML library)
    - AMD GPUs via pyadl (ADL library)

Example usage:
    >>> from fahrpc.hardware import GPUMonitor
    >>> monitor = GPUMonitor(config)
    >>> print(f"Found {monitor.nvidia_count} Nvidia GPUs")
    >>> for name, util, temp in monitor.get_nvidia_data():
    ...     print(f"{name}: {util}% @ {temp}°C")
"""

import logging
import warnings
from typing import Any, Dict, List, Tuple

from fahrpc.config import APP_NAME

logger = logging.getLogger(APP_NAME.upper())

# ============================================================================
# GPU Library Imports
# ============================================================================
# Nvidia: pynvml wraps NVIDIA Management Library (NVML) for GPU monitoring
# AMD: pyadl wraps AMD Display Library (ADL) for Radeon GPUs
# Both libraries may emit warnings during import, which we suppress

# Import Nvidia NVML library (suppress FutureWarning from numpy/etc)
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    import pynvml

# Import AMD ADL library (optional - graceful fallback if not available)
try:
    from pyadl import ADLManager
    AMD_SUPPORT = True
except (ImportError, Exception) as e:
    # AMD support requires specific drivers and pyadl package
    logger.debug(f"AMD GPU support not available: {e}")
    AMD_SUPPORT = False


# ============================================================================
# GPU Monitor Class
# ============================================================================

class GPUMonitor:
    """
    Manages GPU detection and real-time monitoring.

    Attributes:
        config: Configuration dictionary
        nvidia_handles: List of (handle, name) tuples for Nvidia GPUs
        nvidia_names: List of cleaned Nvidia GPU names
        amd_devices: List of AMD device objects from ADLManager
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize GPU Monitor.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.nvidia_handles = []
        self.nvidia_names = []
        self.amd_devices = []
        self._detect_hardware()

    def _detect_hardware(self) -> None:
        """Detect available GPUs (Nvidia and AMD) with sanity checks and extra logging."""
        # Nvidia detection
        if self.config['hardware']['nvidia']['enabled']:
            try:
                pynvml.nvmlInit()
                device_count = pynvml.nvmlDeviceGetCount()
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    name = pynvml.nvmlDeviceGetName(handle)
                    if isinstance(name, bytes):
                        name = name.decode('utf-8')
                    clean_name = name.replace(
                        self.config['hardware']['nvidia']['strip_prefix'], ""
                    ).strip()
                    self.nvidia_handles.append((handle, clean_name))
                    self.nvidia_names.append(clean_name)
            except Exception as e:
                logger.error(f"Nvidia GPU detection failed: {e}", exc_info=True)

        # AMD detection with sanity check and extra logging
        if self.config['hardware']['amd']['enabled'] and AMD_SUPPORT:
            try:
                instance = ADLManager.getInstance()
                if instance:
                    raw_devices = instance.getDevices()
                    valid_devices = []
                    for dev in raw_devices:
                        # Log all detected device details for debugging
                        logger.debug(
                            f"[AMD DETECT] Device: adapterName={getattr(dev, 'adapterName', None)}, "
                            f"present={getattr(dev, 'present', None)}, "
                            f"busNumber={getattr(dev, 'busNumber', None)}"
                        )
                        # Sanity check: Only keep devices with a valid, non-empty adapterName
                        # and present==True if available
                        name = getattr(dev, 'adapterName', None)
                        present = getattr(dev, 'present', True)  # Some ADL versions have 'present' attribute
                        if name and isinstance(name, str) and name.strip() and present:
                            valid_devices.append(dev)
                        else:
                            logger.warning(
                                f"[AMD DETECT] Ignoring invalid or ghost device: adapterName={name}, present={present}"
                            )
                    self.amd_devices = valid_devices
                    logger.info(
                        f"[AMD DETECT] {len(self.amd_devices)} valid AMD device(s) detected after filtering."
                    )
            except Exception as e:
                logger.error(f"AMD GPU detection failed: {e}", exc_info=True)
                self.amd_devices = []

    def get_nvidia_data(self) -> List[Tuple[str, int, int]]:
        """
        Get current Nvidia GPU data.

        Returns:
            List of tuples: (gpu_name, utilization_percent, temperature_celsius)
        """
        data = []
        for handle, name in self.nvidia_handles:
            try:
                temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                util = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
                data.append((name, util, temp))
            except Exception as e:
                logger.error(f"Failed to get Nvidia GPU data for {name}: {e}", exc_info=True)
        return data

    def get_amd_data(self) -> List[Tuple[str, int, Any]]:
        """
        Get current AMD GPU data.

        Returns:
            List of tuples: (gpu_name, utilization_percent, temperature)
        """
        data = []
        if AMD_SUPPORT:
            for dev in self.amd_devices:
                try:
                    name = dev.adapterName.replace(
                        self.config['hardware']['amd']['strip_prefix'], ""
                    ).strip()
                    util = dev.getCurrentUsage()
                    temp = dev.getCurrentTemperature()
                    if temp is None or temp <= 0:
                        temp = "N/A"
                    data.append((name, util, temp))
                except Exception as e:
                    logger.error(f"Failed to get AMD GPU data: {e}", exc_info=True)
        return data

    def get_all_gpu_data(self) -> Tuple[List, List[int], List[int]]:
        """
        Get data from all GPUs.

        Returns:
            Tuple of (gpu_lines, utilizations, temperatures)
        """
        gpu_lines = []
        utilizations = []
        temperatures = []

        # Nvidia GPUs
        for name, util, temp in self.get_nvidia_data():
            utilizations.append(util)
            temperatures.append(temp)
            gpu_lines.append((name, util, temp))
        # AMD GPUs
        for name, util, temp in self.get_amd_data():
            utilizations.append(util)
            if temp != "N/A":
                temperatures.append(temp)
            gpu_lines.append((name, util, temp))
        return gpu_lines, utilizations, temperatures

    @property
    def nvidia_count(self) -> int:
        """Number of detected Nvidia GPUs."""
        return len(self.nvidia_names)

    @property
    def amd_count(self) -> int:
        """Number of detected AMD GPUs."""
        return len(self.amd_devices)

    @staticmethod
    def shutdown() -> None:
        """Clean up GPU monitoring resources."""
        try:
            pynvml.nvmlShutdown()
        except Exception as e:
            logger.error(f"Error during GPU monitor shutdown: {e}", exc_info=True)

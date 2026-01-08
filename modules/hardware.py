"""
Hardware module for FAHRPC
Handles GPU detection and monitoring (Nvidia/AMD)
"""

import warnings
import logging
from typing import Dict, List, Any, Tuple, Optional

logger = logging.getLogger('FAHRPC')

# Silent Nvidia import
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    import pynvml


# AMD Support
try:
    from pyadl import ADLManager
    AMD_SUPPORT = True
except (ImportError, Exception):
    AMD_SUPPORT = False


class GPUMonitor:
    """Manages GPU detection and monitoring."""
    
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
        # self.intel_devices = []
        self._detect_hardware()
    
    def _detect_hardware(self) -> None:
        """Detect available GPUs (Nvidia and AMD)."""
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
            except Exception:
                pass
        
        # AMD detection
        if self.config['hardware']['amd']['enabled'] and AMD_SUPPORT:
            try:
                instance = ADLManager.getInstance()
                if instance:
                    self.amd_devices = instance.getDevices()
            except Exception:
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
            except:
                pass
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
                except:
                    pass
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
    def nvidia_count(self):
        """Number of detected Nvidia GPUs."""
        return len(self.nvidia_names)
    @property
    def amd_count(self):
        """Number of detected AMD GPUs."""
        return len(self.amd_devices)
    # Intel GPU support reserved for future implementation
    # @property
    # def intel_count(self):
    #     """Number of detected Intel GPUs."""
    #     return len(self.intel_devices)
    
    @staticmethod
    def shutdown() -> None:
        """Clean up GPU monitoring resources."""
        try:
            pynvml.nvmlShutdown()
        except:
            pass

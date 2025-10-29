import psutil
import platform
from datetime import datetime
import wmi

try:
    import cpuinfo
except ImportError:
    cpuinfo = None


class CPUMetrics:
    """
    Raccoglie metriche CPU dettagliate: frequenze, utilizzo core, temperature, memoria, interrupt.
    Compatibile con esportazione verso Excel.
    """

    def __init__(self):
        # Interfaccia WMI per lettura sensori (solo Windows)
        try:
            self.w = wmi.WMI(namespace="root\WMI")
        except Exception:
            self.w = None

    def _get_temperatures(self):
        temps = {}
        if not self.w:
            return temps
        try:
            for sensor in self.w.MSAcpi_ThermalZoneTemperature():
                celsius = sensor.CurrentTemperature / 10.0 - 273.15
                temps[sensor.InstanceName] = round(celsius, 1)
        except Exception:
            pass
        return temps

    def _get_cpu_info(self):
        info = {}
        try:
            if cpuinfo:
                ci = cpuinfo.get_cpu_info()
                info['cpu_arch'] = ci.get('arch_string_raw', 'N/A')
                info['cpu_bits'] = ci.get('bits', 'N/A')
                info['cpu_brand'] = ci.get('brand_raw', platform.processor())
                info['l1_cache_size'] = ci.get('l1_data_cache_size', 'N/A')
                info['l2_cache_size'] = ci.get('l2_cache_size', 'N/A')
                info['l3_cache_size'] = ci.get('l3_cache_size', 'N/A')
            else:
                info['cpu_arch'] = platform.machine()
                info['cpu_bits'] = platform.architecture()[0]
                info['cpu_brand'] = platform.processor()
                info['l1_cache_size'] = 'N/A'
                info['l2_cache_size'] = 'N/A'
                info['l3_cache_size'] = 'N/A'
        except Exception:
            info = {k: 'N/A' for k in ['cpu_arch', 'cpu_bits', 'cpu_brand', 'l1_cache_size', 'l2_cache_size', 'l3_cache_size']}
        return info

    def snapshot(self, previous_snapshot=None):
        """
        Cattura uno snapshot di utilizzo CPU/RAM + info hardware.
        """
        # Frequenze e utilizzo core
        cpu_freq_per_core = psutil.cpu_freq(percpu=True)
        cpu_percent_per_core = psutil.cpu_percent(interval=0.2, percpu=True)

        # Info memoria
        vm = psutil.virtual_memory()

        # Statistiche CPU (interrupt/context switch)
        cpu_stats = psutil.cpu_stats() if hasattr(psutil, 'cpu_stats') else None
        interrupts = cpu_stats.interrupts if cpu_stats else 'N/A'
        soft_interrupts = cpu_stats.soft_interrupts if cpu_stats else 'N/A'
        ctx_switches = cpu_stats.ctx_switches if cpu_stats else 'N/A'

        # Calcolo delta interrupts
        if previous_snapshot and previous_snapshot.get('interrupts') not in (None, 'N/A') and interrupts not in (None, 'N/A'):
            delta_interrupts = interrupts - previous_snapshot['interrupts']
        else:
            delta_interrupts = 'N/A'

        if previous_snapshot and previous_snapshot.get('soft_interrupts') not in (None, 'N/A') and soft_interrupts not in (None, 'N/A'):
            delta_soft_interrupts = soft_interrupts - previous_snapshot['soft_interrupts']
        else:
            delta_soft_interrupts = 'N/A'

        # Temperature
        temps = self._get_temperatures()
        info = self._get_cpu_info()

        # Snapshot finale
        snapshot = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'cpu_name': info.get('cpu_brand'),
            'cpu_arch': info.get('cpu_arch'),
            'cpu_bits': info.get('cpu_bits'),
            'l1_cache_size': info.get('l1_cache_size'),
            'l2_cache_size': info.get('l2_cache_size'),
            'l3_cache_size': info.get('l3_cache_size'),
            'physical_cores': psutil.cpu_count(logical=False),
            'logical_cores': psutil.cpu_count(logical=True),
            'cpu_percent_total': round(psutil.cpu_percent(interval=0.1), 2),
            'cpu_percent_per_core': cpu_percent_per_core,
            'cpu_freq_current_per_core': [round(f.current, 1) if f else None for f in cpu_freq_per_core],
            'cpu_freq_min_per_core': [round(f.min, 1) if f else None for f in cpu_freq_per_core],
            'cpu_freq_max_per_core': [round(f.max, 1) if f else None for f in cpu_freq_per_core],
            'cpu_temperatures': temps,
            'context_switches': ctx_switches,
            'interrupts': interrupts,
            'soft_interrupts': soft_interrupts,
            'delta_interrupts': delta_interrupts,
            'delta_soft_interrupts': delta_soft_interrupts,
            'ram_total_gb': round(vm.total / (1024 ** 3), 2),
            'ram_used_gb': round(vm.used / (1024 ** 3), 2),
            'ram_available_gb': round(vm.available / (1024 ** 3), 2),
            'ram_percent': vm.percent
        }

        return snapshot

"""
CPUMetrics
--------------
Raccoglie metriche CPU dettagliate, frequenze, temperature, utilizzo core, consumi stimati, memoria e interrupt.
"""
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
    Classe per raccogliere metriche della CPU su Windows.
    """

    def __init__(self):
        # Inizializza l'interfaccia WMI per leggere sensori temperatura
        self.w = wmi.WMI(namespace="root\WMI")

    def _get_temperatures(self):
        """
        Ritorna un dizionario con le temperature della CPU per sensore.
        Le temperature vengono lette da WMI in decimi di Kelvin e convertite in Celsius.
        Se non disponibili, ritorna un dizionario vuoto.
        """
        temps = {}
        try:
            for sensor in self.w.MSAcpi_ThermalZoneTemperature():
                # Conversione da decimi di Kelvin a Celsius
                celsius = sensor.CurrentTemperature / 10.0 - 273.15
                temps[sensor.InstanceName] = round(celsius, 1)
        # Se il sensore non è disponibile, restituisce vuoto
        except Exception:
            pass  
        return temps

    def _get_cpu_info(self):
        """
        Ritorna un dizionario con informazioni sulla CPU:
        - Architettura, bit, nome CPU
        - Cache L1/L2/L3
        Usa py-cpuinfo se disponibile, altrimenti valori di fallback
        """
        info = {}
        if cpuinfo is not None:
            try:
                ci = cpuinfo.get_cpu_info()
                info['cpu_arch'] = ci.get('arch', 'N/A')
                info['cpu_bits'] = ci.get('bits', 'N/A')
                info['cpu_brand'] = ci.get('brand_raw', platform.processor())
                info['l1_cache_size'] = ci.get('l1_data_cache_size', 'N/A')
                info['l2_cache_size'] = ci.get('l2_cache_size', 'N/A')
                info['l3_cache_size'] = ci.get('l3_cache_size', 'N/A')
            except Exception:
                info['cpu_arch'] = 'N/A'
                info['cpu_bits'] = 'N/A'
                info['cpu_brand'] = platform.processor()
                info['l1_cache_size'] = 'N/A'
                info['l2_cache_size'] = 'N/A'
                info['l3_cache_size'] = 'N/A'
        else:
            info['cpu_arch'] = platform.architecture()[0]
            info['cpu_bits'] = 'N/A'
            info['cpu_brand'] = platform.processor()
            info['l1_cache_size'] = 'N/A'
            info['l2_cache_size'] = 'N/A'
            info['l3_cache_size'] = 'N/A'
        return info

    def snapshot(self, previous_snapshot = None):
        """
        Cattura uno snapshot completo della CPU e RAM.
        Se passato previous_snapshot, calcola delta per interrupts e soft_interrupts.
        Ritorna un dizionario con tutti i dati.
        """
    
        # Memoria e statistiche CPU
        vm = psutil.virtual_memory()
        cpu_freq_per_core = psutil.cpu_freq(percpu = True)
        cpu_percent_per_core = psutil.cpu_percent(interval = 0.1, percpu = True)
        cpu_stats = psutil.cpu_stats() if hasattr(psutil, 'cpu_stats') else None

        # Temperature via WMI
        temps = self._get_temperatures()
        info = self._get_cpu_info()

        # Calcola delta interrupts se disponibile previous_snapshot
        interrupts = getattr(cpu_stats, 'interrupts', 'N/A') if cpu_stats else 'N/A'
        soft_interrupts = getattr(cpu_stats, 'soft_interrupts', 'N/A') if cpu_stats else 'N/A'
        ctx_switches = getattr(cpu_stats, 'ctx_switches', 'N/A') if cpu_stats else 'N/A'

        # Delta calcolato rispetto snapshot precedente
        if previous_snapshot:
            if interrupts != 'N/A' and previous_snapshot.get('interrupts') != 'N/A':
                delta_interrupts = interrupts - previous_snapshot['interrupts']
            else:
                delta_interrupts = 'N/A'

            if soft_interrupts != 'N/A' and previous_snapshot.get('soft_interrupts') != 'N/A':
                delta_soft_interrupts = soft_interrupts - previous_snapshot['soft_interrupts']
            else:
                delta_soft_interrupts = 'N/A'
        else:
            delta_interrupts = 'N/A'
            delta_soft_interrupts = 'N/A'

        snapshot = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'cpu_name': info.get('cpu_brand', 'N/A'),
            'cpu_arch': info.get('cpu_arch', 'N/A'),
            'cpu_bits': info.get('cpu_bits', 'N/A'),
            'l1_cache_size': info.get('l1_cache_size', 'N/A'),
            'l2_cache_size': info.get('l2_cache_size', 'N/A'),
            'l3_cache_size': info.get('l3_cache_size', 'N/A'),
            'physical_cores': psutil.cpu_count(logical=False),
            'logical_cores': psutil.cpu_count(logical=True),
            'cpu_percent_total': psutil.cpu_percent(interval=None),
            'cpu_percent_per_core': cpu_percent_per_core,
            'cpu_freq_per_core': [round(f.current,2) if f else 'N/A' for f in cpu_freq_per_core],
            'cpu_freq_min_per_core': [round(f.min,2) if f else 'N/A' for f in cpu_freq_per_core],
            'cpu_freq_max_per_core': [round(f.max,2) if f else 'N/A' for f in cpu_freq_per_core],
            'cpu_temperatures': temps,
            'context_switches': ctx_switches,
            'interrupts': interrupts,
            'soft_interrupts': soft_interrupts,
            'delta_interrupts': delta_interrupts,  
            'delta_soft_interrupts': delta_soft_interrupts,  
            'ram_total_gb': round(vm.total / (1024**3),2),
            'ram_used_gb': round((vm.total - vm.available) / (1024**3),2),
            'ram_free_gb': round(vm.available / (1024**3),2),
        }

        return snapshot

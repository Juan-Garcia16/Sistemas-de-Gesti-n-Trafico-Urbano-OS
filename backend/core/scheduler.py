import queue
import threading
import time

class TrafficScheduler:
    """
    Implementa Priority Scheduling para las intersecciones (recursos).
    
    --- Concepto de SO: CPU/Resource Scheduler ---
    Análogamente a cómo un Planificador (Scheduler) del Sistema Operativo decide 
    qué proceso alojar en la CPU basado en políticas de planificación, este orquestador 
    gestiona qué vehículo (proceso) obtiene acceso al semáforo (recurso crítico).
    Utiliza el algoritmo de "Priority Scheduling", garantizando que procesos de 
    máxima prioridad (ej. vehículos de EMERGENCIA con prioridad 0) se despachen primero.
    """
    def __init__(self):
        # _queues actúa como las "Ready Queues" (Colas de listos) multiplicadas por recurso
        # PriorityQueue ordena automáticamente mediante una jerarquía (heap) interna.
        self._queues: dict[str, queue.PriorityQueue] = {}
        
        # Otorga una bandera específica por proceso para simular el cambio de contexto a RUNNING
        self._dispatch_events: dict[str, threading.Event] = {}
        
        # Monitor para proteger la creación y acceso seguro a las estructuras del Planificador
        self._lock = threading.Lock()

    def enqueue(self, vehicle, intersection_id: str):
        """
        Encola un proceso en la cola de listos (Ready Queue) perteneciente a un recurso.
        """
        with self._lock:
            if intersection_id not in self._queues:
                self._queues[intersection_id] = queue.PriorityQueue()
            if vehicle.vehicle_id not in self._dispatch_events:
                self._dispatch_events[vehicle.vehicle_id] = threading.Event()

        # En sistemas operativos, si dos procesos tienen igual prioridad, se recurre 
        # a FIFO / Round Robin temporal. Aquí incluimos time.time() para evitar choques
        # en la PriorityQueue si hay prioridades empatadas, respetando el orden de llegada.
        entry = (vehicle.priority, time.time(), vehicle)
        self._queues[intersection_id].put(entry)

    def dispatch_next(self, intersection_id: str):
        """
        Actúa como el Despachador (Dispatcher) en el SO, otorgando el recurso 
        al proceso de máxima jerarquía en la estructura 'heap' de la cola.
        """
        if intersection_id in self._queues:
            try:
                # get_nowait extrae al proceso siempre priorizando el de menor valor IntEnum.
                _, _, vehicle = self._queues[intersection_id].get_nowait()
                # Envía la señal (interrupción de software) para despertar al Vehículo
                self._dispatch_events[vehicle.vehicle_id].set()
            except queue.Empty:
                pass

    def wait_for_dispatch(self, vehicle_id: str):
        """
        Envía coercitivamente al hilo al estado WAITING/BLOCKED.
        Retiene la ejecución (sin consumir ciclos activos de CPU) hasta que el OS le notifica.
        """
        event = self._dispatch_events.get(vehicle_id)
        if event:
            event.wait()
            event.clear()

import threading
from enum import IntEnum

# --- Concepto de SO: Prioridad de Procesos (Priority Scheduling) ---
# En los sistemas operativos, el planificador (scheduler) usa niveles de prioridad 
# para decidir qué proceso obtiene la CPU. Los valores más bajos numéricamente 
# suelen inferir la prioridad más alta (como en Unix/Linux).
class Priority(IntEnum):
    EMERGENCY = 0   # Nivel 0 (Alta Prioridad): Ambulancias, bomberos, interrumpe el flujo normal.
    HIGH      = 1   # Nivel 1: Transporte público o vehículos especiales.
    NORMAL    = 2   # Nivel 2: Tráfico particular regular.

class Vehicle(threading.Thread):
    """
    Cadada Vehículo representa un Proceso o Tarea independiente en nuestro SO simulado.
    
    --- Mapeo de SO: Procesos concurrentes vs Hilos ---
    Al heredar de `threading.Thread`, estamos creando una unidad de ejecución concurrente.
    En el contexto de esta simulación académica, cada hilo se comporta como un "proceso"
    que busca recursos (las intersecciones/semáforos) y es gestionado por un Scheduler.
    Se define como un hilo 'daemon' para simular procesos en segundo plano que mueren
    automáticamente si el sistema principal (el motor de simulación) se apaga, evitando hilos zombis.
    """
    def __init__(self, vehicle_id: str, route: list, priority: Priority, scheduler):
        # daemon=True imita un proceso dependiente del padre que no impide la finalización del programa
        super().__init__(daemon=True)
        self.vehicle_id = vehicle_id
        self.route = route           # Lista de intersection_ids a cruzar
        self.priority = priority
        self.scheduler = scheduler
        self.current_position = 0
        
        # --- Concepto de SO: PCB (Process Control Block) ---
        # Estos atributos forman parte del estado del proceso, de forma análoga
        # a un Bloque de Control de Procesos (PCB) que el SO almacena en memoria:
        # PENDIENTE (WAITING), EJECUTANDO (MOVING), ZOMBI/FINALIZADO (DONE).
        self.status = "WAITING"

    def run(self):
        """
        Ciclo de vida del proceso en el SO y su ejecución principal.
        Representa las instrucciones de la Tarea/Proceso.
        """
        for intersection_id in self.route:
            # 1. Estado: WAIT - El proceso cede el control voluntariamente o espera por un recurso.
            self.status = "WAITING"
            
            # El proceso entra a la cola de listos (Ready Queue) manejada por el Planificador
            self.scheduler.enqueue(self, intersection_id)
            
            # Bloqueo del proceso (Descheduling) - Espera hasta obtener su turno (CPU / Recurso)
            self.scheduler.wait_for_dispatch(self.vehicle_id)
            
            # 2. Estado: RUNNING (MOVING) - El planificador nos dio el recurso/procesador.
            self.status = "MOVING"
            self.current_position += 1
            
        # 3. Estado: TERMINATED (DONE) - Fin del ciclo del proceso.
        self.status = "DONE"

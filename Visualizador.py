import tkinter as tk  
from tkinter import ttk  
import threading 
import time  
import random  
import sys 

# DEFINICION DE ESTADOS
ESTADOS_COLORES = {
    "Nuevo": "#FFB6C1",         
    "Listo": "#4B0082",         
    "En ejecución": "#FF00CC",  
    "Bloqueado": "purple",     
    "Finalizado": "#8A2BE2"    
}

# CLASE PROCESO
class Proceso(threading.Thread):
    def __init__(self, id, actualizar_ui, notificar_finalizacion):
        super().__init__()
        self.id = id
        self.estado = "Nuevo"
        self.actualizar_ui = actualizar_ui
        self.notificar_finalizacion = notificar_finalizacion
        self.detener = False  # Bandera para detener el proceso
        self.bloqueado_manual = False  # Bandera para bloquear manualmente
        self.actualizar_ui(self.id, self.estado)

    # Simula la ejecucion de un proceso pasando por distintos estados
    def run(self): 
        time.sleep(random.uniform(2, 4))  
        self.cambiar_estado("Listo")  

        while self.estado != "Finalizado":
            if self.detener:  
                self.cambiar_estado("Finalizado")
                self.notificar_finalizacion()
                return  

            self.cambiar_estado("En ejecución")  
            for _ in range(int(random.uniform(3, 6))):  
                if self.detener:  
                    self.cambiar_estado("Finalizado")
                    self.notificar_finalizacion()
                    return  
                if self.bloqueado_manual:  
                    self.cambiar_estado("Bloqueado")  
                    time.sleep(3)  # Simula el tiempo en "Bloqueado"
                    self.bloqueado_manual = False  
                    self.cambiar_estado("Listo")  
                    break  
                time.sleep(1)  

            if self.estado == "En ejecución" and random.random() > 0.6:
                self.cambiar_estado("Bloqueado")
                time.sleep(random.uniform(3, 5))
                self.cambiar_estado("Listo")
            elif self.estado == "En ejecución":
                self.cambiar_estado("Finalizado")
                self.notificar_finalizacion()

    def cambiar_estado(self, nuevo_estado):
        self.estado = nuevo_estado
        self.actualizar_ui(self.id, nuevo_estado)

    def detener_proceso(self):
        self.detener = True  

    def bloquear_proceso(self):
        self.bloqueado_manual = True  

# INTERFAZ GRAFICA 
class Visualizador:
    def __init__(self, root, num_procesos=5):
        self.root = root  
        self.num_procesos = num_procesos  
        self.procesos_terminados = 0  
        self.procesos = {}  

        # Etiqueta principal de informacion
        self.label_info = tk.Label(root, text="Esperando el inicio del proceso", font=("Arial", 10, "bold"))
        self.label_info.pack(pady=10)

        # Diccionarios para guardar los widgets asociados a cada proceso
        self.labels = {}  
        self.barras = {}  
        self.botones_detener = {}  
        self.botones_bloquear = {}  

        # Creacion de los elementos graficos para cada proceso
        for i in range(num_procesos):
            frame = tk.Frame(root)  # Contenedor para los elementos de cada proceso
            frame.pack(pady=5)  # Espaciado entre procesos
            
            # Etiqueta que muestra el estado del proceso
            label = tk.Label(frame, text=f"Proceso {i+1}: Nuevo", font=("Arial", 12), width=30, bg="gray")
            label.pack(side="left")

            # Barra de progreso para representar visualmente los cambios de estado
            barra = ttk.Progressbar(frame, length=150, mode="determinate")
            barra.pack(side="left", padx=10)

            # Boton para detener el proceso manualmente
            btn_detener = tk.Button(frame, text="DETENER", command=lambda i=i: self.detener_proceso(i))
            btn_detener.pack(side="left", padx=5)

            # Boton para bloquear el proceso manualmente
            btn_bloquear = tk.Button(frame, text="BLOQUEAR", command=lambda i=i: self.bloquear_proceso(i))
            btn_bloquear.pack(side="left", padx=5)

            # Guardar referencias a los elementos graficos
            self.labels[i] = label  
            self.barras[i] = barra  
            self.botones_detener[i] = btn_detener  
            self.botones_bloquear[i] = btn_bloquear  

        # Boton para iniciar todos los procesos
        self.boton_inicio = tk.Button(root, text="INICIAR", command=self.iniciar_procesos, font=("Arial", 10))
        self.boton_inicio.pack(pady=10)

        # Boton para finalizar la simulacion 
        self.boton_finalizar = tk.Button(root, text="FINALIZAR", command=self.finalizar, font=("Arial", 10))
        self.boton_finalizar.pack(pady=10)
        self.boton_finalizar.pack_forget()  # Se oculta hasta que todos los procesos finalicen

    def actualizar_ui(self, proceso_id, estado):
        def actualizar():
            self.labels[proceso_id].config(text=f"Proceso {proceso_id+1}: {estado}", bg=ESTADOS_COLORES[estado])

            # Modificar la barra de progreso segun el estado
            valores_progreso = {"Nuevo": 0, "Listo": 25, "En ejecución": 50, "Bloqueado": 75, "Finalizado": 100}
            self.barras[proceso_id]["value"] = valores_progreso[estado]
        
        self.root.after(0, actualizar)  # Se actualiza en el hilo principal de Tkinter

    def notificar_finalizacion(self):
        self.procesos_terminados += 1
        if self.procesos_terminados == self.num_procesos:
            self.mostrar_boton_finalizar()

    def mostrar_boton_finalizar(self): #Muestra el boton finalizar cuando termina 
        def actualizar():
            self.label_info.config(text="Todos los procesos han finalizado", fg="gray")
            self.boton_finalizar.pack(pady=10)
        self.root.after(0, actualizar)

    def iniciar_procesos(self):
        print("\nPROCESO INICIADO :)")
        self.label_info.config(text="Todos los procesos han iniciado", fg="gray")
        self.procesos_terminados = 0  # Reiniciar contador de procesos finalizados

        # Creacion y ejecucion de los procesos
        for i in range(self.num_procesos):
            proceso = Proceso(i, self.actualizar_ui, self.notificar_finalizacion)
            self.procesos[i] = proceso  # Guardar la referencia del proceso
            proceso.start()
            time.sleep(0.5)  # Pequeño retraso entre inicios para mejor visualizacion

    def detener_proceso(self, proceso_id):
        if proceso_id in self.procesos:
            self.procesos[proceso_id].detener_proceso()  # Llama al metodo de la clase Proceso

    def bloquear_proceso(self, proceso_id):
        if proceso_id in self.procesos:
            self.procesos[proceso_id].bloquear_proceso()  # Llama al metodo de la clase Proceso

    def finalizar(self):
        print("\nPROCESO FINALIZADO :)")
        self.root.destroy()  # Cierra la ventana de Tkinter

# Se crea la interfaz grafica
root = tk.Tk()
app = Visualizador(root, num_procesos=5)
root.mainloop()

import tkinter as tk
from tkinter import messagebox
import random
import time
import os
#import json
import math
import numpy as np

# -----------------------
#  VARIABLES GLOBALES
# -----------------------
JUGADOR_NOMBRE = ""

# -----------------------
#   ARCHIVO DE PUNTAJES
# -----------------------

#puntajes en memoria
ESCAPA_TOP5 = []   # lista de tuplas (nombre, puntaje)
CAZADOR_TOP5 = []  # lista de tuplas (nombre, puntaje)
JUGADORES = []     # lista de nombres
HISTORIAL = []     # lista de tuplas (nombre, modo, puntaje, ts)
def init_puntajes_globals():
    global ESCAPA_TOP5, CAZADOR_TOP5, JUGADORES, HISTORIAL
    # ya inicializadas arriba; función para reiniciar si hace falta
    ESCAPA_TOP5 = ESCAPA_TOP5 or []
    CAZADOR_TOP5 = CAZADOR_TOP5 or []
    JUGADORES = JUGADORES or []
    HISTORIAL = HISTORIAL or []


def actualizar_top5(modo, nombre, puntuacion):
    """Actualiza ek top5 (modo: 'escapa' o 'cazador')."""
    global ESCAPA_TOP5, CAZADOR_TOP5
    if modo == "escapa":
        ESCAPA_TOP5.append((nombre, puntuacion))
        ESCAPA_TOP5 = sorted(ESCAPA_TOP5, key=lambda x: x[1], reverse=True)[:5]
    elif modo == "cazador":
        CAZADOR_TOP5.append((nombre, puntuacion))
        CAZADOR_TOP5 = sorted(CAZADOR_TOP5, key=lambda x: x[1], reverse=True)[:5]


def registrar_jugador(nombre):
    """Registra el nombre en la lista de jugadores."""
    global JUGADORES
    if not nombre:
        return
    if nombre not in JUGADORES:
        JUGADORES.append(nombre)


def registrar_puntaje_por_jugador(nombre, modo, puntuacion):
    """Añade entrada al historial por jugador """
    global HISTORIAL
    if not nombre:
        return
    HISTORIAL.append((nombre, modo, puntuacion, time.time()))
    registrar_jugador(nombre)
        
# ----------------------------------------------------
#   CLASES DE CELDAS (CAMINO, LIANA, MURO, TUNEL)
# ----------------------------------------------------
# ----------------------------------------------------
#     MENÚ INICIAL (ACTUALIZADO CON REGISTRO + TOP5)
# ----------------------------------------------------
class MenuInicial:
    def __init__(self, master):
        self.master = master
        self.master.title("Juego – Menu Inicial")
        self.pedir_nombre()   # Se pide antes de todo

    # -----------------------
    #   REGISTRO OBLIGATORIO
    # -----------------------
    def pedir_nombre(self):
        self.ventana_nombre = tk.Toplevel(self.master)
        self.ventana_nombre.title("Registro")
        # mantener estilo retro (no cambiar colores globales)
        self.ventana_nombre.transient(self.master)
        self.ventana_nombre.grab_set()

        tk.Label(self.ventana_nombre, text="Ingrese su nombre:").pack(pady=10)
        self.entry_nombre = tk.Entry(self.ventana_nombre)
        self.entry_nombre.pack()
        if JUGADOR_NOMBRE:
            self.entry_nombre.insert(0, JUGADOR_NOMBRE)

        tk.Button(self.ventana_nombre, text="Continuar",
                command=self.guardar_nombre).pack(pady=10)

    def guardar_nombre(self):
        global JUGADOR_NOMBRE
        nombre = self.entry_nombre.get().strip()
        if nombre == "":
            messagebox.showerror("Error", "Debe ingresar un nombre.")
            return
        JUGADOR_NOMBRE = nombre
        registrar_jugador(nombre)
        self.ventana_nombre.grab_release()
        self.ventana_nombre.destroy()
        self.mostrar_menu()

    # -----------------------
    #      MENÚ PRINCIPAL
    # -----------------------
    def mostrar_menu(self):
        self.frame = tk.Frame(self.master)
        self.frame.pack(pady=20)

        tk.Label(self.frame, text=f"Bienvenido, {JUGADOR_NOMBRE}",
                font=("Arial", 14)).pack(pady=10)

        tk.Button(self.frame, text="Modo Escapa",
                    command=lambda: self.iniciar_juego(1)).pack(pady=5)

        tk.Button(self.frame, text="Modo Cazador",
                    command=lambda: self.iniciar_juego(2)).pack(pady=5)

        tk.Button(self.frame, text="Ver Top 5",
                command=self.mostrar_top5).pack(pady=5)

        tk.Button(self.frame, text="Registro de jugadores",
                command=self.mostrar_registro_jugadores).pack(pady=5)

    # -----------------------
    #   VENTANA     DEL TOP 5
    # -----------------------
    def mostrar_top5(self):
        v = tk.Toplevel(self.master)
        v.title("Top 5 Puntajes")
        v.transient(self.master)

        tk.Label(v, text="Top 5 – Modo Escapa",
                font=("Arial", 14, "bold")).pack()

        if not ESCAPA_TOP5:
            tk.Label(v, text="(Sin puntajes)").pack()
        else:
            for nombre, puntaje in ESCAPA_TOP5:
                tk.Label(v, text=f"{nombre} – {puntaje}").pack()

        tk.Label(v, text=" ", font=("Arial")).pack()

        tk.Label(v, text="Top 5 – Modo Cazador",
                font=("Arial", 14, "bold")).pack()

        if not CAZADOR_TOP5:
            tk.Label(v, text="(Sin puntajes)").pack()
        else:
            for nombre, puntaje in CAZADOR_TOP5:
                tk.Label(v, text=f"{nombre} – {puntaje}").pack()

    # -----------------------
    #   VENTANA REGISTRO DE JUGADORES 
    # -----------------------
    def mostrar_registro_jugadores(self):
        v = tk.Toplevel(self.master)
        v.title("Registro de jugadores")
        v.transient(self.master)

        tk.Label(v, text="Jugadores registrados:", font=("Arial", 12, "bold")).pack(pady=(8, 0))
        listbox = tk.Listbox(v, width=40, height=8)
        listbox.pack(padx=8, pady=6)
        for name in JUGADORES:
            listbox.insert(tk.END, name)

        frm = tk.Frame(v)
        frm.pack(pady=6)
        tk.Label(frm, text="Nuevo nombre:").grid(row=0, column=0, padx=4, pady=4)
        entry_new = tk.Entry(frm)
        entry_new.grid(row=0, column=1, padx=4, pady=4)

        def agregar():
            nm = entry_new.get().strip()
            if not nm:
                return
            registrar_jugador(nm)
            listbox.insert(tk.END, nm)
            entry_new.delete(0, tk.END)

        def eliminar_seleccion():
            sel = listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            nombre = listbox.get(idx)
            if nombre in JUGADORES:
                try:
                    # eliminar de JUGADORES
                    JUGADORES.remove(nombre)
                    # eliminar entradas de HISTORIAL
                    global HISTORIAL
                    HISTORIAL = [h for h in HISTORIAL if h[0] != nombre]
                    # eliminar de top5 si aparece
                    global ESCAPA_TOP5, CAZADOR_TOP5
                    ESCAPA_TOP5 = [t for t in ESCAPA_TOP5 if t[0] != nombre]
                    CAZADOR_TOP5 = [t for t in CAZADOR_TOP5 if t[0] != nombre]
                except Exception:
                    pass
            listbox.delete(idx)

        tk.Button(frm, text="Agregar", command=agregar).grid(row=1, column=0, pady=6)
        tk.Button(frm, text="Eliminar seleccionado", command=eliminar_seleccion).grid(row=1, column=1, pady=6)

    # -------------------------------------
    #   INICIAR JUEGO 
    # -------------------------------------
    def inicia_juego(self,modo):
        self.frame.destroy()
        Juego(self.master, modo)
# ----------------------------------------------------
#   TIPOS DE CASILLA (LÓGICA)
# ----------------------------------------------------
class Casilla:
    def es_transitable_jugador(self): return False
    def es_transitable_cazador(self): return False

class Camino(Casilla):
    def es_transitable_jugador(self): return True
    def es_transitable_cazador(self): return True

class Liana(Casilla):
    def es_transitable_jugador(self): return False
    def es_transitable_cazador(self): return True

class Tunel(Casilla):
    def es_transitable_jugador(self): return True
    def es_transitable_cazador(self): return False

class Muro(Casilla):
    def es_transitable_jugador(self): return False
    def es_transitable_cazador(self): return False

class Salida(Casilla):
    def es_transitable_jugador(self): return True
    def es_transitable_cazador(self): return False

TIPOS_CASILLA = {
    0: Camino,
    1: Liana,
    2: Tunel,
    3: Muro,
    4: Salida
}

# ----------------------------------------------------
#   GENERADOR DE MAPA
# ----------------------------------------------------
class GeneradorMapa:
    def __init__(self, filas, columnas, semilla=None):
        self.filas = filas
        self.columnas = columnas
        if semilla is not None:
            random.seed(semilla)
            np.random.seed(semilla)
        self.matriz = None

    def generar_hasta_valido(self, intentos_maximos=30):
        inicio = None
        salida = None
        for _ in range(intentos_maximos):
            self._generar_base()
            inicio = self._seleccionar_inicio()
            salida = self._encontrar_salida()
            if inicio is None or salida is None:
                continue
            if inicio == salida:
                inicio = self._seleccionar_inicio(otra_que=salida)
                if inicio is None:
                    continue
            if self._validar_alcance_bfs(inicio, salida):
                return self.matriz, inicio, salida
        return self.matriz, inicio, salida

    def _generar_base(self):
        pesos = [0.4, 0.18, 0.18, 0.24]  # camino, liana, tunel, muro
        opc = np.random.choice([0,1,2,3], size=(self.filas, self.columnas), p=np.array(pesos))
        mat = np.array(opc, dtype=int)
        sf = random.randint(0, self.filas-1)
        sc = random.randint(0, self.columnas-1)
        mat[sf, sc] = 4
        if mat[0,0] in (1,3):
            mat[0,0] = 0
        fila, col = 0, 0
        while fila != sf:
            fila += 1 if sf > fila else -1
            if mat[fila, col] in (1,3):
                mat[fila, col] = 0
        while col != sc:
            col += 1 if sc > col else -1
            if mat[fila, col] in (1,3):
                mat[fila, col] = 0
        self.matriz = mat

    def _seleccionar_inicio(self, otra_que=None):
        validos = np.where(np.isin(self.matriz, [0,2]))
        coords = list(zip(validos[0].tolist(), validos[1].tolist()))
        if otra_que is not None:
            coords = [c for c in coords if c != otra_que]
        return random.choice(coords) if coords else None

    def _encontrar_salida(self):
        pos = np.where(self.matriz == 4)
        if len(pos[0]) == 0:
            return None
        return (int(pos[0][0]), int(pos[1][0]))

    def _validar_alcance_bfs(self, inicio, salida):
        filas, cols = self.filas, self.columnas
        visitado = np.zeros((filas, cols), dtype=bool)
        fila0, col0 = inicio
        visitado[fila0, col0] = True
        cola = [inicio]
        head = 0
        while head < len(cola):
            f, c = cola[head]; head += 1
            if (f, c) == salida:
                return True
            # arriba
            if f-1 >= 0:
                nf, nc = f-1, c
                if not visitado[nf, nc]:
                    tipo = int(self.matriz[nf, nc])
                    if TIPOS_CASILLA[tipo]().es_transitable_jugador():
                        visitado[nf, nc] = True
                        cola.append((nf, nc))
            # abajo
            if f+1 < filas:
                nf, nc = f+1, c
                if not visitado[nf, nc]:
                    tipo = int(self.matriz[nf, nc])
                    if TIPOS_CASILLA[tipo]().es_transitable_jugador():
                        visitado[nf, nc] = True
                        cola.append((nf, nc))
            # izquierda (wrap)
            nf, nc = f, (c-1) % cols
            if not visitado[nf, nc]:
                tipo = int(self.matriz[nf, nc])
                if TIPOS_CASILLA[tipo]().es_transitable_jugador():
                    visitado[nf, nc] = True
                    cola.append((nf, nc))
            # derecha (wrap)
            nf, nc = f, (c+1) % cols
            if not visitado[nf, nc]:
                tipo = int(self.matriz[nf, nc])
                if TIPOS_CASILLA[tipo]().es_transitable_jugador():
                    visitado[nf, nc] = True
                    cola.append((nf, nc))
        return False

# ----------------------------------------------------
#   Enemigo (cazador)
# ----------------------------------------------------
class Enemigo:
    def __init__(self, id_enemigo, posicion, matriz_ref):
        self.id = id_enemigo
        self.posicion = posicion
        self.matriz_ref = matriz_ref
        self.vivo = True

    def mover_greedy(self, objetivo, perseguir=True):
        filas, cols = self.matriz_ref.shape
        f0, c0 = self.posicion
        objetivo_f, objetivo_c = objetivo
        candidatos = []
        if f0-1 >= 0:
            candidatos.append((f0-1, c0))
        if f0+1 < filas:
            candidatos.append((f0+1, c0))
        candidatos.append((f0, (c0-1) % cols))
        candidatos.append((f0, (c0+1) % cols))

        mejor = None
        mejor_val = None
        for (r, c) in candidatos:
            tipo = int(self.matriz_ref[r, c])
            if not TIPOS_CASILLA[tipo]().es_transitable_cazador():
                continue
            dh = abs(c - objetivo_c)
            dh = min(dh, cols - dh)
            dist = abs(r - objetivo_f) + dh
            if mejor is None:
                mejor = (r, c); mejor_val = dist
            else:
                if perseguir:
                    if dist < mejor_val:
                        mejor, mejor_val = (r, c), dist
                else:
                    if dist > mejor_val:
                        mejor, mejor_val = (r, c), dist
        if mejor is None:
            return self.posicion
        self.posicion = mejor
        return mejor

    def mover_hacia_objetivo(self, objetivo, perseguir=True):
        return self.mover_greedy(objetivo, perseguir=perseguir)

# ----------------------------------------------------
#   CLASE JUEGO (integrada con registro y puntajes)
# ----------------------------------------------------
class Juego:
    TAM_CELDA = 28
    PADDING = 8

    def __init__(self, root, modo):
        # modo: 1 = Escapa, 2 = Cazador
        self.root = root
        self.modo = "escapa" if modo == 1 else "cazador"
        # Pedir parámetros (tamaño, cazadores, velocidad)
        self._pedir_parametros()

    def _pedir_parametros(self):
        # diálogo simple para elegir tamaño, número de cazadores, velocidad (som los que están despues de TEXT entre comillas)
        dlg = tk.Toplevel(self.root)
        dlg.title("Parámetros de la partida")
        tk.Label(dlg, text="Tamaño del mapa:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        tam = tk.IntVar(value=2)
        tk.Radiobutton(dlg, text="Pequeño (10x10)", variable=tam, value=1).grid(row=0, column=1, sticky="w")
        tk.Radiobutton(dlg, text="Mediano (15x21)", variable=tam, value=2).grid(row=0, column=2, sticky="w")
        tk.Radiobutton(dlg, text="Grande (20x35)", variable=tam, value=3).grid(row=0, column=3, sticky="w")

        tk.Label(dlg, text="Número de cazadores:").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        n_caz = tk.IntVar(value=3)
        tk.Spinbox(dlg, from_=1, to=8, textvariable=n_caz, width=6).grid(row=1, column=1, sticky="w")

        tk.Label(dlg, text="Velocidad (1-5):").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        vel = tk.IntVar(value=2)
        tk.Scale(dlg, from_=1, to=5, orient="horizontal", variable=vel, length=160).grid(row=2, column=1, columnspan=2, sticky="w")

        def continuar():
            v = tam.get()
            if v == 1:
                filas, cols = 10, 10
            elif v == 2:
                filas, cols = 15, 21
            else:
                filas, cols = 20, 35
            self.filas = filas
            self.columnas = cols
            self.numero_cazadores = max(1, min(8, n_caz.get()))
            self.velocidad = max(1, min(5, vel.get()))
            dlg.destroy()
            self._inicializar_partida()

        tk.Button(dlg, text="Iniciar", command=continuar).grid(row=3, column=1, pady=10)
        tk.Button(dlg, text="Cancelar", command=lambda: self._volver_menu(dlg)).grid(row=3, column=2, pady=10)

    def _volver_menu(self, dlg):
        dlg.destroy()
        # volver al menu inicial
        for w in self.root.winfo_children(): w.destroy()
        MenuInicial(self.root)

    def _inicializar_partida(self):
        # Generar mapa validado
        generador = GeneradorMapa(self.filas, self.columnas)
        matriz, inicio, salida = generador.generar_hasta_valido()
        if matriz is None:
            messagebox.showerror("Error", "No se pudo generar un mapa válido.")
            for w in self.root.winfo_children(): w.destroy()
            MenuInicial(self.root)
            return

        self.matriz = matriz
        self.posicion_jugador = inicio
        self.posicion_salida = salida

        # matrices booleanas
        self.transitable_jugador = np.vectorize(lambda t: TIPOS_CASILLA[int(t)]().es_transitable_jugador())(self.matriz)
        self.transitable_cazador = np.vectorize(lambda t: TIPOS_CASILLA[int(t)]().es_transitable_cazador())(self.matriz)
        self.es_salida = (self.matriz == 4)

        # pellets
        self.pellets = np.zeros_like(self.matriz, dtype=np.uint8)
        self._colocar_pellets()

        # trampas
        self.trampas = {}
        self.ultima_colocacion = 0.0
        self.cooldown_trampa = 5.0
        self.max_trampas = 3

        # enemigos
        self.enemigos = []
        self._colocar_enemigos()

        # puntajes y metas
        self.puntos = 0
        self.momento_inicio = None

        # modo cazador contadores
        self.cazadores_eliminados = 0
        self.cazadores_escapados = 0
        self.meta_cazadores = max(5, self.numero_cazadores * 2)  # ejemplo: meta para ganar en modo cazador

        # canvas y UI
        ancho = self.PADDING*2 + self.columnas * self.TAM_CELDA
        alto = self.PADDING*2 + self.filas * self.TAM_CELDA + 80
        self.canvas = tk.Canvas(self.root, width=ancho, height=alto, bg="#071021", highlightthickness=0)
        self.canvas.pack()

        # items
        self.item_celda = [[None for _ in range(self.columnas)] for _ in range(self.filas)]
        self.item_pellet = {}
        self.item_trampa = {}
        self.item_enemigo = {}
        self.item_jugador = None

        # estado y controles
        self.juego_activo = False
        self.direccion_actual = None
        self.sprint = False
        self.energia = 100.0
        self.energia_max = 100.0
        self.player_job = None
        self.enemies_job = None
        self.hud_job = None

        self._configurar_controles()
        self._dibujar_mapa_estatica()
        self._dibujar_pellets_iniciales()
        self._crear_items_jugador_y_enemigos()
        self.crear_hud()

    # --------------------------
    # Inicializaciones
    # --------------------------
    def _colocar_pellets(self):
        caminos = np.where(self.matriz == 0)
        for f, c in zip(caminos[0], caminos[1]):
            if random.random() < 0.88:
                self.pellets[f, c] = 1
        if self.posicion_salida:
            sf, sc = self.posicion_salida
            self.pellets[sf, sc] = 0

    def _colocar_enemigos(self):
        posiciones = []
        intentos = 0
        while len(posiciones) < self.numero_cazadores and intentos < 4000:
            i = random.randint(0, self.filas-1)
            j = random.randint(0, self.columnas-1)
            if (i,j) != self.posicion_jugador and self.transitable_cazador[i,j] and not self.es_salida[i,j]:
                if (i,j) not in posiciones:
                    posiciones.append((i,j))
            intentos += 1
        self.enemigos = [Enemigo(idx+1, pos, self.matriz) for idx,pos in enumerate(posiciones)]

    # --------------------------
    # Dibujo
    # --------------------------
    def _dibujar_mapa_estatica(self):
        colores = {0: "#10202b", 1: "#0b3a22", 2: "#4b2b1f", 3: "#081142", 4: "#8b0000"}
        for i in range(self.filas):
            for j in range(self.columnas):
                x1 = self.PADDING + j*self.TAM_CELDA
                y1 = self.PADDING + i*self.TAM_CELDA
                x2 = x1 + self.TAM_CELDA - 1
                y2 = y1 + self.TAM_CELDA - 1
                tipo = int(self.matriz[i,j])
                color = colores.get(tipo, "#111111")
                if tipo == 3:
                    rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#27408b", width=2)
                elif tipo == 4:
                    rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#ff4040", width=2)
                else:
                    rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#0b1822")
                self.item_celda[i][j] = rect

    def _dibujar_pellets_iniciales(self):
        for i in range(self.filas):
            for j in range(self.columnas):
                if self.pellets[i,j] == 1:
                    cx = self.PADDING + j*self.TAM_CELDA + self.TAM_CELDA//2
                    cy = self.PADDING + i*self.TAM_CELDA + self.TAM_CELDA//2
                    r = max(2, self.TAM_CELDA//12)
                    item = self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="#f7c948", outline="")
                    self.item_pellet[(i,j)] = item

    def _crear_items_jugador_y_enemigos(self):
        f, c = self.posicion_jugador
        x = self.PADDING + c*self.TAM_CELDA + self.TAM_CELDA//6
        y = self.PADDING + f*self.TAM_CELDA + self.TAM_CELDA//6
        size = self.TAM_CELDA - self.TAM_CELDA//3
        self.item_jugador = self.canvas.create_oval(x, y, x+size, y+size, fill="#00b4d8", outline="#caf0f8", width=2)
        for idx, enem in enumerate(self.enemigos):
            ef, ec = enem.posicion
            ex = self.PADDING + ec*self.TAM_CELDA + self.TAM_CELDA//8
            ey = self.PADDING + ef*self.TAM_CELDA + self.TAM_CELDA//8
            ew = self.TAM_CELDA - self.TAM_CELDA//4
            color = "#ff8c42" if idx % 2 == 0 else "#ff6bcb"
            item = self.canvas.create_rectangle(ex, ey, ex+ew, ey+ew, fill=color, outline="#ffffff", width=1)
            self.item_enemigo[enem.id] = item

    # --------------------------
    # Controles
    # --------------------------
    def _configurar_controles(self):
        mapa_keys = {
            "Up":"arriba","w":"arriba","k":"arriba",
            "Down":"abajo","s":"abajo","j":"abajo",
            "Left":"izquierda","a":"izquierda","h":"izquierda",
            "Right":"derecha","d":"derecha","l":"derecha"
        }
        for key, dir_ in mapa_keys.items():
            self.root.bind(f"<KeyPress-{key}>", lambda e, d=dir_: self._on_press(d))
            self.root.bind(f"<KeyRelease-{key}>", lambda e, d=dir_: self._on_release(d))
        self.root.bind("<KeyPress-Shift_L>", lambda e: setattr(self, 'sprint', True))
        self.root.bind("<KeyRelease-Shift_L>", lambda e: setattr(self, 'sprint', False))
        self.root.bind("<KeyPress-Shift_R>", lambda e: setattr(self, 'sprint', True))
        self.root.bind("<KeyRelease-Shift_R>", lambda e: setattr(self, 'sprint', False))
        self.root.bind("<t>", lambda e: self.colocar_trampa())
        self.root.bind("<space>", lambda e: self._toggle_inicio())

    def _on_press(self, direccion):
        self.direccion_actual = direccion
        if self.juego_activo and self.player_job is None:
            self._programar_movimiento_jugador()
        if not self.juego_activo:
            self._mover_jugador_una_vez()

    def _on_release(self, direccion):
        if self.direccion_actual == direccion:
            self.direccion_actual = None

    # --------------------------
    # Movimiento jugador
    # --------------------------
    def _toggle_inicio(self):
        if not self.juego_activo:
            self.juego_activo = True
            self.momento_inicio = time.time()
            if self.player_job is None:
                self._programar_movimiento_jugador()
            if self.enemies_job is None:
                self._programar_movimiento_enemigos()
            if self.hud_job is None:
                self._programar_hud()
        else:
            self.juego_activo = False
            self._cancelar_jobs()

    def _cancelar_jobs(self):
        if self.player_job:
            try: self.root.after_cancel(self.player_job)
            except Exception: pass
            self.player_job = None
        if self.enemies_job:
            try: self.root.after_cancel(self.enemies_job)
            except Exception: pass
            self.enemies_job = None
        if self.hud_job:
            try: self.root.after_cancel(self.hud_job)
            except Exception: pass
            self.hud_job = None

    def _programar_movimiento_jugador(self):
        if not self.juego_activo:
            return
        base_ms = 140
        if self.sprint and self.energia > 5:
            intervalo = max(50, int(base_ms / 2))
        else:
            intervalo = base_ms
        self.player_job = self.root.after(intervalo, self._movimiento_jugador_job)

    def _movimiento_jugador_job(self):
        self.player_job = None
        if not self.juego_activo:
            return
        if self.direccion_actual:
            self._mover_jugador_una_vez()
            if self.sprint and self.energia > 0:
                self.energia = max(0.0, self.energia - 6.0)
            else:
                self.energia = min(self.energia_max, self.energia + 2.0)
        else:
            self.energia = min(self.energia_max, self.energia + 2.0)
        self._programar_movimiento_jugador()

    def _mover_jugador_una_vez(self):
        if not self.direccion_actual:
            return
        f, c = self.posicion_jugador
        if self.direccion_actual == "arriba":
            destino = (f-1, c)
        elif self.direccion_actual == "abajo":
            destino = (f+1, c)
        elif self.direccion_actual == "izquierda":
            destino = (f, c-1)
        elif self.direccion_actual == "derecha":
            destino = (f, c+1)
        else:
            destino = (f, c)
        destino = (destino[0], destino[1] % self.columnas)
        if destino[0] < 0 or destino[0] >= self.filas:
            return
        if not self.transitable_jugador[destino]:
            return
        self._actualizar_posicion_jugador(destino)

    def _actualizar_posicion_jugador(self, destino):
        prev = self.posicion_jugador
        self.posicion_jugador = destino
        try:
            if not self.canvas.winfo_exists():
                return
        except Exception:
            return
        try:
            bbox = self.canvas.coords(self.item_jugador)
            if not bbox:
                f, c = destino
                x = self.PADDING + c*self.TAM_CELDA + self.TAM_CELDA//6
                y = self.PADDING + f*self.TAM_CELDA + self.TAM_CELDA//6
                size = self.TAM_CELDA - self.TAM_CELDA//3
                self.item_jugador = self.canvas.create_oval(x, y, x+size, y+size, fill="#00b4d8", outline="#caf0f8", width=2)
            else:
                dx = (destino[1] - prev[1]) * self.TAM_CELDA
                if abs(dx) > (self.columnas//2)*self.TAM_CELDA:
                    new_x = self.PADDING + destino[1]*self.TAM_CELDA + self.TAM_CELDA//6
                    new_y = self.PADDING + destino[0]*self.TAM_CELDA + self.TAM_CELDA//6
                    w = bbox[2]-bbox[0]; h = bbox[3]-bbox[1]
                    self.canvas.coords(self.item_jugador, new_x, new_y, new_x + w, new_y + h)
                else:
                    self.canvas.move(self.item_jugador, dx, (destino[0] - prev[0]) * self.TAM_CELDA)
        except tk.TclError:
            return

        # recoger pellet
        if self.pellets[destino]:
            self.pellets[destino] = 0
            item = self.item_pellet.pop(destino, None)
            if item:
                try:
                    if self.canvas.winfo_exists(): self.canvas.delete(item)
                except Exception:
                    pass
            self.puntos += 5

        # llegada a salida
        if self.es_salida[destino]:
            if self.modo == "escapa":
                # calcular puntaje y guardar
                tiempo = time.time() - self.momento_inicio if self.momento_inicio else 0.0
                # Fórmula: base por tiempo inverso + bonus por dificultad
                base = int(max(1, 1000.0 / (tiempo + 1.0)))
                dificultad = self.numero_cazadores + self.velocidad
                puntaje_final = base + dificultad * 50 + self.puntos
                actualizar_top5("escapa", JUGADOR_NOMBRE, puntaje_final)
                messagebox.showinfo("Victoria", f"Has llegado a la salida.\nTiempo: {tiempo:.2f}s\nPuntos: {self.puntos}\nPuntaje: {puntaje_final}")
                self._volver_menu_post()
                return

        # colisión con enemigos
        for enem in self.enemigos:
            if enem.vivo and enem.posicion == destino:
                if self.modo == "escapa":
                    messagebox.showinfo("Derrota", f"Has sido alcanzado por un cazador.\nPuntos: {self.puntos}")
                    self._volver_menu_post()
                    return
                else:
                    # modo cazador: jugador atrapa enemigo
                    enem.vivo = False
                    self.puntos += 30
                    self.cazadores_eliminados += 1
                    item = self.item_enemigo.pop(enem.id, None)
                    if item:
                        try:
                            if self.canvas.winfo_exists(): self.canvas.delete(item)
                        except Exception:
                            pass
                    # recompensa doble especificada por requisitos:
                    recompensa = 20
                    self.puntos += recompensa  # sumar la recompensa
                    # programar respawn
                    self.root.after(10000, lambda e=enem: self._respawn_enemigo(e))
                    # comprobar condición de victoria modo cazador
                    if self.cazadores_eliminados >= self.meta_cazadores:
                        actualizar_top5("cazador", JUGADOR_NOMBRE, self.puntos)
                        messagebox.showinfo("Victoria", f"¡Has atrapado a la meta de cazadores!\nPuntaje final: {self.puntos}")
                        self._volver_menu_post()
                    return

    # --------------------------
    # Movimiento enemigos
    # --------------------------
    def _programar_movimiento_enemigos(self):
        if not self.juego_activo:
            return
        intervalo = max(160, int(700 / self.velocidad))
        self.enemies_job = self.root.after(intervalo, self._movimiento_enemigos_job)

    def _movimiento_enemigos_job(self):
        self.enemies_job = None
        if not self.juego_activo:
            return
        perseguir = (self.modo == "escapa")
        try:
            if not self.canvas.winfo_exists(): return
        except Exception:
            return
        for enem in self.enemigos:
            if not enem.vivo:
                continue
            prev = enem.posicion
            enem.mover_hacia_objetivo(self.posicion_jugador, perseguir=perseguir)
            nueva = enem.posicion
            if prev != nueva:
                item = self.item_enemigo.get(enem.id)
                if item:
                    try:
                        bbox = self.canvas.coords(item)
                        if not bbox:
                            ex = self.PADDING + nueva[1]*self.TAM_CELDA + self.TAM_CELDA//8
                            ey = self.PADDING + nueva[0]*self.TAM_CELDA + self.TAM_CELDA//8
                            ew = self.TAM_CELDA - self.TAM_CELDA//4
                            color = "#ff8c42" if (enem.id-1) % 2 == 0 else "#ff6bcb"
                            self.item_enemigo[enem.id] = self.canvas.create_rectangle(ex, ey, ex+ew, ey+ew, fill=color, outline="#ffffff", width=1)
                        else:
                            dx = (nueva[1] - prev[1]) * self.TAM_CELDA
                            if abs(dx) > (self.columnas//2)*self.TAM_CELDA:
                                new_x = self.PADDING + nueva[1]*self.TAM_CELDA + self.TAM_CELDA//8
                                new_y = self.PADDING + nueva[0]*self.TAM_CELDA + self.TAM_CELDA//8
                                w = bbox[2]-bbox[0]; h = bbox[3]-bbox[1]
                                self.canvas.coords(item, new_x, new_y, new_x+w, new_y+h)
                            else:
                                self.canvas.move(item, dx, (nueva[0] - prev[0]) * self.TAM_CELDA)
                    except tk.TclError:
                        pass

            # si pisó trampa
            if enem.vivo and enem.posicion in self.trampas:
                enem.vivo = False
                self.puntos += 20
                item = self.item_enemigo.pop(enem.id, None)
                if item:
                    try:
                        if self.canvas.winfo_exists(): self.canvas.delete(item)
                    except Exception:
                        pass
                titem = self.item_trampa.pop(enem.posicion, None)
                if titem:
                    try:
                        if self.canvas.winfo_exists(): self.canvas.delete(titem)
                    except Exception:
                        pass
                try:
                    del self.trampas[enem.posicion]
                except KeyError:
                    pass
                self.root.after(10000, lambda e=enem: self._respawn_enemigo(e))

            # comprobar si enemigo llegó a la salida (solo cuenta en modo cazador)
            if self.modo == "cazador" and enem.vivo and self.es_salida[enem.posicion]:
                # penalizar
                self.cazadores_escapados += 1
                self.puntos -= 10  # penalización por escapar
                # si puntaje baja de 0, derrota
                if self.puntos < 0:
                    actualizar_top5("cazador", JUGADOR_NOMBRE, max(0, self.puntos))
                    messagebox.showerror("Derrota", "Demasiados cazadores han escapado. Puntaje: {}".format(self.puntos))
                    self._volver_menu_post()
                    return
                # forzar respawn para mantener dinamica
                enem.vivo = False
                item = self.item_enemigo.pop(enem.id, None)
                if item:
                    try:
                        if self.canvas.winfo_exists(): self.canvas.delete(item)
                    except Exception:
                        pass
                self.root.after(10000, lambda e=enem: self._respawn_enemigo(e))

        # colisión jugador - enemigo (al final)
        for enem in self.enemigos:
            if enem.vivo and enem.posicion == self.posicion_jugador:
                if self.modo == "escapa":
                    messagebox.showinfo("Derrota", f"Has sido alcanzado por un cazador.\nPuntos: {self.puntos}")
                    self._volver_menu_post()
                    return
                else:
                    enem.vivo = False
                    self.puntos += 30
                    self.cazadores_eliminados += 1
                    item = self.item_enemigo.pop(enem.id, None)
                    if item:
                        try:
                            if self.canvas.winfo_exists(): self.canvas.delete(item)
                        except Exception:
                            pass
                    self.root.after(10000, lambda e=enem: self._respawn_enemigo(e))
                    if self.cazadores_eliminados >= self.meta_cazadores:
                        actualizar_top5("cazador", JUGADOR_NOMBRE, self.puntos)
                        messagebox.showinfo("Victoria", f"¡Has atrapado a la meta de cazadores!\nPuntaje final: {self.puntos}")
                        self._volver_menu_post()
                        return

        self._programar_movimiento_enemigos()

    def _respawn_enemigo(self, enemigo):
        intentos = 0
        while intentos < 2000:
            i = random.randint(0, self.filas-1)
            j = random.randint(0, self.columnas-1)
            if self.transitable_cazador[i,j] and (i,j) != self.posicion_jugador and not self.es_salida[i,j]:
                enemigo.posicion = (i,j)
                enemigo.vivo = True
                try:
                    if self.canvas.winfo_exists():
                        idx = enemigo.id - 1
                        ex = self.PADDING + j*self.TAM_CELDA + self.TAM_CELDA//8
                        ey = self.PADDING + i*self.TAM_CELDA + self.TAM_CELDA//8
                        ew = self.TAM_CELDA - self.TAM_CELDA//4
                        color = "#ff8c42" if idx % 2 == 0 else "#ff6bcb"
                        item = self.canvas.create_rectangle(ex, ey, ex+ew, ey+ew, fill=color, outline="#ffffff", width=1)
                        self.item_enemigo[enemigo.id] = item
                except Exception:
                    pass
                return
            intentos += 1
        enemigo.vivo = True

    # --------------------------
    # Trampas
    # --------------------------
    def colocar_trampa(self):
        if self.modo != "escapa" or not self.juego_activo:
            return
        ahora = time.time()
        if len(self.trampas) >= self.max_trampas:
            return
        if ahora - self.ultima_colocacion < self.cooldown_trampa:
            return
        pos = self.posicion_jugador
        if pos in self.trampas:
            return
        self.trampas[pos] = ahora
        self.ultima_colocacion = ahora
        try:
            if self.canvas.winfo_exists():
                x = self.PADDING + pos[1]*self.TAM_CELDA + 6
                y = self.PADDING + pos[0]*self.TAM_CELDA + 6
                item = self.canvas.create_rectangle(x, y, x + self.TAM_CELDA - 12, y + self.TAM_CELDA - 12, fill="#551A8B", outline="#ffccff")
                self.item_trampa[pos] = item
        except Exception:
            pass

    # --------------------------
    # HUD
    # --------------------------
    def crear_hud(self):
        try:
            y = self.PADDING + self.filas*self.TAM_CELDA + 10
            self.hud_text = self.canvas.create_text(12, y, anchor="nw", fill="white", text="", font=("Helvetica", 11, "bold"))
            bx = 12; by = y + 22; bw = 200; bh = 12
            self.hud_bar_outline = self.canvas.create_rectangle(bx, by, bx+bw, by+bh, outline="#555")
            self.hud_bar_fill = self.canvas.create_rectangle(bx, by, bx, by+bh, fill="#00FF66", outline="")
            modo_texto = f"Modo: {'Escapa' if self.modo=='escapa' else 'Cazador'} | Cazadores: {self.numero_cazadores} | Vel: {self.velocidad}"
            self.hud_info = self.canvas.create_text(12, by+bh+8, anchor="nw", fill="white", text=modo_texto, font=("Helvetica", 10))
        except Exception:
            self.hud_text = None
            self.hud_bar_outline = None
            self.hud_bar_fill = None
            self.hud_info = None

    def _programar_hud(self):
        if not self.juego_activo:
            return
        self.hud_job = self.root.after(200, self._actualizar_hud)

    def _actualizar_hud(self):
        self.hud_job = None
        if not self.juego_activo:
            return
        if not hasattr(self, "hud_text") or self.hud_text is None:
            try:
                self.crear_hud()
            except Exception:
                return
        try:
            if not self.canvas.winfo_exists(): return
        except Exception:
            return
        try:
            tiempo = time.time() - self.momento_inicio if self.momento_inicio else 0.0
            texto = f"Puntos: {self.puntos}    Tiempo: {tiempo:.1f}s    Trampas: {len(self.trampas)}/{self.max_trampas}"
            try:
                self.canvas.itemconfigure(self.hud_text, text=texto)
            except Exception:
                pass
            if self.hud_bar_fill and self.hud_bar_outline:
                try:
                    bx1, by1, bx2, by2 = self.canvas.coords(self.hud_bar_outline)
                    bw = bx2 - bx1
                    porcentaje = max(0.0, min(1.0, self.energia / self.energia_max))
                    self.canvas.coords(self.hud_bar_fill, bx1, by1, bx1 + bw * porcentaje, by2)
                except Exception:
                    pass
        finally:
            self._programar_hud()

    # --------------------------
    # Finalización y volver al menú
    # --------------------------
    def _volver_menu_post(self):
        # cancelar jobs y volver al menú
        self.juego_activo = False
        self._cancelar_jobs()
        try:
            for w in self.root.winfo_children(): w.destroy()
        except Exception:
            pass
        MenuInicial(self.root)

# ----------------------------------------------------
#   INICIO 
# ----------------------------------------------------
if __name__ == "__main__":
    init_puntajes_globals()
    root = tk.Tk()
    root.configure(bg="#071021")  
    MenuInicial(root)
    root.mainloop()




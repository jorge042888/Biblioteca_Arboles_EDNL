# ============================================================
#  SISTEMA DE BIBLIOTECA
#  Estructuras de Datos No Lineales - 5to Semestre
#
#  ¿Qué estructura usamos para cada cosa?
#   - BST  → catálogo de libros  (se ordena por ISBN)
#   - AVL  → registro de usuarios (se ordena por ID)
#   - Cola (deque) → lista de espera por libro (primero en llegar, primero en salir)
#
#  Diferencia BST vs AVL:
#   - BST: inserta sin preocuparse de la altura. Si insertas datos
#     ya ordenados, el árbol se vuelve una línea recta (lento).
#   - AVL: después de cada inserción o borrado revisa si el árbol
#     está "inclinado" y lo corrige con rotaciones. Siempre queda
#     balanceado → búsquedas más rápidas garantizadas.
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque


# ============================================================
#  PARTE 1: ÁRBOL BST — Catálogo de Libros
# ============================================================

class NodoLibro:
    # Cada nodo guarda un libro y apunta a sus dos hijos (izq y der)
    def __init__(self, isbn, titulo, autor):
        self.isbn = isbn
        self.titulo  = titulo
        self.autor = autor
        self.disponible = True    # True = está en el estante
        self.prestado_a = None    # ID del usuario que lo tiene
        self.cola_espera = deque() # usuarios que esperan este libro
        self.izq = None    # hijo con ISBN menor
        self.der = None    # hijo con ISBN mayor


class BST_Libros:
    def __init__(self):
        self.raiz = None

    # Devuelve el nodo con el ISBN más pequeño dentro de un subárbol.
    # Se usa al eliminar un nodo con dos hijos (necesitamos el "sucesor inorden")
    def _min_nodo(self, nodo):
        while nodo.izq:
            nodo = nodo.izq
        return nodo

    # --- Insertar ---
    def insertar(self, isbn, titulo, autor):
        if self.buscar(isbn):
            return False  # ya existe ese ISBN
        self.raiz = self._insertar(self.raiz, isbn, titulo, autor)
        return True

    def _insertar(self, nodo, isbn, titulo, autor):
        if nodo is None:
            return NodoLibro(isbn, titulo, autor)
        if isbn < nodo.isbn:
            nodo.izq = self._insertar(nodo.izq, isbn, titulo, autor)
        else:
            nodo.der = self._insertar(nodo.der, isbn, titulo, autor)
        return nodo

    # --- Buscar por ISBN exacto ---
    def buscar(self, isbn):
        nodo = self.raiz
        while nodo:
            if isbn == nodo.isbn:
                return nodo
            nodo = nodo.izq if isbn < nodo.isbn else nodo.der
        return None

    # --- Buscar por parte del título (recorre todo el árbol) ---
    def buscar_titulo(self, texto):
        resultados = []
        self._buscar_titulo(self.raiz, texto.lower(), resultados)
        return resultados

    def _buscar_titulo(self, nodo, texto, res):
        if nodo:
            if texto in nodo.titulo.lower():
                res.append(nodo)
            self._buscar_titulo(nodo.izq, texto, res)
            self._buscar_titulo(nodo.der, texto, res)

    # --- Eliminar ---
    def eliminar(self, isbn):
        self.raiz, ok = self._eliminar(self.raiz, isbn)
        return ok

    def _eliminar(self, nodo, isbn):
        if nodo is None:
            return None, False
        ok = False
        if isbn < nodo.isbn:
            nodo.izq, ok = self._eliminar(nodo.izq, isbn)
        elif isbn > nodo.isbn:
            nodo.der, ok = self._eliminar(nodo.der, isbn)
        else:
            ok = True
            if nodo.izq is None: return nodo.der, ok   # sin hijo izq → subir hijo der
            if nodo.der is None: return nodo.izq, ok   # sin hijo der → subir hijo izq
            # Tiene dos hijos: reemplazar con el sucesor (mínimo del subárbol derecho)
            sucesor = self._min_nodo(nodo.der)
            nodo.isbn, nodo.titulo, nodo.autor = sucesor.isbn, sucesor.titulo, sucesor.autor
            nodo.disponible, nodo.prestado_a   = sucesor.disponible, sucesor.prestado_a
            nodo.cola_espera                   = sucesor.cola_espera
            nodo.der, _ = self._eliminar(nodo.der, sucesor.isbn)
        return nodo, ok

    # --- Inorden: devuelve la lista de libros ordenada por ISBN ---
    def inorden(self):
        lista = []
        self._inorden(self.raiz, lista)
        return lista

    def _inorden(self, nodo, lista):
        if nodo:
            self._inorden(nodo.izq, lista)
            lista.append(nodo)
            self._inorden(nodo.der, lista)

    # --- Vista del árbol de arriba hacia abajo (raíz arriba, hijos abajo) ---
    def mostrar_arbol(self):
        if not self.raiz:
            return "(árbol vacío)"
        estado = "DISP" if self.raiz.disponible else f"PREST→{self.raiz.prestado_a}"
        lineas = [f"[{self.raiz.isbn}] {self.raiz.titulo}  ({estado})  ← raíz"]
        self._dibujar(self.raiz, "", lineas)
        return "\n".join(lineas)

    def _dibujar(self, nodo, prefijo, lineas):
        tiene_izq = nodo.izq is not None
        tiene_der = nodo.der is not None
        if not tiene_izq and not tiene_der:
            return  # es hoja, no tiene hijos que mostrar

        # Hijo izquierdo
        if tiene_izq:
            conector = "├── IZQ: " if tiene_der else "└── IZQ: "
            estado = "DISP" if nodo.izq.disponible else f"PREST→{nodo.izq.prestado_a}"
            lineas.append(prefijo + conector + f"[{nodo.izq.isbn}] {nodo.izq.titulo}  ({estado})")
            extension = "│   " if tiene_der else "    "
            self._dibujar(nodo.izq, prefijo + extension, lineas)
        else:
            lineas.append(prefijo + "├── IZQ: (vacío)")

        # Hijo derecho
        if tiene_der:
            estado = "DISP" if nodo.der.disponible else f"PREST→{nodo.der.prestado_a}"
            lineas.append(prefijo + "└── DER: " + f"[{nodo.der.isbn}] {nodo.der.titulo}  ({estado})")
            self._dibujar(nodo.der, prefijo + "    ", lineas)
        else:
            lineas.append(prefijo + "└── DER: (vacío)")


# ============================================================
#  PARTE 2: ÁRBOL AVL — Registro de Usuarios
# ============================================================
#
#  El AVL es un BST que se "autobalancea".
#  Después de insertar o borrar, calcula el factor de balance:
#    fb = altura(hijo_izq) - altura(hijo_der)
#  Si fb queda fuera de [-1, 0, 1] → aplica una rotación.
#
#  4 rotaciones posibles:
#    Caso II (fb>1, hijo izq pesado a la izq) → rotar a la derecha
#    Caso DD (fb<-1, hijo der pesado a la der) → rotar a la izquierda
#    Caso ID (fb>1, hijo izq pesado a la der) → doble rotación izq-der
#    Caso DI (fb<-1, hijo der pesado a la izq) → doble rotación der-izq
# ============================================================

class NodoUsuario:
    # Igual que NodoLibro pero guarda 'altura' para calcular el balance
    def __init__(self, id_usuario, nombre):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.libros_prestados = []  # ISBNs que tiene actualmente
        self.izq = None
        self.der = None
        self.altura = 1   # toda hoja nueva tiene altura 1


class AVL_Usuarios:
    def __init__(self):
        self.raiz = None

    # --- Utilidades de altura y balance ---
    def _altura(self, n):
        return n.altura if n else 0

    def _fb(self, n):
        return self._altura(n.izq) - self._altura(n.der) if n else 0

    def _act_altura(self, n):
        n.altura = 1 + max(self._altura(n.izq), self._altura(n.der))

    def _min_nodo(self, nodo):
        while nodo.izq:
            nodo = nodo.izq
        return nodo

    # --- Rotaciones ---
    def _rot_der(self, y):
        # Rotación simple a la DERECHA (caso II)
        x = y.izq;  y.izq = x.der;  x.der = y
        self._act_altura(y);  self._act_altura(x)
        return x

    def _rot_izq(self, x):
        # Rotación simple a la IZQUIERDA (caso DD)
        y = x.der;  x.der = y.izq;  y.izq = x
        self._act_altura(x);  self._act_altura(y)
        return y

    # --- Rebalancear: aplica la rotación correcta según el fb ---
    # Se llama igual después de insertar y después de borrar
    def _rebalancear(self, nodo):
        self._act_altura(nodo)
        fb = self._fb(nodo)

        if fb > 1:                          # árbol inclinado a la izquierda
            if self._fb(nodo.izq) < 0:     # caso ID → rotar hijo izq a la izq primero
                nodo.izq = self._rot_izq(nodo.izq)
            return self._rot_der(nodo)      # caso II

        if fb < -1:                         # árbol inclinado a la derecha
            if self._fb(nodo.der) > 0:     # caso DI → rotar hijo der a la der primero
                nodo.der = self._rot_der(nodo.der)
            return self._rot_izq(nodo)      # caso DD

        return nodo  # ya está balanceado

    # --- Insertar ---
    def insertar(self, id_u, nombre):
        if self.buscar(id_u):
            return False
        self.raiz = self._insertar(self.raiz, id_u, nombre)
        return True

    def _insertar(self, nodo, id_u, nombre):
        # Paso 1: inserción normal (igual que BST)
        if nodo is None:
            return NodoUsuario(id_u, nombre)
        if id_u < nodo.id_usuario:
            nodo.izq = self._insertar(nodo.izq, id_u, nombre)
        elif id_u > nodo.id_usuario:
            nodo.der = self._insertar(nodo.der, id_u, nombre)
        else:
            return nodo  # duplicado
        # Paso 2: al regresar de la recursión, revisar y corregir el balance
        return self._rebalancear(nodo)

    # --- Buscar ---
    def buscar(self, id_u):
        nodo = self.raiz
        while nodo:
            if id_u == nodo.id_usuario:
                return nodo
            nodo = nodo.izq if id_u < nodo.id_usuario else nodo.der
        return None

    # --- Eliminar ---
    def eliminar(self, id_u):
        self.raiz, ok = self._eliminar(self.raiz, id_u)
        return ok

    def _eliminar(self, nodo, id_u):
        if nodo is None:
            return None, False
        ok = False
        if id_u < nodo.id_usuario:
            nodo.izq, ok = self._eliminar(nodo.izq, id_u)
        elif id_u > nodo.id_usuario:
            nodo.der, ok = self._eliminar(nodo.der, id_u)
        else:
            ok = True
            if nodo.izq is None: return nodo.der, ok
            if nodo.der is None: return nodo.izq, ok
            sucesor = self._min_nodo(nodo.der)
            nodo.id_usuario, nodo.nombre, nodo.libros_prestados = (
                sucesor.id_usuario, sucesor.nombre, sucesor.libros_prestados)
            nodo.der, _ = self._eliminar(nodo.der, sucesor.id_usuario)
        return self._rebalancear(nodo), ok

    # --- Inorden y visualización ---
    def inorden(self):
        lista = []
        self._inorden(self.raiz, lista)
        return lista

    def _inorden(self, nodo, lista):
        if nodo:
            self._inorden(nodo.izq, lista)
            lista.append(nodo)
            self._inorden(nodo.der, lista)

    def mostrar_arbol(self):
        if not self.raiz:
            return "(árbol vacío)"
        lineas = [f"[{self.raiz.id_usuario}] {self.raiz.nombre}  (h={self.raiz.altura}, fb={self._fb(self.raiz)})  ← raíz"]
        self._dibujar(self.raiz, "", lineas)
        return "\n".join(lineas)

    def _dibujar(self, nodo, prefijo, lineas):
        tiene_izq = nodo.izq is not None
        tiene_der = nodo.der is not None
        if not tiene_izq and not tiene_der:
            return  # es hoja

        if tiene_izq:
            n = nodo.izq
            conector = "├── IZQ: " if tiene_der else "└── IZQ: "
            lineas.append(prefijo + conector + f"[{n.id_usuario}] {n.nombre}  (h={n.altura}, fb={self._fb(n)})")
            extension = "│   " if tiene_der else "    "
            self._dibujar(n, prefijo + extension, lineas)
        else:
            lineas.append(prefijo + "├── IZQ: (vacío)")

        if tiene_der:
            n = nodo.der
            lineas.append(prefijo + "└── DER: " + f"[{n.id_usuario}] {n.nombre}  (h={n.altura}, fb={self._fb(n)})")
            self._dibujar(n, prefijo + "    ", lineas)
        else:
            lineas.append(prefijo + "└── DER: (vacío)")


# ============================================================
#  PARTE 3: INTERFAZ GRÁFICA — Tkinter
# ============================================================

class AppBiblioteca:

    # Helper: crea un campo (Label + Entry) en una fila del formulario
    def _campo(self, frame, texto, fila, ancho=22):
        tk.Label(frame, text=texto).grid(row=fila, column=0, sticky="w", pady=2)
        e = tk.Entry(frame, width=ancho)
        e.grid(row=fila, column=1, padx=6, pady=2, sticky="w")
        return e

    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Sistema de Biblioteca")
        self.ventana.geometry("860x600")

        self.libros   = BST_Libros()
        self.usuarios = AVL_Usuarios()
        self._cargar_datos_prueba()

        nb = ttk.Notebook(ventana)
        nb.pack(fill="both", expand=True, padx=8, pady=8)

        self._tab_libros(nb)
        self._tab_usuarios(nb)
        self._tab_prestamos(nb)
        self._tab_arboles(nb)

    def _cargar_datos_prueba(self):
        for isbn, titulo, autor in [
            ("978-003", "1984",                    "George Orwell"),
            ("978-001", "Cien Años de Soledad",    "Gabriel García Márquez"),
            ("978-005", "Fahrenheit 451",           "Ray Bradbury"),
            ("978-002", "El Principito",            "Antoine de Saint-Exupéry"),
            ("978-004", "Don Quijote de la Mancha", "Miguel de Cervantes"),
            ("978-006", "El Alquimista",            "Paulo Coelho"),
        ]:
            self.libros.insertar(isbn, titulo, autor)

        for id_u, nombre in [
            ("U003", "Carlos López"),
            ("U001", "Ana García"),
            ("U005", "María Martínez"),
            ("U002", "Juan Pérez"),
            ("U004", "Laura Díaz"),
        ]:
            self.usuarios.insertar(id_u, nombre)

    # ----------------------------------------------------------
    #  TAB 1 — Libros
    # ----------------------------------------------------------
    def _tab_libros(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="  Libros  ")

        fm = tk.LabelFrame(tab, text=" Agregar / Eliminar Libro ", padx=6, pady=6)
        fm.pack(fill="x", padx=10, pady=6)
        self.e_isbn   = self._campo(fm, "ISBN:",   0, ancho=22)
        self.e_titulo = self._campo(fm, "Título:", 1, ancho=32)
        self.e_autor  = self._campo(fm, "Autor:",  2, ancho=32)
        bf = tk.Frame(fm)
        bf.grid(row=3, column=0, columnspan=2, pady=4)
        tk.Button(bf, text="Agregar",  command=self._agregar_libro).pack(side="left", padx=4)
        tk.Button(bf, text="Eliminar", command=self._eliminar_libro).pack(side="left", padx=4)

        fb = tk.LabelFrame(tab, text=" Buscar ", padx=6, pady=6)
        fb.pack(fill="x", padx=10, pady=4)
        tk.Label(fb, text="ISBN o parte del título:").pack(side="left")
        self.e_buscar = tk.Entry(fb, width=28)
        self.e_buscar.pack(side="left", padx=6)
        tk.Button(fb, text="Buscar", command=self._buscar_libro).pack(side="left")

        ft = tk.LabelFrame(tab, text=" Catálogo  (recorrido inorden del BST → ordenado por ISBN) ", padx=6, pady=6)
        ft.pack(fill="both", expand=True, padx=10, pady=4)
        cols = ("ISBN", "Título", "Autor", "Estado")
        self.tbl_libros = ttk.Treeview(ft, columns=cols, show="headings", height=9)
        for c, w in zip(cols, [110, 240, 180, 220]):
            self.tbl_libros.heading(c, text=c)
            self.tbl_libros.column(c, width=w)
        self.tbl_libros.pack(fill="both", expand=True)
        self._refrescar_libros()

    def _agregar_libro(self):
        isbn, titulo, autor = self.e_isbn.get().strip(), self.e_titulo.get().strip(), self.e_autor.get().strip()
        if not isbn or not titulo or not autor:
            messagebox.showwarning("Atención", "Rellena los tres campos.")
            return
        if self.libros.insertar(isbn, titulo, autor):
            messagebox.showinfo("OK", f"'{titulo}' agregado al BST.")
            for e in (self.e_isbn, self.e_titulo, self.e_autor): e.delete(0, tk.END)
            self._refrescar_libros()
        else:
            messagebox.showerror("Error", f"Ya existe el ISBN '{isbn}'.")

    def _eliminar_libro(self):
        isbn = self.e_isbn.get().strip()
        if not isbn:
            messagebox.showwarning("Atención", "Ingresa el ISBN."); return
        libro = self.libros.buscar(isbn)
        if libro and not libro.disponible:
            messagebox.showerror("Error", "No se puede eliminar: el libro está prestado."); return
        if self.libros.eliminar(isbn):
            messagebox.showinfo("OK", f"ISBN '{isbn}' eliminado del BST.")
            self._refrescar_libros()
        else:
            messagebox.showerror("Error", f"No se encontró '{isbn}'.")

    def _buscar_libro(self):
        termino = self.e_buscar.get().strip()
        if not termino: return
        libro = self.libros.buscar(termino)
        if libro:
            cola  = list(libro.cola_espera) or ["—"]
            estado = "Disponible" if libro.disponible else f"Prestado a {libro.prestado_a}"
            messagebox.showinfo("Libro encontrado",
                f"ISBN  : {libro.isbn}\nTítulo: {libro.titulo}\nAutor : {libro.autor}\n"
                f"Estado: {estado}\nCola  : {', '.join(cola)}")
        else:
            res = self.libros.buscar_titulo(termino)
            if res:
                texto = "\n".join(f"• [{l.isbn}] {l.titulo}  ({'Disp.' if l.disponible else 'Prest.'})" for l in res)
                messagebox.showinfo(f"Resultados para '{termino}'", texto)
            else:
                messagebox.showinfo("Sin resultados", "No se encontró ningún libro.")

    def _refrescar_libros(self):
        for item in self.tbl_libros.get_children(): self.tbl_libros.delete(item)
        for libro in self.libros.inorden():
            if libro.disponible:
                estado = "Disponible"
            else:
                u = self.usuarios.buscar(libro.prestado_a)
                estado = f"Prestado a: {u.nombre if u else libro.prestado_a} ({libro.prestado_a})"
            self.tbl_libros.insert("", "end", values=(libro.isbn, libro.titulo, libro.autor, estado))

    # ----------------------------------------------------------
    #  TAB 2 — Usuarios
    # ----------------------------------------------------------
    def _tab_usuarios(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="  Usuarios  ")

        fm = tk.LabelFrame(tab, text=" Agregar / Eliminar / Buscar Usuario ", padx=6, pady=6)
        fm.pack(fill="x", padx=10, pady=6)
        self.e_id_u  = self._campo(fm, "ID Usuario:", 0, ancho=20)
        self.e_nom_u = self._campo(fm, "Nombre:",     1, ancho=30)
        bf = tk.Frame(fm)
        bf.grid(row=2, column=0, columnspan=2, pady=4)
        tk.Button(bf, text="Agregar",  command=self._agregar_usuario).pack(side="left", padx=4)
        tk.Button(bf, text="Eliminar", command=self._eliminar_usuario).pack(side="left", padx=4)
        tk.Button(bf, text="Buscar",   command=self._buscar_usuario).pack(side="left", padx=4)

        ft = tk.LabelFrame(tab, text=" Lista de Usuarios  (recorrido inorden del AVL → ordenado por ID) ", padx=6, pady=6)
        ft.pack(fill="both", expand=True, padx=10, pady=4)
        cols = ("ID", "Nombre", "Libros prestados", "Altura", "Factor balance")
        self.tbl_usuarios = ttk.Treeview(ft, columns=cols, show="headings", height=10)
        for c, w in zip(cols, [90, 200, 260, 80, 110]):
            self.tbl_usuarios.heading(c, text=c)
            self.tbl_usuarios.column(c, width=w)
        self.tbl_usuarios.pack(fill="both", expand=True)
        self._refrescar_usuarios()

    def _agregar_usuario(self):
        id_u, nombre = self.e_id_u.get().strip(), self.e_nom_u.get().strip()
        if not id_u or not nombre:
            messagebox.showwarning("Atención", "Rellena ID y Nombre."); return
        if self.usuarios.insertar(id_u, nombre):
            messagebox.showinfo("OK", f"Usuario '{nombre}' insertado en el AVL.")
            for e in (self.e_id_u, self.e_nom_u): e.delete(0, tk.END)
            self._refrescar_usuarios()
        else:
            messagebox.showerror("Error", f"Ya existe el ID '{id_u}'.")

    def _eliminar_usuario(self):
        id_u = self.e_id_u.get().strip()
        if not id_u:
            messagebox.showwarning("Atención", "Ingresa el ID."); return
        u = self.usuarios.buscar(id_u)
        if u and u.libros_prestados:
            messagebox.showerror("Error", f"No se puede eliminar: tiene libros prestados.\n{', '.join(u.libros_prestados)}"); return
        if self.usuarios.eliminar(id_u):
            messagebox.showinfo("OK", f"Usuario '{id_u}' eliminado del AVL.")
            self._refrescar_usuarios()
        else:
            messagebox.showerror("Error", f"No se encontró '{id_u}'.")

    def _buscar_usuario(self):
        id_u = self.e_id_u.get().strip()
        if not id_u:
            messagebox.showwarning("Atención", "Ingresa el ID."); return
        u = self.usuarios.buscar(id_u)
        if u:
            prestados = ", ".join(u.libros_prestados) or "ninguno"
            messagebox.showinfo("Usuario encontrado",
                f"ID            : {u.id_usuario}\nNombre        : {u.nombre}\n"
                f"Libros        : {prestados}\nAltura nodo   : {u.altura}\n"
                f"Factor balance: {self.usuarios._fb(u)}  (AVL válido: entre -1 y 1)")
        else:
            messagebox.showinfo("No encontrado", f"No existe usuario con ID '{id_u}'.")

    def _refrescar_usuarios(self):
        for item in self.tbl_usuarios.get_children(): self.tbl_usuarios.delete(item)
        for u in self.usuarios.inorden():
            self.tbl_usuarios.insert("", "end",
                values=(u.id_usuario, u.nombre, ", ".join(u.libros_prestados) or "—", u.altura, self.usuarios._fb(u)))

    # ----------------------------------------------------------
    #  TAB 3 — Préstamos
    # ----------------------------------------------------------
    def _tab_prestamos(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="  Préstamos  ")

        fp = tk.LabelFrame(tab, text=" Gestión de Préstamos ", padx=6, pady=6)
        fp.pack(fill="x", padx=10, pady=6)
        self.e_p_isbn = self._campo(fp, "ISBN:",       0)
        self.e_p_id   = self._campo(fp, "ID Usuario:", 1)
        tk.Label(fp, text="(El campo 'ID Usuario' solo se usa al prestar o poner en cola)",
                 fg="gray").grid(row=2, column=0, columnspan=2, sticky="w", pady=2)
        bf = tk.Frame(fp)
        bf.grid(row=3, column=0, columnspan=2, pady=6)
        tk.Button(bf, text="Prestar",       command=self._prestar).pack(side="left", padx=4)
        tk.Button(bf, text="Devolver",      command=self._devolver).pack(side="left", padx=4)
        tk.Button(bf, text="Poner en cola", command=self._poner_en_cola).pack(side="left", padx=4)
        tk.Button(bf, text="Ver cola",      command=self._ver_cola).pack(side="left", padx=4)

    def _prestar(self):
        isbn, id_u = self.e_p_isbn.get().strip(), self.e_p_id.get().strip()
        if not isbn or not id_u:
            messagebox.showwarning("Atención", "Ingresa ISBN e ID de usuario."); return
        libro, usuario = self.libros.buscar(isbn), self.usuarios.buscar(id_u)
        if not libro:   messagebox.showerror("Error", f"No existe libro '{isbn}'."); return
        if not usuario: messagebox.showerror("Error", f"No existe usuario '{id_u}'."); return
        if not libro.disponible:
            messagebox.showwarning("No disponible", f"Prestado a '{libro.prestado_a}'. Usa 'Poner en cola'."); return
        libro.disponible = False
        libro.prestado_a = id_u
        usuario.libros_prestados.append(isbn)
        messagebox.showinfo("Préstamo exitoso", f"'{libro.titulo}' prestado a {usuario.nombre}.")
        self._refrescar_libros(); self._refrescar_usuarios()

    def _devolver(self):
        isbn = self.e_p_isbn.get().strip()
        if not isbn:
            messagebox.showwarning("Atención", "Ingresa el ISBN."); return
        libro = self.libros.buscar(isbn)
        if not libro:    messagebox.showerror("Error", f"No existe '{isbn}'."); return
        if libro.disponible: messagebox.showwarning("Aviso", "El libro no está prestado."); return

        # Quitar el libro del usuario anterior
        u_anterior = self.usuarios.buscar(libro.prestado_a)
        if u_anterior and isbn in u_anterior.libros_prestados:
            u_anterior.libros_prestados.remove(isbn)

        # Si hay cola, prestar al siguiente automáticamente (FIFO: popleft = el primero que entró)
        if libro.cola_espera:
            sig_id = libro.cola_espera.popleft()
            sig_u  = self.usuarios.buscar(sig_id)
            libro.prestado_a = sig_id
            if sig_u: sig_u.libros_prestados.append(isbn)
            nombre = sig_u.nombre if sig_u else sig_id
            messagebox.showinfo("Devolución + préstamo automático",
                f"Devuelto. Prestado automáticamente a {nombre} (siguiente en cola).")
        else:
            libro.disponible = True
            libro.prestado_a = None
            messagebox.showinfo("OK", f"'{libro.titulo}' devuelto y disponible.")

        self._refrescar_libros(); self._refrescar_usuarios()

    def _poner_en_cola(self):
        isbn, id_u = self.e_p_isbn.get().strip(), self.e_p_id.get().strip()
        if not isbn or not id_u:
            messagebox.showwarning("Atención", "Ingresa ISBN e ID."); return
        libro, usuario = self.libros.buscar(isbn), self.usuarios.buscar(id_u)
        if not libro:   messagebox.showerror("Error", f"No existe '{isbn}'."); return
        if not usuario: messagebox.showerror("Error", f"No existe '{id_u}'."); return
        if libro.disponible:
            messagebox.showinfo("Disponible", "El libro está libre. Usa 'Prestar' directamente."); return
        if id_u in libro.cola_espera:
            messagebox.showwarning("Ya en cola", f"{usuario.nombre} ya está esperando."); return
        libro.cola_espera.append(id_u)
        messagebox.showinfo("Cola", f"{usuario.nombre} está en posición {len(libro.cola_espera)}.")

    def _ver_cola(self):
        isbn = self.e_p_isbn.get().strip()
        if not isbn:
            messagebox.showwarning("Atención", "Ingresa el ISBN."); return
        libro = self.libros.buscar(isbn)
        if not libro:
            messagebox.showerror("Error", f"No existe '{isbn}'."); return
        cola = list(libro.cola_espera)
        if not cola:
            messagebox.showinfo("Cola vacía", f"Nadie espera '{libro.titulo}'.")
        else:
            texto = "\n".join(f"  {i+1}. {id_u}" for i, id_u in enumerate(cola))
            messagebox.showinfo(f"Cola — {libro.titulo}", f"En espera:\n{texto}")

    # ----------------------------------------------------------
    #  TAB 4 — Visualizar Árboles
    # ----------------------------------------------------------
    def _tab_arboles(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="  Ver Árboles  ")

        tk.Label(tab,
                 text="Vista rotada 90°: el hijo DERECHO aparece ARRIBA, el IZQUIERDO ABAJO.\n"
                      "La indentación indica la profundidad del nodo en el árbol.",
                 fg="#555", justify="left").pack(anchor="w", padx=12, pady=6)

        fbst = tk.LabelFrame(tab, text=" BST — Libros (clave: ISBN) ", padx=6, pady=6)
        fbst.pack(fill="both", expand=True, padx=10, pady=4)
        self.txt_bst = tk.Text(fbst, height=9, font=("Courier", 10))
        self.txt_bst.pack(fill="both", expand=True)

        favl = tk.LabelFrame(tab, text=" AVL — Usuarios (clave: ID)  [h=altura, fb=factor balance] ", padx=6, pady=6)
        favl.pack(fill="both", expand=True, padx=10, pady=4)
        self.txt_avl = tk.Text(favl, height=7, font=("Courier", 10))
        self.txt_avl.pack(fill="both", expand=True)

        tk.Button(tab, text="Actualizar árboles", command=self._refrescar_arboles).pack(pady=6)
        self._refrescar_arboles()

    def _refrescar_arboles(self):
        self.txt_bst.delete("1.0", tk.END)
        self.txt_bst.insert(tk.END, self.libros.mostrar_arbol())
        self.txt_avl.delete("1.0", tk.END)
        self.txt_avl.insert(tk.END, self.usuarios.mostrar_arbol())


# ============================================================
#  MAIN
# ============================================================
if __name__ == "__main__":
    ventana = tk.Tk()
    AppBiblioteca(ventana)
    ventana.mainloop()

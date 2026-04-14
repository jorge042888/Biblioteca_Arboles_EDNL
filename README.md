# Sistema de Biblioteca — Estructuras de Datos No Lineales

Proyecto de la materia **Estructuras de Datos** (5to Semestre).
Un solo archivo `biblioteca_AB.py`. Se ejecuta con `python biblioteca_AB.py`.

---

## ¿Qué estructuras se usan y para qué?

| Estructura | Para qué se usa | Ventaja |
|---|---|---|
| **Árbol BST** | Guardar los libros | Buscar un libro por ISBN en O(log n) en promedio |
| **Árbol AVL** | Guardar los usuarios | Busca en O(log n) siempre, incluso en el peor caso |
| **Cola (deque)** | Lista de espera de cada libro | El primero en entrar es el primero en recibir el libro |

---

## Explicación bloque por bloque

### 1. `NodoLibro` — el nodo del árbol BST

```python
class NodoLibro:
    def __init__(self, isbn, titulo, autor):
        self.isbn        = isbn
        self.titulo      = titulo
        self.autor       = autor
        self.disponible  = True       # ¿está en el estante?
        self.prestado_a  = None       # ID del usuario que lo tiene
        self.cola_espera = deque()    # usuarios esperando este libro
        self.izq  = None              # hijo izquierdo (ISBN menor)
        self.der  = None              # hijo derecho  (ISBN mayor)
```

Cada libro es un nodo en el árbol. Además de los datos del libro,
tiene dos punteros (`izq` y `der`) que apuntan a otros nodos.
La `cola_espera` es una cola FIFO por libro: si el libro está prestado,
los usuarios que lo pidan se agregan aquí y esperan su turno.

---

### 2. `BST_Libros` — el árbol BST completo

El BST ordena los nodos por ISBN. Si el ISBN a insertar es menor que
el nodo actual, va a la izquierda; si es mayor, va a la derecha.

#### Insertar
```
        "978-003"
       /         \
  "978-001"    "978-005"
      \         /
   "978-002" "978-004"
```
Cada vez que se agrega un libro se va comparando con los nodos existentes
hasta encontrar un lugar vacío (`None`). No hay rebalanceo.

#### Buscar por ISBN
Recorre el árbol comparando: si el ISBN buscado es menor, va a la izquierda;
si es mayor, va a la derecha. Termina cuando lo encuentra o llega a `None`.

#### Buscar por título
Como el árbol solo está ordenado por ISBN, para buscar por título hay que
recorrer **todos** los nodos (búsqueda completa). Devuelve todos los que
contengan el texto buscado en el título.

#### Eliminar
Hay tres casos posibles:
- **Sin hijos** → se borra directamente
- **Un hijo** → el padre apunta al único hijo del nodo borrado
- **Dos hijos** → se busca el "sucesor inorden" (el nodo con el ISBN
  inmediatamente mayor), se copian sus datos al nodo borrado, y se
  elimina el sucesor del subárbol derecho

#### Inorden
Recorre el árbol en orden: izquierda → nodo actual → derecha.
El resultado es la lista de libros **ordenada por ISBN**.
Esto se usa para mostrar la tabla en pantalla.

---

### 3. `NodoUsuario` — el nodo del árbol AVL

```python
class NodoUsuario:
    def __init__(self, id_usuario, nombre):
        self.id_usuario       = id_usuario
        self.nombre           = nombre
        self.libros_prestados = []    # lista de ISBNs que tiene prestados
        self.izq     = None
        self.der     = None
        self.altura  = 1              # altura del nodo (para el balance)
```

Igual que el nodo del BST, pero tiene un campo extra: `altura`.
La altura se actualiza cada vez que se inserta o elimina un nodo,
y sirve para calcular el factor de balance.

---

### 4. `AVL_Usuarios` — el árbol AVL completo

El AVL es un BST que se **autobalancea**. Después de cada inserción o
eliminación verifica si el árbol quedó desbalanceado y, si es así,
lo corrige con rotaciones.

#### Factor de balance
```
factor_balance = altura(hijo_izquierdo) - altura(hijo_derecho)
```
Si el resultado es **mayor a 1 o menor a -1**, el nodo está desbalanceado
y hay que aplicar una rotación.

#### Las 4 rotaciones posibles

**Caso II (Izquierda-Izquierda)** → rotación simple a la derecha
```
    C              B
   /              / \
  B      →       A   C
 /
A
```

**Caso DD (Derecha-Derecha)** → rotación simple a la izquierda
```
A                B
 \              / \
  B      →     A   C
   \
    C
```

**Caso ID (Izquierda-Derecha)** → rotar izquierda el hijo, luego rotar derecha el nodo
```
  C            C           B
 /            /           / \
A      →     B     →     A   C
 \          /
  B        A
```

**Caso DI (Derecha-Izquierda)** → rotar derecha el hijo, luego rotar izquierda el nodo
```
A          A               B
 \          \             / \
  C    →     B     →     A   C
 /            \
B              C
```

Gracias a esto, la altura del árbol siempre es O(log n), y las búsquedas
son rápidas incluso si los IDs se insertan en orden secuencial.

---

### 5. Cola de espera (`deque`) dentro de cada libro

Cuando un libro está prestado y otro usuario lo pide, se agrega su ID
a la `cola_espera` del libro:

```python
libro.cola_espera.append(id_usuario)   # entrar a la cola (al final)
```

Cuando el libro es devuelto, se toma automáticamente el primero:

```python
sig_id = libro.cola_espera.popleft()   # sacar al primero (FIFO)
```

Esto es una **cola FIFO**: el primero que esperó es el primero en recibirlo.

---

### 6. `AppBiblioteca` — la interfaz gráfica (Tkinter)

La ventana tiene 4 pestañas:

| Pestaña | Qué hace |
|---|---|
| **Libros** | Agregar, eliminar y buscar libros. Muestra la tabla inorden del BST. |
| **Usuarios** | Agregar, eliminar y buscar usuarios. Muestra altura y factor de balance del AVL. |
| **Préstamos** | Prestar, devolver, poner en cola, ver cola. |
| **Ver Árboles** | Muestra la estructura real de los dos árboles con la raíz arriba y las ramas hacia abajo. |

#### ¿Cómo se ve el árbol?

La pestaña **Ver Árboles** dibuja cada árbol de arriba hacia abajo.
La raíz aparece en la primera línea y los hijos debajo con líneas que muestran la conexión:

```
[978-003] 1984  (DISP)  ← raíz
├── IZQ: [978-001] Cien Años de Soledad  (DISP)
│   └── DER: [978-002] El Principito  (DISP)
└── DER: [978-005] Fahrenheit 451  (DISP)
    ├── IZQ: [978-004] Don Quijote  (DISP)
    └── DER: [978-006] El Alquimista  (DISP)
```

- `IZQ` = hijo izquierdo (ISBN menor que el padre)
- `DER` = hijo derecho (ISBN mayor que el padre)
- `(vacío)` = ese hijo no existe (rama sin nodo)

Para el AVL también se muestra `h` (altura del nodo) y `fb` (factor de balance):
```
[U003] Carlos López  (h=3, fb=0)  ← raíz
├── IZQ: [U001] Ana García  (h=2, fb=-1)
│   └── DER: [U002] Juan Pérez  (h=1, fb=0)
└── DER: [U004] Laura Díaz  (h=2, fb=-1)
    └── DER: [U005] María Martínez  (h=1, fb=0)
```

#### ¿Cómo se sabe a quién está prestado un libro?
En la tabla de libros, la columna **Estado** muestra el nombre y el ID
del usuario que tiene el libro prestado, por ejemplo:
```
Prestado a: Ana García (U001)
```
Esto funciona porque cuando se hace un préstamo se guarda el ID en
`libro.prestado_a`, y al mostrar la tabla se busca ese ID en el AVL
para obtener el nombre.

#### Helper `_campo`
Para no repetir el mismo código de `Label + Entry` en cada formulario,
se usa un método auxiliar:
```python
def _campo(self, frame, texto, fila, ancho=22):
    tk.Label(frame, text=texto).grid(row=fila, column=0, sticky="w", pady=2)
    e = tk.Entry(frame, width=ancho)
    e.grid(row=fila, column=1, padx=6, pady=2, sticky="w")
    return e
```
Se llama así: `self.e_isbn = self._campo(fm, "ISBN:", 0)` y hace lo mismo
que escribir 5 líneas cada vez.

---

## Flujo de un préstamo completo

```
1. Usuario ingresa ISBN + ID de usuario y presiona "Prestar"
2. Se busca el libro en el BST  → O(log n)
3. Se busca el usuario en el AVL → O(log n)
4. Si el libro está disponible:
      libro.disponible = False
      libro.prestado_a = id_usuario
      usuario.libros_prestados.append(isbn)
5. Si el libro NO está disponible:
      El usuario puede usar "Poner en cola"
      → su ID se agrega al deque del libro

Al devolver:
1. Se quita el ISBN de la lista del usuario anterior
2. Si hay alguien en la cola → se le presta automáticamente
3. Si no hay cola → libro.disponible = True
```

---

## Cómo ejecutar

```bash
python biblioteca_AB.py
```

No requiere instalar nada. Tkinter viene incluido con Python 3.

---

## Guia de estudio

Para practicar la implementacion paso a paso de un BST, un AVL y un arbol B en Python, revisa [TALLER_ARBOLES.md](/c:/Users/Jgutierrez/OneDrive/Backup/Iberoamericana/5to%20Semestre/Estructuras%20de%20Datos/NO%20Lineales/TALLER_ARBOLES.md).

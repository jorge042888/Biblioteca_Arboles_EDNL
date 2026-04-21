# Proyecto: Sistema de Biblioteca — Estructuras de Datos No Lineales

Proyecto de la materia **Estructuras de Datos** (5to semestre, Iberoamericana).

El programa simula una biblioteca usando árboles BST, AVL y colas de espera. Tiene interfaz gráfica con Tkinter.

---

## ¿Qué hace?

- Agregar y eliminar libros y usuarios
- Prestar y devolver libros
- Si un libro está prestado, el usuario puede ponerse en cola de espera
- Ver la estructura real de los árboles

---

## Estructuras que se usan

- **BST** → guarda los libros, ordenados por ISBN
- **AVL** → guarda los usuarios, se autobalancea para que las búsquedas sean siempre rápidas
- **Cola (deque)** → lista de espera por libro, funciona como FIFO

---

## Cómo ejecutar

```bash
python biblioteca_AB.py
```

No necesita instalar nada extra, Tkinter ya viene con Python 3.

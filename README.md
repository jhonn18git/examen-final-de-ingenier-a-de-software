# JWLR Petrol — Sistema de Venta Controlada de Carburantes

Sistema web para la gestión de inventario y venta controlada de carburantes
(Gasolina y Diésel) en la estación de servicio **JWLR Petrol** (Jhonn Wilder Llanos Rojas).

Controla el stock de tanques y aplica un algoritmo de **cupos dinámicos** por cliente
basado en el promedio semanal de compras de los últimos 28 días, evitando
sobreabastecimiento y especulación.

> Proyecto académico — Examen Final · Ingeniería de Software · USFX 2025

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12 + Flask 3.0 |
| Base de datos | SQLite 3 + SQLAlchemy |
| Frontend | HTML5 + Jinja2 + Bootstrap 5.3 |
| Servidor (prod) | Gunicorn |

---

## Instalación local

```bash
# 1. Clonar el repositorio
git clone https://github.com/jhonn18git/examen-final-de-ingenier-a-de-software
cd examen-final-de-ingenier-a-de-software

# 2. Crear entorno virtual e instalar dependencias
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

# 3. Ejecutar la aplicación
python app.py
```

La base de datos `carburantes.db` se crea automáticamente con datos de prueba
al primer arranque.

Abrir en el navegador: **http://localhost:5000**

---

## Credenciales de prueba

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `admin123` | Administrador |
| `playero1` | `playero123` | Operador |

### Clientes seed y sus cupos calculados

| Cliente | Placa | Tipo | Ps (L/sem) | Límite (L) |
|---|---|---|---|---|
| Juan Perez Flores | 1234-ABC | Particular | 9.75 | 10.73 |
| Transportes del Sur S.R.L. | 9876-TRA | Transp. Público | 39.75 | 43.73 |
| Empresa Constructora Andina | 5678-EMP | Empresa | 25.00 | 27.50 |

---

## Módulos del sistema

- **Dashboard** — estado de tanques con barras de progreso + alertas de stock mínimo
- **Nueva Venta** — búsqueda por placa/cédula → cálculo de cupo → validación → comprobante
- **Ingresos** — registro de abastecimiento de tanques desde cisternas
- **Clientes** — padrón con estado Activo/Suspendido y conteo de ventas

### Regla de negocio: cupo dinámico

```
Ps  = Σ litros últimos 28 días / 4 semanas
Límite = Ps × (1 + factor_holgura)   →  ej. Ps × 1.10  (10% de holgura)
```

- Si el cliente es nuevo (sin historial): se usa el **cupo base** configurado (20 L por defecto).
- Si la cantidad solicitada > límite: el botón "Procesar" se desactiva; aparece
  "Ajustar al límite" para confirmar la venta al máximo permitido.

---

## Estructura del proyecto

```
/
├── app.py              # Factory Flask + instancia para gunicorn
├── config.py           # Configuración (SECRET_KEY, SQLite URI)
├── models.py           # Modelos SQLAlchemy (Empresa, Tanque, Cliente, Ingreso, Venta, Operador)
├── seed.py             # Datos de prueba (auto_seed + seed standalone)
├── requirements.txt
├── Procfile            # Para Render: gunicorn --bind 0.0.0.0:$PORT app:app
├── routes/
│   ├── auth.py         # Login / logout
│   ├── dashboard.py    # Página principal
│   ├── ventas.py       # Nueva venta (búsqueda, cupo, procesar, comprobante)
│   ├── ingresos.py     # Abastecimiento de tanques
│   ├── clientes.py     # Padrón de clientes
│   └── utils.py        # login_required + calcular_cupo()
├── templates/
│   ├── base.html
│   ├── auth/login.html
│   ├── dashboard/index.html
│   ├── ventas/         (buscar, nuevo_cliente, procesar, comprobante, lista)
│   ├── ingresos/       (nuevo, lista)
│   └── clientes/lista.html
└── static/css/style.css
```

---

## Despliegue en Render

1. Crear un nuevo **Web Service** en [render.com](https://render.com)
2. Conectar este repositorio de GitHub
3. Configurar:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT app:app`
   - **Environment:** Python 3
4. La base de datos SQLite se inicializa automáticamente con datos de prueba
   en cada arranque (el filesystem de Render Free es efímero).

> **Nota:** Para persistencia real de datos en producción se recomienda
> migrar a PostgreSQL (usando Flask-Migrate + psycopg2).

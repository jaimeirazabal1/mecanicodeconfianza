# MecaDeConfianza

Plataforma web para conectar clientes con mecánicos automotrices de confianza. Los clientes pueden buscar mecánicos por especialidad, ubicación y calificación, ver su perfil con reseñas y tutoriales, chatear con ellos y contratar servicios directamente desde la plataforma.

## Tecnologías

- **Backend:** Python 3.13 + FastAPI (async)
- **Base de datos:** SQLite vía aiosqlite + SQLAlchemy 2.0 (async)
- **Frontend:** Jinja2 templates + CSS vanilla + JavaScript vanilla
- **Autenticación:** JWT (cookies) + SHA-256 con salt

## Funcionalidades

- **Búsqueda de mecánicos:** por nombre, ubicación, especialidad; ordenado por calificación; paginado
- **Perfiles de mecánico:** información del taller, especialidades, años de experiencia, reseñas, tutoriales, fotos de trabajos
- **Sistema de reseñas:** clientes pueden calificar (1-5) y comentar
- **Tutoriales:** los mecánicos publican tutoriales con video embebido de YouTube
- **Mensajería:** conversaciones en tiempo real entre cliente y mecánico
- **Contrataciones:** los clientes contratan servicios específicos con seguimiento de estado (pendiente → aceptado → en progreso → completado)
- **Servicios:** los mecánicos gestionan su catálogo de servicios con precios y duración
- **Autenticación:** registro e inicio de sesión con roles (cliente / mecánico)
- **Responsive:** diseño adaptable a móviles

## Instalación

```bash
git clone https://github.com/jaimeirazabal1/mecanicodeconfianza.git
cd mecanicodeconfianza
pip install -r requirements.txt
python seed.py
python run.py
```

Abrir `http://localhost:8000` en el navegador.

## Usuarios de prueba

Todos los usuarios creados por `seed.py` usan la contraseña `123456`.

**Mecánicos:**
- carlos@email.com
- maria@email.com
- juan@email.com
- roberto@email.com
- ana@email.com
- pedro@email.com
- luis@email.com
- gabriela@email.com
- fernando@email.com
- diego@email.com

**Clientes:** puedes registrarte libremente o usar cualquiera de los clientes creados automáticamente con las reseñas.

## Estructura del proyecto

```
mecanicodeconfianza/
├── app/
│   ├── main.py              # Punto de entrada FastAPI
│   ├── auth.py              # JWT + hash de contraseñas
│   ├── database.py          # Configuración SQLAlchemy async
│   ├── models/              # Modelos SQLAlchemy
│   ├── routers/             # Endpoints por módulo
│   ├── schemas/             # Schemas Pydantic
│   └── services/            # Lógica de negocio
├── static/
│   ├── css/style.css
│   └── js/app.js
├── templates/               # Jinja2 templates
├── seed.py                  # Población de la base de datos
├── run.py                   # Script para arrancar el servidor
└── requirements.txt
```

## API endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/auth/register` | Registrar usuario |
| POST | `/api/auth/login` | Iniciar sesión |
| GET | `/api/mechanics` | Buscar mecánicos |
| GET | `/api/mechanics/{id}` | Detalle de mecánico |
| POST | `/api/reviews` | Crear reseña |
| POST | `/api/tutorials` | Crear tutorial |
| GET | `/api/messages/{conv_id}` | Mensajes de conversación |
| POST | `/api/bookings` | Crear contratación |
| PUT | `/api/bookings/{id}/status` | Actualizar estado de contratación |
| GET | `/api/mechanics/{id}/services` | Servicios de un mecánico |
| POST | `/api/services` | Crear servicio (mecánico) |

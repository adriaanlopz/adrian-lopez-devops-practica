# Tienda online · DevOps

**Autor:** Adrián López Río

API REST de una tienda online hecha en Python con FastAPI en la Práctica 2 de Arquitectura del Software. Gestiona usuarios (clientes y administradores), productos (genéricos, electrónicos y de ropa) y pedidos con control de stock. Incluye un cliente de consola que consume la API con `requests` y un panel web en HTML y JavaScript.

En este repositorio se gestiona el proyecto con Git y GitHub (Práctica 3.1) y se conteneriza la aplicación con Docker (Práctica 3.2).

[![CI Docker](https://github.com/adriaanlopz/adrian-lopez-devops-practica/actions/workflows/docker.yml/badge.svg)](https://github.com/adriaanlopz/adrian-lopez-devops-practica/actions/workflows/docker.yml)

## Estructura

```text
adrian-lopez-devops-practica/
├── .github/workflows/docker.yml   CI: tests, build, run, test y push de la imagen
├── src/
│   ├── Tienda_online/             API FastAPI (la que va dentro de la imagen)
│   │   ├── main.py                Endpoints
│   │   ├── models/                Clases de dominio (Producto, Usuario, Pedido)
│   │   ├── schemas/               Esquemas Pydantic
│   │   └── Services/              TiendaService (lógica de negocio)
│   ├── consola/                   Cliente de consola con requests
│   └── web/tienda.html            Panel web
├── frontend/
│   ├── Dockerfile                 Imagen nginx con el panel web
│   └── nginx.conf                 Sirve el panel y reenvía /api/ a la API
├── tests/test_api.py              Tests de la API con pytest
├── scripts/prueba_contenedor.py   Prueba de la API ya arrancada (local o en Docker)
├── Dockerfile                     Imagen de la API
├── docker-compose.yml             Levanta la API y el frontend juntos
├── .dockerignore
├── requirements.txt               Dependencias de la API con versiones fijadas
└── requirements-dev.txt           Dependencias para los tests
```

## Ejecutar sin Docker

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows (en Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
cd src/Tienda_online
uvicorn main:app --reload
```

La documentación interactiva queda en <http://localhost:8000/docs>.

## Docker

La imagen parte de `python:3.12-slim`, instala `requirements.txt`, copia el código de `src/Tienda_online`, se ejecuta con un usuario sin privilegios (`tienda`) y arranca Uvicorn en el puerto 8000. Tiene un `HEALTHCHECK` que consulta `/health`.

### 1. Construir la imagen

```bash
docker build -t tienda-api:1.0.0 .
```

### 2. Ejecutar el contenedor

```bash
docker run -d --name tienda -p 8000:8000 tienda-api:1.0.0
```

Otros ejemplos:

```bash
# En primer plano, borrando el contenedor al pararlo (Ctrl+C)
docker run --rm -p 8000:8000 tienda-api:1.0.0

# En otro puerto y limitando CORS a un origen
docker run -d --name tienda -p 9000:9000 -e PORT=9000 -e CORS_ORIGINS=http://localhost:8080 tienda-api:1.0.0

# Ver logs, estado y parar
docker logs -f tienda
docker ps --filter name=tienda
docker stop tienda && docker rm tienda
```

### 3. Variables de entorno

| Variable | Dónde | Valor por defecto | Para qué |
|---|---|---|---|
| `PORT` | API (contenedor) | `8000` | Puerto en el que escucha Uvicorn dentro del contenedor |
| `CORS_ORIGINS` | API (contenedor) | `*` | Orígenes permitidos por CORS, separados por comas |
| `API_URL` | Cliente de consola | `http://127.0.0.1:8000` | Dirección de la API a la que llama el cliente |

La aplicación no usa secretos, así que no hay ninguna clave en el repositorio.

### 4. Probar el contenedor (salida esperada)

Con el contenedor arrancado:

| Prueba | Resultado esperado |
|---|---|
| `curl http://localhost:8000/health` | `{"status":"ok"}` |
| Abrir <http://localhost:8000/docs> | Swagger con los endpoints de usuarios, productos y pedidos |
| `docker ps --filter name=tienda` | Estado `Up ... (healthy)` |
| `docker exec tienda whoami` | `tienda` (no `root`) |
| `python scripts/prueba_contenedor.py` | Las 12 comprobaciones en `[OK]` |

Salida de `python scripts/prueba_contenedor.py http://localhost:8000`:

```text
Probando la API en http://localhost:8000

[OK] GET /health: (200, {'status': 'ok'})
[OK] POST /usuarios (cliente): 201
[OK] GET /usuarios/{id}: 200
[OK] POST /productos (electrónico): 201
[OK] GET /productos incluye el nuevo: True
[OK] POST /pedidos: 201
[OK] Total del pedido (2 x 229.0): 458.0
[OK] Stock después del pedido (5 - 2): 3
[OK] POST /pedidos sin stock suficiente: 400
[OK] GET /usuarios/{id}/pedidos: (200, 1)
[OK] DELETE /productos/{id}: 200
[OK] GET /productos/{id} tras borrarlo: 404

Todas las comprobaciones son correctas
```

El script solo usa la biblioteca estándar de Python. También se pueden usar los clientes de la Práctica 2 contra el contenedor:

```bash
pip install -r src/consola/requirements.txt
python src/consola/tienda_consola.py          # menú; la opción 8 carga datos de ejemplo
```

Y el panel web se abre con doble clic en `src/web/tienda.html` (apunta a `http://127.0.0.1:8000`).

### 5. Descargar la imagen publicada (pull)

Cada push a `main` publica la imagen en GitHub Container Registry con dos etiquetas: `latest` y `sha-<commit>`.

```bash
docker pull ghcr.io/adriaanlopz/adrian-lopez-devops-practica:latest
docker run -d --name tienda -p 8000:8000 ghcr.io/adriaanlopz/adrian-lopez-devops-practica:latest
```

### 6. Publicar la imagen a mano (push)

Lo hace la CI, pero también se puede hacer desde el equipo con un token de GitHub con permiso `write:packages`:

```bash
docker tag tienda-api:1.0.0 ghcr.io/adriaanlopz/adrian-lopez-devops-practica:1.0.0
docker login ghcr.io -u adriaanlopz
docker push ghcr.io/adriaanlopz/adrian-lopez-devops-practica:1.0.0
```

## Docker Compose: API y frontend

`docker-compose.yml` levanta dos contenedores que se comunican por la red interna que crea Compose:

```bash
docker compose up -d --build
docker compose ps
docker compose down
```

| Servicio | Imagen | Puerto | Qué es |
|---|---|---|---|
| `api` | `tienda-api:1.0.0` | 8000 | La API FastAPI (el `Dockerfile` de la raíz) |
| `frontend` | `tienda-frontend:1.0.0` | 8080 | nginx con el panel web de la Práctica 2 |

| Prueba | Resultado esperado |
|---|---|
| Abrir <http://localhost:8080> | Panel web con el campo API en `/api` y el estado «Conectado» |
| `python scripts/prueba_contenedor.py http://localhost:8080/api` | Las 12 comprobaciones en `[OK]`, pasando por nginx |
| Abrir <http://localhost:8000/docs> | Swagger de la API |

Cómo se comunican: el navegador pide `http://localhost:8080/api/...` a nginx, y nginx lo reenvía a `http://api:8000/...`, donde `api` es el nombre del servicio en la red de Compose. nginx cambia al servir la página la dirección por defecto del panel (`http://127.0.0.1:8000`) por `/api`, así que `tienda.html` no se toca. El frontend espera a que el healthcheck de la API esté en `healthy` antes de arrancar.

## Tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

Son 14 tests con `TestClient` de FastAPI: altas, consultas, borrados, errores 400, 404 y 422, descuento de stock y historial de pedidos. Cada test usa un `TiendaService` nuevo, sustituyendo la dependencia `get_tienda`.

## Integración continua

El workflow [`.github/workflows/docker.yml`](.github/workflows/docker.yml) se ejecuta en cada Pull Request y en cada push a `main`:

| Paso | Qué hace |
|---|---|
| Tests | Instala `requirements-dev.txt` y ejecuta `pytest` |
| Build | `docker build` de la imagen |
| Run | `docker run` del contenedor en el puerto 8000 |
| Test | `scripts/prueba_contenedor.py`, usuario no root y healthcheck en `healthy` |
| Push | Solo en `main`: `docker push` a `ghcr.io` con las etiquetas `latest` y `sha-<commit>` |

## Flujo de trabajo con Git

| Rama | Uso |
|---|---|
| `main` | Rama principal, siempre estable. Solo recibe cambios por Pull Request |
| `feature/docker` | Contenerización de la API (Práctica 3.2) |
| `feature/frontend` | Contenedor del panel web y `docker-compose.yml` (extra de la Práctica 3.2) |

Los commits siguen el formato `tipo(ámbito): descripción` (`feat`, `fix`, `docs`, `test`, `build`, `ci`, `chore`).

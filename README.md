# RENIEC API (FastAPI + PostgreSQL + Keycloak)

API de solo lectura para consultar `public.reniec` y `public.reniec2`.

## 1. Configuración

```powershell
copy .env.example .env
```

Edita `.env` con PostgreSQL y Keycloak.

## 2. Ejecutar local

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger:

`http://localhost:8000/docs`

Health:

`GET /health`

## 3. Ejecutar con Docker

```bash
docker compose up -d --build
```

## 4. Endpoints

Todos los endpoints `/api/v1/*` requieren:

```http
Authorization: Bearer <TOKEN_KEYCLOAK>
```

### Documento exacto

```http
GET /api/v1/reniec/documento/12345678
```

Consulta ambas tablas y devuelve todas las columnas de cada coincidencia.

### Nombre / apellidos con ILIKE

```http
GET /api/v1/reniec/nombres?nombre=JUAN&ape_paterno=PEREZ&ape_materno=LOPEZ
```

Parámetros opcionales:

- `table=all|reniec|reniec2`
- `limit=1..20` (máximo 20)

### Departamento

```http
GET /api/v1/reniec/departamento/PUNO?limit=20
```

En `reniec` usa `nom_departamento`; en `reniec2` busca dentro de `des_ubigeo_direccion`.

### Ubigeo

```http
GET /api/v1/reniec/ubigeo/210101?limit=20
```

### Estado civil

```http
GET /api/v1/reniec/estado-civil/SOLTERO?limit=20
```

## 5. Keycloak

La API NO crea usuarios. Keycloak administra la autenticación.

Configuración mínima recomendada:

- Realm: el que definas en `.env`
- Client: `reniec-api`
- Audience del token: igual a `KEYCLOAK_AUDIENCE`
- Un único usuario permitido, opcionalmente fijado en `KEYCLOAK_ALLOWED_USERNAME`

La API valida:

- firma JWT contra JWKS de Keycloak
- `iss`
- `aud`
- expiración
- `preferred_username` si `KEYCLOAK_ALLOWED_USERNAME` está definido

## 6. Índices

Con 30M y 37M de filas, no uses estas búsquedas sin índices después de terminar la carga.

Ejecuta:

```bash
psql -h 192.168.0.107 -p 6543 -U admin -d reniec -f sql/indexes.sql
```

Los índices trigram (`pg_trgm`) aceleran `ILIKE '%texto%'`.

## 7. Recomendaciones de seguridad

- No publiques PostgreSQL (`6543`) a Internet.
- Expón solamente la API por HTTPS.
- Mantén la API detrás de Tailscale o un reverse proxy si será privada.
- Añade rate limiting y auditoría antes de exponer consultas de datos personales.
- No escribas credenciales directamente en el código; usa `.env` o secretos de Docker.

from typing import Any, Literal
from psycopg.rows import dict_row

from app.db.pool import pool

TableName = Literal["reniec", "reniec2", "all"]

RENIEC_COLUMNS = """
    id_ext_reniec_his,
    cod_tipo_documento,
    nro_documento,
    nombre,
    ape_paterno,
    ape_materno,
    des_situacion_laboral,
    des_nse,
    fec_nacimiento,
    des_estado_civil,
    des_genero,
    nro_cantidad_hijos,
    des_gra_institucional,
    des_direccion,
    nom_departamento,
    nom_provincia,
    nom_distrito,
    des_ubigeo,
    des_profesion,
    fec_fallecimiento
"""

RENIEC2_COLUMNS = """
    id_ext_reniec_his,
    nro_documento,
    nombre,
    ape_paterno,
    ape_materno,
    fec_nacimiento,
    fec_inscripcion,
    fec_emision,
    fec_caducidad,
    des_ubigeo_nacimiento,
    des_ubigeo_direccion,
    des_direccion,
    des_sexo,
    des_estado_civil,
    des_dig_ruc,
    nom_madre,
    nom_padre
"""


def _query(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params)
            return list(cur.fetchall())


def search_documento(documento: str) -> list[dict[str, Any]]:
    sql1 = f"SELECT {RENIEC_COLUMNS} FROM public.reniec WHERE nro_documento = %s"
    sql2 = f"SELECT {RENIEC2_COLUMNS} FROM public.reniec2 WHERE nro_documento = %s"

    results: list[dict[str, Any]] = []
    for row in _query(sql1, (documento,)):
        results.append({"source": "reniec", "data": row})
    for row in _query(sql2, (documento,)):
        results.append({"source": "reniec2", "data": row})
    return results


def search_nombres(
    nombre: str | None,
    ape_paterno: str | None,
    ape_materno: str | None,
    table: TableName,
    limit: int,
) -> list[dict[str, Any]]:
    conditions: list[str] = []
    params: list[Any] = []

    if nombre:
        conditions.append("nombre ILIKE %s")
        params.append(f"%{nombre}%")
    if ape_paterno:
        conditions.append("ape_paterno ILIKE %s")
        params.append(f"%{ape_paterno}%")
    if ape_materno:
        conditions.append("ape_materno ILIKE %s")
        params.append(f"%{ape_materno}%")

    if not conditions:
        return []

    where = " AND ".join(conditions)
    results: list[dict[str, Any]] = []

    if table in ("reniec", "all"):
        sql = f"""
            SELECT {RENIEC_COLUMNS}
            FROM public.reniec
            WHERE {where}
            ORDER BY ape_paterno, ape_materno, nombre
            LIMIT %s
        """
        rows = _query(sql, tuple(params + [limit]))
        results.extend({"source": "reniec", "data": row} for row in rows)

    remaining = max(0, limit - len(results))
    if table in ("reniec2", "all") and remaining > 0:
        sql = f"""
            SELECT {RENIEC2_COLUMNS}
            FROM public.reniec2
            WHERE {where}
            ORDER BY ape_paterno, ape_materno, nombre
            LIMIT %s
        """
        rows = _query(sql, tuple(params + [remaining]))
        results.extend({"source": "reniec2", "data": row} for row in rows)

    return results[:limit]


def search_departamento(departamento: str, table: TableName, limit: int) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    if table in ("reniec", "all"):
        sql = f"""
            SELECT {RENIEC_COLUMNS}
            FROM public.reniec
            WHERE nom_departamento ILIKE %s
            ORDER BY ape_paterno, ape_materno, nombre
            LIMIT %s
        """
        rows = _query(sql, (f"%{departamento}%", limit))
        results.extend({"source": "reniec", "data": row} for row in rows)

    remaining = max(0, limit - len(results))
    if table in ("reniec2", "all") and remaining > 0:
        sql = f"""
            SELECT {RENIEC2_COLUMNS}
            FROM public.reniec2
            WHERE des_ubigeo_direccion ILIKE %s
            ORDER BY ape_paterno, ape_materno, nombre
            LIMIT %s
        """
        rows = _query(sql, (f"%{departamento}%", remaining))
        results.extend({"source": "reniec2", "data": row} for row in rows)

    return results[:limit]


def search_ubigeo(ubigeo: str, table: TableName, limit: int) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    if table in ("reniec", "all"):
        sql = f"""
            SELECT {RENIEC_COLUMNS}
            FROM public.reniec
            WHERE des_ubigeo ILIKE %s
            LIMIT %s
        """
        rows = _query(sql, (f"%{ubigeo}%", limit))
        results.extend({"source": "reniec", "data": row} for row in rows)

    remaining = max(0, limit - len(results))
    if table in ("reniec2", "all") and remaining > 0:
        sql = f"""
            SELECT {RENIEC2_COLUMNS}
            FROM public.reniec2
            WHERE des_ubigeo_direccion ILIKE %s
               OR des_ubigeo_nacimiento ILIKE %s
            LIMIT %s
        """
        term = f"%{ubigeo}%"
        rows = _query(sql, (term, term, remaining))
        results.extend({"source": "reniec2", "data": row} for row in rows)

    return results[:limit]


def search_estado_civil(estado: str, table: TableName, limit: int) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    if table in ("reniec", "all"):
        sql = f"SELECT {RENIEC_COLUMNS} FROM public.reniec WHERE des_estado_civil ILIKE %s LIMIT %s"
        rows = _query(sql, (f"%{estado}%", limit))
        results.extend({"source": "reniec", "data": row} for row in rows)

    remaining = max(0, limit - len(results))
    if table in ("reniec2", "all") and remaining > 0:
        sql = f"SELECT {RENIEC2_COLUMNS} FROM public.reniec2 WHERE des_estado_civil ILIKE %s LIMIT %s"
        rows = _query(sql, (f"%{estado}%", remaining))
        results.extend({"source": "reniec2", "data": row} for row in rows)

    return results[:limit]

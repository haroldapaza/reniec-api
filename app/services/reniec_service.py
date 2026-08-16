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


def _wrap(source: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"source": source, "data": row} for row in rows]


def search_documento(documento: str) -> list[dict[str, Any]]:
    """Busca primero en reniec2 y solo si no existe, busca en reniec."""
    sql2 = f"SELECT {RENIEC2_COLUMNS} FROM public.reniec2 WHERE nro_documento = %s"
    rows = _query(sql2, (documento,))
    if rows:
        return _wrap("reniec2", rows)

    sql1 = f"SELECT {RENIEC_COLUMNS} FROM public.reniec WHERE nro_documento = %s"
    return _wrap("reniec", _query(sql1, (documento,)))


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

    if table in ("reniec2", "all"):
        sql = f"""
            SELECT {RENIEC2_COLUMNS}
            FROM public.reniec2
            WHERE {where}
            ORDER BY ape_paterno, ape_materno, nombre
            LIMIT %s
        """
        rows = _query(sql, tuple(params + [limit]))
        if rows or table == "reniec2":
            return _wrap("reniec2", rows)

    sql = f"""
        SELECT {RENIEC_COLUMNS}
        FROM public.reniec
        WHERE {where}
        ORDER BY ape_paterno, ape_materno, nombre
        LIMIT %s
    """
    return _wrap("reniec", _query(sql, tuple(params + [limit])))


def search_departamento(departamento: str, table: TableName, limit: int) -> list[dict[str, Any]]:
    term = f"%{departamento}%"

    if table in ("reniec2", "all"):
        sql = f"""
            SELECT {RENIEC2_COLUMNS}
            FROM public.reniec2
            WHERE des_ubigeo_direccion ILIKE %s
            ORDER BY ape_paterno, ape_materno, nombre
            LIMIT %s
        """
        rows = _query(sql, (term, limit))
        if rows or table == "reniec2":
            return _wrap("reniec2", rows)

    sql = f"""
        SELECT {RENIEC_COLUMNS}
        FROM public.reniec
        WHERE nom_departamento ILIKE %s
        ORDER BY ape_paterno, ape_materno, nombre
        LIMIT %s
    """
    return _wrap("reniec", _query(sql, (term, limit)))


def search_ubigeo(ubigeo: str, table: TableName, limit: int) -> list[dict[str, Any]]:
    term = f"%{ubigeo}%"

    if table in ("reniec2", "all"):
        sql = f"""
            SELECT {RENIEC2_COLUMNS}
            FROM public.reniec2
            WHERE des_ubigeo_direccion ILIKE %s
               OR des_ubigeo_nacimiento ILIKE %s
            LIMIT %s
        """
        rows = _query(sql, (term, term, limit))
        if rows or table == "reniec2":
            return _wrap("reniec2", rows)

    sql = f"""
        SELECT {RENIEC_COLUMNS}
        FROM public.reniec
        WHERE des_ubigeo ILIKE %s
        LIMIT %s
    """
    return _wrap("reniec", _query(sql, (term, limit)))


def search_estado_civil(estado: str, table: TableName, limit: int) -> list[dict[str, Any]]:
    term = f"%{estado}%"

    if table in ("reniec2", "all"):
        sql = f"SELECT {RENIEC2_COLUMNS} FROM public.reniec2 WHERE des_estado_civil ILIKE %s LIMIT %s"
        rows = _query(sql, (term, limit))
        if rows or table == "reniec2":
            return _wrap("reniec2", rows)

    sql = f"SELECT {RENIEC_COLUMNS} FROM public.reniec WHERE des_estado_civil ILIKE %s LIMIT %s"
    return _wrap("reniec", _query(sql, (term, limit)))


def search_avanzada(
    nombre: str | None,
    ape_paterno: str | None,
    ape_materno: str | None,
    departamento: str | None,
    provincia: str | None,
    distrito: str | None,
    estado_civil: str | None,
    nombre_padre: str | None,
    nombre_madre: str | None,
    sexo: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    """
    Filtro avanzado con prioridad RENIEC2 -> RENIEC.

    En reniec2 departamento/provincia/distrito se buscan dentro de
    des_ubigeo_direccion porque esa tabla no tiene columnas separadas.
    nom_padre y nom_madre solo existen en reniec2; si se envía alguno de
    esos filtros y reniec2 no encuentra coincidencias, no hay fallback
    válido hacia reniec.
    """
    filters = {
        "nombre": nombre,
        "ape_paterno": ape_paterno,
        "ape_materno": ape_materno,
        "departamento": departamento,
        "provincia": provincia,
        "distrito": distrito,
        "estado_civil": estado_civil,
        "nombre_padre": nombre_padre,
        "nombre_madre": nombre_madre,
        "sexo": sexo,
    }
    if not any(value for value in filters.values()):
        return []

    # 1) RENIEC2 primero
    conditions2: list[str] = []
    params2: list[Any] = []

    def add2(column: str, value: str | None) -> None:
        if value:
            conditions2.append(f"{column} ILIKE %s")
            params2.append(f"%{value}%")

    add2("nombre", nombre)
    add2("ape_paterno", ape_paterno)
    add2("ape_materno", ape_materno)
    # reniec2 guarda el ubigeo/dirección como texto compuesto
    add2("des_ubigeo_direccion", departamento)
    add2("des_ubigeo_direccion", provincia)
    add2("des_ubigeo_direccion", distrito)
    add2("des_estado_civil", estado_civil)
    add2("nom_padre", nombre_padre)
    add2("nom_madre", nombre_madre)
    add2("des_sexo", sexo)

    sql2 = f"""
        SELECT {RENIEC2_COLUMNS}
        FROM public.reniec2
        WHERE {' AND '.join(conditions2)}
        ORDER BY ape_paterno, ape_materno, nombre
        LIMIT %s
    """
    rows2 = _query(sql2, tuple(params2 + [limit]))
    if rows2:
        return _wrap("reniec2", rows2)

    # nom_padre / nom_madre no existen en public.reniec.
    if nombre_padre or nombre_madre:
        return []

    # 2) Solo si RENIEC2 no devolvió nada, buscar en RENIEC
    conditions1: list[str] = []
    params1: list[Any] = []

    def add1(column: str, value: str | None) -> None:
        if value:
            conditions1.append(f"{column} ILIKE %s")
            params1.append(f"%{value}%")

    add1("nombre", nombre)
    add1("ape_paterno", ape_paterno)
    add1("ape_materno", ape_materno)
    add1("nom_departamento", departamento)
    add1("nom_provincia", provincia)
    add1("nom_distrito", distrito)
    add1("des_estado_civil", estado_civil)
    add1("des_genero", sexo)

    if not conditions1:
        return []

    sql1 = f"""
        SELECT {RENIEC_COLUMNS}
        FROM public.reniec
        WHERE {' AND '.join(conditions1)}
        ORDER BY ape_paterno, ape_materno, nombre
        LIMIT %s
    """
    return _wrap("reniec", _query(sql1, tuple(params1 + [limit])))

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.security import validate_token
from app.services.reniec_service import (
    search_avanzada,
    search_departamento,
    search_documento,
    search_estado_civil,
    search_nombres,
    search_ubigeo,
)

router = APIRouter(prefix="/api/v1", dependencies=[Depends(validate_token)])

TableParam = Literal["reniec", "reniec2", "all"]


def capped_limit(limit: int) -> int:
    return min(max(limit, 1), 100)


def clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


@router.get("/reniec/documento/{nro_documento}", tags=["RENIEC"])
def obtener_por_documento(nro_documento: str):
    nro_documento = nro_documento.strip()
    if not nro_documento:
        raise HTTPException(status_code=400, detail="Documento obligatorio")
    if not nro_documento.isdigit() or len(nro_documento) != 8:
        raise HTTPException(status_code=400, detail="El DNI debe contener exactamente 8 dígitos")

    results = search_documento(nro_documento)
    return {"total": len(results), "results": results}


@router.get("/reniec/nombres", tags=["RENIEC"])
def obtener_por_nombres(
    nombre: str | None = Query(default=None),
    ape_paterno: str | None = Query(default=None),
    ape_materno: str | None = Query(default=None),
    table: TableParam = "all",
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    nombre = clean(nombre)
    ape_paterno = clean(ape_paterno)
    ape_materno = clean(ape_materno)

    if not any([nombre, ape_paterno, ape_materno]):
        raise HTTPException(
            status_code=400,
            detail="Debes enviar al menos nombre, ape_paterno o ape_materno",
        )

    results = search_nombres(nombre, ape_paterno, ape_materno, table, capped_limit(limit))
    return {"total": len(results), "limit": capped_limit(limit), "results": results}


@router.get("/reniec/departamento/{departamento}", tags=["RENIEC"])
def obtener_por_departamento(
    departamento: str,
    table: TableParam = "all",
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    results = search_departamento(departamento.strip(), table, capped_limit(limit))
    return {"total": len(results), "limit": capped_limit(limit), "results": results}


@router.get("/reniec/ubigeo/{ubigeo}", tags=["RENIEC"])
def obtener_por_ubigeo(
    ubigeo: str,
    table: TableParam = "all",
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    results = search_ubigeo(ubigeo.strip(), table, capped_limit(limit))
    return {"total": len(results), "limit": capped_limit(limit), "results": results}


@router.get("/reniec/estado-civil/{estado}", tags=["RENIEC"])
def obtener_por_estado_civil(
    estado: str,
    table: TableParam = "all",
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    results = search_estado_civil(estado.strip(), table, capped_limit(limit))
    return {"total": len(results), "limit": capped_limit(limit), "results": results}


@router.get("/reniec/filtro-avanzado", tags=["RENIEC"])
def obtener_por_filtro_avanzado(
    nombre: str | None = Query(default=None),
    ape_paterno: str | None = Query(default=None),
    ape_materno: str | None = Query(default=None),
    departamento: str | None = Query(default=None),
    provincia: str | None = Query(default=None),
    distrito: str | None = Query(default=None),
    estado_civil: str | None = Query(default=None),
    nombre_padre: str | None = Query(default=None),
    nombre_madre: str | None = Query(default=None),
    sexo: str | None = Query(default=None, description="Sexo/género, por ejemplo M, F, masculino o femenino según tus datos"),
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    valores = {
        "nombre": clean(nombre),
        "ape_paterno": clean(ape_paterno),
        "ape_materno": clean(ape_materno),
        "departamento": clean(departamento),
        "provincia": clean(provincia),
        "distrito": clean(distrito),
        "estado_civil": clean(estado_civil),
        "nombre_padre": clean(nombre_padre),
        "nombre_madre": clean(nombre_madre),
        "sexo": clean(sexo),
    }

    if not any(valores.values()):
        raise HTTPException(
            status_code=400,
            detail="Debes enviar al menos un filtro con valor",
        )

    results = search_avanzada(**valores, limit=capped_limit(limit))
    return {
        "total": len(results),
        "limit": capped_limit(limit),
        "priority": ["reniec2", "reniec"],
        "results": results,
    }

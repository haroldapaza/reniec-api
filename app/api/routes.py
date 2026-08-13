from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.security import validate_token
from app.services.reniec_service import (
    search_departamento,
    search_documento,
    search_estado_civil,
    search_nombres,
    search_ubigeo,
)

router = APIRouter(prefix="/api/v1", dependencies=[Depends(validate_token)])

TableParam = Literal["reniec", "reniec2", "all"]


def capped_limit(limit: int) -> int:
    return min(max(limit, 1), 20)


@router.get("/reniec/documento/{nro_documento}", tags=["RENIEC"])
def obtener_por_documento(nro_documento: str):
    nro_documento = nro_documento.strip()
    if not nro_documento:
        raise HTTPException(status_code=400, detail="Documento obligatorio")

    results = search_documento(nro_documento)
    return {"total": len(results), "results": results}


@router.get("/reniec/nombres", tags=["RENIEC"])
def obtener_por_nombres(
    nombre: str | None = Query(default=None, min_length=2),
    ape_paterno: str | None = Query(default=None, min_length=2),
    ape_materno: str | None = Query(default=None, min_length=2),
    table: TableParam = "all",
    limit: Annotated[int, Query(ge=1, le=20)] = 20,
):
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
    limit: Annotated[int, Query(ge=1, le=20)] = 20,
):
    results = search_departamento(departamento, table, capped_limit(limit))
    return {"total": len(results), "limit": capped_limit(limit), "results": results}


@router.get("/reniec/ubigeo/{ubigeo}", tags=["RENIEC"])
def obtener_por_ubigeo(
    ubigeo: str,
    table: TableParam = "all",
    limit: Annotated[int, Query(ge=1, le=20)] = 20,
):
    results = search_ubigeo(ubigeo, table, capped_limit(limit))
    return {"total": len(results), "limit": capped_limit(limit), "results": results}


@router.get("/reniec/estado-civil/{estado}", tags=["RENIEC"])
def obtener_por_estado_civil(
    estado: str,
    table: TableParam = "all",
    limit: Annotated[int, Query(ge=1, le=20)] = 20,
):
    results = search_estado_civil(estado, table, capped_limit(limit))
    return {"total": len(results), "limit": capped_limit(limit), "results": results}

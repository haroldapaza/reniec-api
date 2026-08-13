-- Ejecutar DESPUÉS de terminar la migración masiva.
-- Con 67M de filas, crear índices puede tardar y consumir bastante SSD.

CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Búsqueda exacta por documento (muy importante)
CREATE INDEX IF NOT EXISTS idx_reniec_nro_documento
    ON public.reniec (nro_documento);

CREATE INDEX IF NOT EXISTS idx_reniec2_nro_documento
    ON public.reniec2 (nro_documento);

-- ILIKE '%texto%' en nombres/apellidos
CREATE INDEX IF NOT EXISTS idx_reniec_nombre_trgm
    ON public.reniec USING gin (nombre gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_reniec_ape_paterno_trgm
    ON public.reniec USING gin (ape_paterno gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_reniec_ape_materno_trgm
    ON public.reniec USING gin (ape_materno gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_reniec2_nombre_trgm
    ON public.reniec2 USING gin (nombre gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_reniec2_ape_paterno_trgm
    ON public.reniec2 USING gin (ape_paterno gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_reniec2_ape_materno_trgm
    ON public.reniec2 USING gin (ape_materno gin_trgm_ops);

-- Departamento / ubicación
CREATE INDEX IF NOT EXISTS idx_reniec_departamento_trgm
    ON public.reniec USING gin (nom_departamento gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_reniec_ubigeo_trgm
    ON public.reniec USING gin (des_ubigeo gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_reniec2_ubigeo_direccion_trgm
    ON public.reniec2 USING gin (des_ubigeo_direccion gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_reniec2_ubigeo_nacimiento_trgm
    ON public.reniec2 USING gin (des_ubigeo_nacimiento gin_trgm_ops);

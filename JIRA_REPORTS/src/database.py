import pyodbc
import pandas as pd

from config.settings import (
    DB_SERVER,
    DB_DATABASE
)

from src.logger import logger


class Database:

    def get_connection(self):

        return pyodbc.connect(
            f"""
            DRIVER={{ODBC Driver 17 for SQL Server}};
            SERVER={DB_SERVER};
            DATABASE={DB_DATABASE};
            Trusted_Connection=yes;
            TrustServerCertificate=yes;
            """
        )

    def test_connection(self):

        conn = self.get_connection()
        logger.info("✅ Conexión SQL Server exitosa")
        conn.close()


    def load_csv(self, csv_path):

        logger.info(
            f"📥 Leyendo CSV: {csv_path}"
        )

        df = pd.read_csv(
            csv_path,
            encoding="utf-8"
        )

        meses = {
            "ene": "Jan",
            "feb": "Feb",
            "mar": "Mar",
            "abr": "Apr",
            "may": "May",
            "jun": "Jun",
            "jul": "Jul",
            "ago": "Aug",
            "sep": "Sep",
            "oct": "Oct",
            "nov": "Nov",
            "dic": "Dec"
        }

        for columna in [
            "Creada",
            "Actualizada",
            "Resuelta"
        ]:

            if columna in df.columns:

                df[columna] = (
                    df[columna]
                    .fillna("")
                    .astype(str)
                    .replace(meses, regex=True)
                )

                df[columna] = pd.to_datetime(
                    df[columna],
                    format="%d/%b/%y %H:%M",
                    errors="coerce"
                )

        conn = self.get_connection()

        cursor = conn.cursor()

        registros_ok = 0

        def limpiar(valor):

            if pd.isna(valor):
                return None

            valor = str(valor).strip()

            if valor == "":
                return None

            return valor

        for _, row in df.iterrows():

            try:

                fecha_creacion = None

                if pd.notna(row["Creada"]):

                    try:
                        fecha_creacion = row["Creada"].to_pydatetime()
                    except Exception:
                        fecha_creacion = None

                fecha_actualizada = (
                    None
                    if pd.isna(row["Actualizada"])
                    else row["Actualizada"].to_pydatetime()
                )

                fecha_resolucion = (
                    None
                    if pd.isna(row["Resuelta"])
                    else row["Resuelta"].to_pydatetime()
                )

                votos = 0

                try:

                    valor_votos = str(row["Votos"]).strip()

                    if valor_votos not in ("", "nan", "None"):

                        votos = int(float(valor_votos))

                except Exception:

                    votos = 0


                parent_issue_id = None

                if "ID del elemento padre" in df.columns:

                    valor_padre = row["ID del elemento padre"]

                    if pd.notna(valor_padre):

                        valor_padre = str(valor_padre).strip()

                        if valor_padre != "":

                            try:
                                parent_issue_id = int(valor_padre)
                            except ValueError:
                                parent_issue_id = None

                ultimo_comentario = (
                    str(row["Campo personalizado (Ultimo Comentario)"])
                    if pd.notna(row["Campo personalizado (Ultimo Comentario)"])
                    else None
                )

                pais = "Peru"

                empresa = (
                    str(row["Campo personalizado (Empresa)"])
                    if pd.notna(row["Campo personalizado (Empresa)"])
                    else None
                )

                tipo_incidencia = (
                    str(row["Tipo de Incidencia"]).strip()
                    if pd.notna(row["Tipo de Incidencia"])
                    else None
                )

                estado = (
                    str(row["Estado"]).strip()
                    if pd.notna(row["Estado"])
                    else None
                )

                prioridad = (
                    str(row["Prioridad"]).strip()
                    if pd.notna(row["Prioridad"])
                    else None
                )

                proyecto_key = (
                    str(row["Clave del proyecto"]).strip()
                    if pd.notna(row["Clave del proyecto"])
                    else None
                )

                proyecto_nombre = (
                    str(row["Nombre del proyecto"]).strip()
                    if pd.notna(row["Nombre del proyecto"])
                    else None
                )

                proyecto_tipo = (
                    str(row["Tipo de proyecto"]).strip()
                    if pd.notna(row["Tipo de proyecto"])
                    else None
                )

                responsable = (
                    str(row["Responsable"]).strip()
                    if pd.notna(row["Responsable"])
                    else None
                )

                informador = (
                    str(row["Informador"]).strip()
                    if pd.notna(row["Informador"])
                    else None
                )

                creador = (
                    str(row["Creador"]).strip()
                    if pd.notna(row["Creador"])
                    else None
                )

                resumen = (
                    str(row["Resumen"]).strip()
                    if pd.notna(row["Resumen"])
                    else None
                )

                descripcion = (
                    str(row["Descripción"]).strip()
                    if pd.notna(row["Descripción"])
                    else None
                )

                # Audtioria
                #logger.info(
                #    f"""
                #    Ticket={row['Clave de incidencia']}
                #    Resumen={resumen!r}
                #    TipoIncidencia={tipo_incidencia!r}
                #    Estado={estado!r}
                #    Prioridad={prioridad!r}
                #    ParentIssueId={parent_issue_id!r}
                #    Empresa={empresa!r}
                #    """
                #)
                

                cursor.execute(
                    """
                    MERGE dbo.JiraTickets AS T

                    USING (
                        SELECT ? AS TicketKey
                    ) AS S

                    ON T.TicketKey = S.TicketKey

                    WHEN MATCHED THEN

                        UPDATE SET
                            Resumen = ?,
                            TipoIncidencia = ?,
                            Estado = ?,
                            Prioridad = ?,
                            ProyectoKey = ?,
                            ProyectoNombre = ?,
                            ProyectoTipo = ?,
                            Responsable = ?,
                            Informador = ?,
                            Creador = ?,
                            FechaCreacion = ?,
                            FechaActualizacion = ?,
                            FechaResolucion = ?,
                            Votos = ?,
                            Descripcion = ?,
                            ParentIssueId = ?,
                            UltimoComentario = ?,
                            Pais = ?,
                            Empresa = ?,
                            FechaUltimaSincronizacion = GETDATE()

                    WHEN NOT MATCHED THEN

                        INSERT
                        (
                            TicketKey,
                            TicketId,
                            Resumen,
                            TipoIncidencia,
                            Estado,
                            Prioridad,
                            ProyectoKey,
                            ProyectoNombre,
                            ProyectoTipo,
                            Responsable,
                            Informador,
                            Creador,
                            FechaCreacion,
                            FechaActualizacion,
                            FechaResolucion,
                            Votos,
                            Descripcion,
                            ParentIssueId,
                            UltimoComentario,
                            Pais,
                            Empresa
                        )

                        VALUES
                        (
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                        );
                    """,

                    # MATCH
                    str(row["Clave de incidencia"]),

                    resumen,

                    tipo_incidencia,

                    estado,

                    prioridad,

                    proyecto_key,

                    proyecto_nombre,

                    proyecto_tipo,

                    responsable,

                    informador,

                    creador,

                    fecha_creacion,

                    fecha_actualizada,

                    fecha_resolucion,

                    votos,

                    descripcion,

                    parent_issue_id,

                    ultimo_comentario,

                    pais,

                    empresa,
                    
                    # INSERT
                    str(row["Clave de incidencia"]),

                    int(row["ID de la incidencia"])
                    if pd.notna(row["ID de la incidencia"])
                    else None,

                    resumen,

                    tipo_incidencia,

                    estado,

                    prioridad,

                    proyecto_key,

                    proyecto_nombre,

                    proyecto_tipo,

                    responsable,

                    informador,

                    creador,

                    fecha_creacion,

                    fecha_actualizada,

                    fecha_resolucion,

                    votos,

                    descripcion,

                    parent_issue_id,

                    ultimo_comentario,

                    pais,

                    empresa,

                )

                registros_ok += 1

            except Exception as e:

                logger.error(
                    f"❌ Error Ticket: {row['Clave de incidencia']}"
                )

                logger.error(
                    f"Actualizada: {repr(row['Actualizada'])}"
                )

                logger.error(str(e))

        conn.commit()

        cursor.close()
        conn.close()

        logger.info(
            f"✅ Registros procesados: {registros_ok}"
        )
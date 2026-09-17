import pyodbc

from src.logger import logger


class KPIService:
    ESTADOS_ATENDIDOS = (
        "Cancelado",
        "Cerrado",
        "Listo",
        "Finalizado",
        "Resuelto",
    )

    def _get_connection(self):
        return pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=WL01IT065\\SQLEXPRESS;"
            "DATABASE=JiraAutomation;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )

    @staticmethod
    def _valor(row, campo, default=0):
        if row is None:
            return default
        valor = getattr(row, campo, None)
        return default if valor is None else valor

    def get_resumen(self):
        logger.info("📊 Consultando indicadores en SQL Server")

        conn = self._get_connection()
        cursor = conn.cursor()

        try:

            # Backlog Historico
            cursor.execute("""
                SELECT count(*) as BacklogHistorico
                FROM dbo.JiraTickets j
                WHERE j.Estado NOT IN (
                    'Cancelado','Cerrado','Listo','Finalizado','Resuelto'
                )
            """)
            row_backlog_historico = cursor.fetchone()

            # Año actual. Total y pendientes se filtran por creación.
            cursor.execute("""
                SELECT
                    COUNT(*) AS TotalTicketsAno,
                    SUM(CASE WHEN Estado NOT IN (
                        'Cancelado','Cerrado','Listo','Finalizado','Resuelto'
                    ) THEN 1 ELSE 0 END) AS TicketsPendientesAno
                FROM dbo.JiraTickets
                WHERE FechaCreacion >= DATEFROMPARTS(YEAR(GETDATE()), 1, 1)
                  AND FechaCreacion < DATEFROMPARTS(YEAR(GETDATE()) + 1, 1, 1);
            """)
            row_anio_creacion = cursor.fetchone()

            # Año actual. Atendidos, TMR y SLA se filtran por resolución.
            cursor.execute("""
                SELECT
                    COUNT(*) AS TicketsAtendidosAno,
                    ROUND(AVG(TRY_CAST(TiempoResolucion AS FLOAT)), 2)
                        AS TiempoMedioResolucionAno,
                    CAST(
                        ROUND(
                            SUM(CASE WHEN EstadoSLA = 'Cumple' THEN 1.0 ELSE 0.0 END)
                            * 100.0 /
                            NULLIF(SUM(CASE WHEN EstadoSLA IN ('Cumple','No Cumple')
                                            THEN 1 ELSE 0 END), 0),
                            2
                        ) AS DECIMAL(5,2)
                    ) AS PorcentajeSLAAno
                FROM dbo.JiraTickets
                WHERE FechaResolucion >= DATEFROMPARTS(YEAR(GETDATE()), 1, 1)
                  AND FechaResolucion < DATEFROMPARTS(YEAR(GETDATE()) + 1, 1, 1)
                  AND Estado IN ('Cancelado','Cerrado','Listo','Finalizado','Resuelto');
            """)
            row_anio_resolucion = cursor.fetchone()

            # Hoy por creación.
            cursor.execute("""
                DECLARE @InicioHoy DATE = CAST(GETDATE() AS DATE);
                DECLARE @FinHoy DATE = DATEADD(DAY, 1, @InicioHoy);

                SELECT
                    COUNT(*) AS TotalTicketsHoy,
                    SUM(CASE WHEN Estado NOT IN (
                        'Cancelado','Cerrado','Listo','Finalizado','Resuelto'
                    ) THEN 1 ELSE 0 END) AS TicketsPendientesHoy
                FROM dbo.JiraTickets
                WHERE FechaCreacion >= @InicioHoy
                  AND FechaCreacion < @FinHoy;
            """)
            row_hoy_creacion = cursor.fetchone()

            # Hoy por resolución.
            cursor.execute("""
                DECLARE @InicioHoy DATE = CAST(GETDATE() AS DATE);
                DECLARE @FinHoy DATE = DATEADD(DAY, 1, @InicioHoy);

                SELECT
                    COUNT(*) AS TicketsAtendidosHoy,
                    ROUND(AVG(TRY_CAST(TiempoResolucion AS FLOAT)), 2)
                        AS TiempoMedioResolucionHoy,
                    CAST(
                        ROUND(
                            SUM(CASE WHEN EstadoSLA = 'Cumple' THEN 1.0 ELSE 0.0 END)
                            * 100.0 /
                            NULLIF(SUM(CASE WHEN EstadoSLA IN ('Cumple','No Cumple')
                                            THEN 1 ELSE 0 END), 0),
                            2
                        ) AS DECIMAL(5,2)
                    ) AS PorcentajeSLAHoy
                FROM dbo.JiraTickets
                WHERE FechaResolucion >= @InicioHoy
                  AND FechaResolucion < @FinHoy
                  AND Estado IN ('Cancelado','Cerrado','Listo','Finalizado','Resuelto');
            """)
            row_hoy_resolucion = cursor.fetchone()

            # Mes actual por creación.
            cursor.execute("""
                DECLARE @InicioMes DATE = DATEFROMPARTS(YEAR(GETDATE()), MONTH(GETDATE()), 1);
                DECLARE @FinMes DATE = DATEADD(MONTH, 1, @InicioMes);

                SELECT
                    COUNT(*) AS TotalTicketsMes,
                    SUM(CASE WHEN Estado NOT IN (
                        'Cancelado','Cerrado','Listo','Finalizado','Resuelto'
                    ) THEN 1 ELSE 0 END) AS TicketsPendientesMes
                FROM dbo.JiraTickets
                WHERE FechaCreacion >= @InicioMes
                  AND FechaCreacion < @FinMes;
            """)
            row_mes_creacion = cursor.fetchone()

            # Mes actual por resolución.
            cursor.execute("""
                DECLARE @InicioMes DATE = DATEFROMPARTS(YEAR(GETDATE()), MONTH(GETDATE()), 1);
                DECLARE @FinMes DATE = DATEADD(MONTH, 1, @InicioMes);

                SELECT
                    COUNT(*) AS TicketsAtendidosMes,
                    ROUND(AVG(TRY_CAST(TiempoResolucion AS FLOAT)), 2)
                        AS TiempoMedioResolucionMes,
                    CAST(
                        ROUND(
                            SUM(CASE WHEN EstadoSLA = 'Cumple' THEN 1.0 ELSE 0.0 END)
                            * 100.0 /
                            NULLIF(SUM(CASE WHEN EstadoSLA IN ('Cumple','No Cumple')
                                            THEN 1 ELSE 0 END), 0),
                            2
                        ) AS DECIMAL(5,2)
                    ) AS PorcentajeSLAMes
                FROM dbo.JiraTickets
                WHERE FechaResolucion >= @InicioMes
                  AND FechaResolucion < @FinMes
                  AND Estado IN ('Cancelado','Cerrado','Listo','Finalizado','Resuelto');
            """)
            row_mes_resolucion = cursor.fetchone()

            # Mes anterior, robusto también para enero/diciembre.
            cursor.execute("""
                DECLARE @InicioActual DATE = DATEFROMPARTS(YEAR(GETDATE()), MONTH(GETDATE()), 1);
                DECLARE @InicioAnterior DATE = DATEADD(MONTH, -1, @InicioActual);

                SELECT
                    COUNT(*) AS TotalTicketsMesAnterior,
                    SUM(CASE WHEN Estado NOT IN (
                        'Cancelado','Cerrado','Listo','Finalizado','Resuelto'
                    ) THEN 1 ELSE 0 END) AS TicketsPendientesMesAnterior
                FROM dbo.JiraTickets
                WHERE FechaCreacion >= @InicioAnterior
                  AND FechaCreacion < @InicioActual;
            """)
            row_anterior_creacion = cursor.fetchone()

            cursor.execute("""
                DECLARE @InicioActual DATE = DATEFROMPARTS(YEAR(GETDATE()), MONTH(GETDATE()), 1);
                DECLARE @InicioAnterior DATE = DATEADD(MONTH, -1, @InicioActual);

                SELECT
                    COUNT(*) AS TicketsAtendidosMesAnterior,
                    ROUND(AVG(TRY_CAST(TiempoResolucion AS FLOAT)), 2)
                        AS TiempoMedioResolucionMesAnterior,
                    CAST(
                        ROUND(
                            SUM(CASE WHEN EstadoSLA = 'Cumple' THEN 1.0 ELSE 0.0 END)
                            * 100.0 /
                            NULLIF(SUM(CASE WHEN EstadoSLA IN ('Cumple','No Cumple')
                                            THEN 1 ELSE 0 END), 0),
                            2
                        ) AS DECIMAL(5,2)
                    ) AS PorcentajeSLAMesAnterior
                FROM dbo.JiraTickets
                WHERE FechaResolucion >= @InicioAnterior
                  AND FechaResolucion < @InicioActual
                  AND Estado IN ('Cancelado','Cerrado','Listo','Finalizado','Resuelto');
            """)
            row_anterior_resolucion = cursor.fetchone()

            equipos = self._get_kpis_equipos(cursor)
            top_tickets = self._get_top_tickets(cursor)

            resultado = {
                "backlogh": self._valor(row_backlog_historico, "BacklogHistorico"),
                "totala": self._valor(row_anio_creacion, "TotalTicketsAno"),
                "atendidosa": self._valor(row_anio_resolucion, "TicketsAtendidosAno"),
                "pendientesa": self._valor(row_anio_creacion, "TicketsPendientesAno"),
                "tmra": float(self._valor(row_anio_resolucion, "TiempoMedioResolucionAno")),
                "slaa": float(self._valor(row_anio_resolucion, "PorcentajeSLAAno")),
                "totalhoy": self._valor(row_hoy_creacion, "TotalTicketsHoy"),
                "atendidoshoy": self._valor(row_hoy_resolucion, "TicketsAtendidosHoy"),
                "pendienteshoy": self._valor(row_hoy_creacion, "TicketsPendientesHoy"),
                "tmrhoy": float(self._valor(row_hoy_resolucion, "TiempoMedioResolucionHoy")),
                "slahoy": float(self._valor(row_hoy_resolucion, "PorcentajeSLAHoy")),
                "totalm": self._valor(row_mes_creacion, "TotalTicketsMes"),
                "atendidosm": self._valor(row_mes_resolucion, "TicketsAtendidosMes"),
                "pendientesm": self._valor(row_mes_creacion, "TicketsPendientesMes"),
                "tmrm": float(self._valor(row_mes_resolucion, "TiempoMedioResolucionMes")),
                "slam": float(self._valor(row_mes_resolucion, "PorcentajeSLAMes")),
                "totalmant": self._valor(row_anterior_creacion, "TotalTicketsMesAnterior"),
                "atendidosmant": self._valor(row_anterior_resolucion, "TicketsAtendidosMesAnterior"),
                "pendientesmant": self._valor(row_anterior_creacion, "TicketsPendientesMesAnterior"),
                "tmrmant": float(self._valor(row_anterior_resolucion, "TiempoMedioResolucionMesAnterior")),
                "slamant": float(self._valor(row_anterior_resolucion, "PorcentajeSLAMesAnterior")),
                "equipos": equipos,
                "top_tickets": top_tickets,
            }

            logger.info(
                "✅ KPIs consultados: %s equipos y %s tickets antiguos",
                len(equipos),
                len(top_tickets),
            )
            return resultado

        finally:
            cursor.close()
            conn.close()

    def _get_kpis_equipos(self, cursor):
        # Total y pendientes del mes por fecha de creación.
        cursor.execute("""
            DECLARE @InicioMes DATE = DATEFROMPARTS(YEAR(GETDATE()), MONTH(GETDATE()), 1);
            DECLARE @FinMes DATE = DATEADD(MONTH, 1, @InicioMes);

            SELECT
                CASE
                    WHEN da.Grupo IN ('CANV - ServTI','EXP - ServTI') THEN 'MDA-Experis'
                    WHEN da.Grupo = 'EXT - ServTI' THEN 'Externo'
                    WHEN da.Grupo = 'Nivel 2 - ServTI' THEN 'MDA-DP World'
                    WHEN da.Grupo = 'Nivel 3 - Infra' THEN 'Infraestructura'
                    WHEN da.Grupo = 'Nivel 3 - TOS' THEN 'TOS'
                    WHEN da.Grupo IN ('Nivel 3 - App','Nivel 3 - BS')
                        THEN 'Aplicaciones'
                    ELSE 'Sin Asignar'
                END AS Equipo,
                COUNT(*) AS Total,
                SUM(CASE WHEN j.Estado NOT IN (
                    'Cancelado','Cerrado','Listo','Finalizado','Resuelto'
                ) THEN 1 ELSE 0 END) AS Pendientes
            FROM dbo.JiraTickets j
            LEFT JOIN dbo.DimAnalistas da
                ON j.Responsable = da.CodigoUsuario
            WHERE j.FechaCreacion >= @InicioMes
              AND j.FechaCreacion < @FinMes
            GROUP BY
                CASE
                    WHEN da.Grupo IN ('CANV - ServTI','EXP - ServTI') THEN 'MDA-Experis'
                    WHEN da.Grupo = 'EXT - ServTI' THEN 'Externo'
                    WHEN da.Grupo = 'Nivel 2 - ServTI' THEN 'MDA-DP World'
                    WHEN da.Grupo = 'Nivel 3 - Infra' THEN 'Infraestructura'
                    WHEN da.Grupo = 'Nivel 3 - TOS' THEN 'TOS'
                    WHEN da.Grupo IN ('Nivel 3 - App','Nivel 3 - BS')
                        THEN 'Aplicaciones'
                    ELSE 'Sin Asignar'
                END;
        """)
        creados = {
            row.Equipo: {"equipo": row.Equipo, "total": row.Total or 0,
                         "pendientes": row.Pendientes or 0}
            for row in cursor.fetchall()
        }

        # Atendidos, TMR y SLA del mes por fecha de resolución.
        cursor.execute("""
                DECLARE @InicioMes DATE = DATEFROMPARTS(YEAR(GETDATE()), MONTH(GETDATE()), 1);
            DECLARE @FinMes DATE = DATEADD(MONTH, 1, @InicioMes);

            SELECT
                CASE
                    WHEN da.Grupo IN ('CANV - ServTI','EXP - ServTI') THEN 'MDA-Experis'
                    WHEN da.Grupo = 'EXT - ServTI' THEN 'Externo'
                    WHEN da.Grupo = 'Nivel 2 - ServTI' THEN 'MDA-DP World'
                    WHEN da.Grupo = 'Nivel 3 - Infra' THEN 'Infraestructura'
                    WHEN da.Grupo = 'Nivel 3 - TOS' THEN 'TOS'
                    WHEN da.Grupo IN ('Nivel 3 - App','Nivel 3 - BS')
                        THEN 'Aplicaciones'
                    ELSE 'Sin Asignar'
                END AS Equipo,
                COUNT(*) AS Atendidos,
                ROUND(AVG(TRY_CAST(j.TiempoResolucion AS FLOAT)), 2) AS TMR,
                CAST(
                    ROUND(
                        SUM(CASE WHEN j.EstadoSLA = 'Cumple' THEN 1.0 ELSE 0.0 END)
                        * 100.0 /
                        NULLIF(SUM(CASE WHEN j.EstadoSLA IN ('Cumple','No Cumple')
                                        THEN 1 ELSE 0 END), 0),
                        2
                    ) AS DECIMAL(5,2)
                ) AS SLA
            FROM dbo.JiraTickets j
            LEFT JOIN dbo.DimAnalistas da
                ON j.Responsable = da.CodigoUsuario
            WHERE j.FechaResolucion >= @InicioMes
              AND j.FechaResolucion < @FinMes
              AND j.Estado IN ('Cancelado','Cerrado','Listo','Finalizado','Resuelto')
            GROUP BY
                CASE
                    WHEN da.Grupo IN ('CANV - ServTI','EXP - ServTI') THEN 'MDA-Experis'
                    WHEN da.Grupo = 'EXT - ServTI' THEN 'Externo'
                    WHEN da.Grupo = 'Nivel 2 - ServTI' THEN 'MDA-DP World'
                    WHEN da.Grupo = 'Nivel 3 - Infra' THEN 'Infraestructura'
                    WHEN da.Grupo = 'Nivel 3 - TOS' THEN 'TOS'
                    WHEN da.Grupo IN ('Nivel 3 - App','Nivel 3 - BS')
                        THEN 'Aplicaciones'
                    ELSE 'Sin Asignar'
                END;
        """)
        resueltos = {
            row.Equipo: {"atendidos": row.Atendidos or 0,
                         "tmr": float(row.TMR or 0), "sla": float(row.SLA or 0)}
            for row in cursor.fetchall()
        }

        orden = ["MDA-Experis", "MDA-DP World", "Infraestructura", "Aplicaciones", "TOS", "Externo", "Sin Asignar"]
        resultado = []
        for equipo in orden:
            base = creados.get(equipo, {"equipo": equipo, "total": 0, "pendientes": 0})
            cierre = resueltos.get(equipo, {"atendidos": 0, "tmr": 0.0, "sla": 0.0})
            resultado.append({**base, **cierre})
        return resultado

    def _get_top_tickets(self, cursor):
        cursor.execute("""
            SELECT TOP (10)
                j.TicketKey AS Ticket,
                j.Resumen AS Asunto,
                COALESCE(da.Grupo, 'Sin Asignar') AS Equipo,
                COALESCE(da.Nombre, j.Responsable, 'Sin Asignar') AS Responsable,
                j.Estado,
                DATEDIFF(DAY, j.FechaCreacion, GETDATE()) AS DiasAbierto
            FROM dbo.JiraTickets j
            LEFT JOIN dbo.DimAnalistas da
                ON j.Responsable = da.CodigoUsuario
            WHERE j.Estado NOT IN (
                'Cancelado','Cerrado','Listo','Finalizado','Resuelto'
            )
            ORDER BY DiasAbierto DESC, j.TicketKey;
        """)
        return [
            {
                "ticket": row.Ticket or "",
                "asunto": row.Asunto or "Sin asunto",
                "equipo": row.Equipo or "Sin Asignar",
                "responsable": row.Responsable or "Sin Asignar",
                "estado": row.Estado or "",
                "dias_abierto": row.DiasAbierto or 0,
            }
            for row in cursor.fetchall()
        ]

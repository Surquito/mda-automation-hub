import html
import os
import time
from datetime import datetime

import win32com.client

from src.logger import logger


class Mailer:
    @staticmethod
    def _n(valor):
        try:
            return f"{int(valor or 0):,}".replace(",", ".")
        except (TypeError, ValueError):
            return "0"

    @staticmethod
    def _f(valor):
        try:
            return f"{float(valor or 0):.2f}"
        except (TypeError, ValueError):
            return "0.00"

    def _filas_equipos(self, equipos):
        filas = []
        for i, equipo in enumerate(equipos):
            fondo = "#FFFFFF" if i % 2 == 0 else "#F7F9FC"
            tmr = float(equipo.get("tmr", 0) or 0)
            color = "#17A558" if tmr < 3 else "#F59E0B" if tmr < 7 else "#D93025"
            sla = float(equipo.get("sla", 0) or 0)
            color = "#17A558" if sla >= 80 else "#D93025"
            filas.append(f"""<tr style="background:{fondo}">
            <td style="padding:8px">{html.escape(str(equipo.get('equipo','Sin Asignar')))}</td>
            <td align="center">{self._n(equipo.get('total'))}</td>
            <td align="center">{self._n(equipo.get('atendidos'))}</td>
            <td align="center">{self._n(equipo.get('pendientes'))}</td>
            <td align="center">{self._f(equipo.get('tmr'))}</td>
            <td align="center" style="color:{color};font-weight:bold">{self._f(sla)}%</td></tr>""")
        return "".join(filas)

    def _filas_top(self, tickets):
        if not tickets:
            return '<tr><td colspan="6" align="center">Sin tickets pendientes</td></tr>'
        filas = []
        for ticket in tickets:
            filas.append(f"""<tr>
            <td>{html.escape(str(ticket.get('ticket','')))}</td>
            <td>{html.escape(str(ticket.get('asunto','')))}</td>
            <td>{html.escape(str(ticket.get('equipo','')))}</td>
            <td>{html.escape(str(ticket.get('responsable','')))}</td>
            <td align="center">{html.escape(str(ticket.get('estado','')))}</td>
            <td align="center">{int(ticket.get('dias_abierto',0) or 0)}</td></tr>""")
        return "".join(filas)

    def send_mail(self, destinatarios, cc, bcc, asunto, adjunto, imagenes_tendencias, kpis):
        inicio = time.time()
        logger.info("📧 Conectando con Outlook")
        outlook = win32com.client.GetActiveObject("Outlook.Application")
        mail = outlook.CreateItem(0)

        adjunto = os.path.abspath(adjunto)
        if not os.path.isfile(adjunto):
            raise FileNotFoundError(f"No se encontró el PDF: {adjunto}")
        if len(imagenes_tendencias) != 4:
            raise ValueError("Se requieren exactamente cuatro imágenes de tendencia.")

        cids = []

        for indice, ruta_imagen in enumerate(
            imagenes_tendencias,
            start=1
        ):
            ruta_imagen = os.path.abspath(
                ruta_imagen
            )

            if not os.path.isfile(ruta_imagen):
                raise FileNotFoundError(
                    f"No se encontró la imagen: {ruta_imagen}"
                )

            cid = f"tendencia_{indice}"

            logger.info(
                "🖼️ Incrustando imagen %s con CID %s: %s",
                indice,
                cid,
                ruta_imagen
            )

            imagen_adjunta = mail.Attachments.Add(
                ruta_imagen
            )

            property_accessor = (
                imagen_adjunta.PropertyAccessor
            )

            # Identificador usado en el HTML: src="cid:tendencia_X"
            property_accessor.SetProperty(
                "http://schemas.microsoft.com/mapi/"
                "proptag/0x3712001F",
                cid
            )

            # Tipo MIME de la imagen
            property_accessor.SetProperty(
                "http://schemas.microsoft.com/mapi/"
                "proptag/0x370E001F",
                "image/png"
            )

            # Ocultar imagen de la bandeja visible de adjuntos
            try:
                property_accessor.SetProperty(
                    "http://schemas.microsoft.com/mapi/"
                    "proptag/0x7FFE000B",
                    True
                )

                logger.info(
                    "✅ Imagen %s marcada como oculta",
                    indice
                )

            except Exception as error_oculto:
                logger.warning(
                    "⚠️ Outlook no permitió ocultar la imagen %s: %s",
                    indice,
                    error_oculto
                )

            cids.append(
                cid
            )

        logger.info(
            "✅ Las cuatro imágenes quedaron incrustadas mediante CID"
        )
        fecha = datetime.now().strftime("%d/%m/%Y")
        fecha_hora = datetime.now().strftime("%d/%m/%Y %I:%M %p")
        mail.To = destinatarios
        mail.CC = cc or ""
        mail.BCC = bcc or ""
        mail.Subject = f"{asunto} - {fecha}"

        filas_equipos = self._filas_equipos(kpis.get("equipos", []))
        filas_top = self._filas_top(kpis.get("top_tickets", []))

        # Imágenes incrustadas en el cuerpo, distribuidas en 2 filas x 2 columnas.
        imagenes_html = f"""
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;border-collapse:separate;">
        <tr>
            <td width="49%" valign="top" style="width:49%;background:#FFFFFF;border:1px solid #D9E1EC;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                <td align="center" style="padding:10px 6px;background:#EEF5FF;border-bottom:1px solid #D9E1EC;color:#1665D8;font-size:12px;font-weight:bold;">
                    📥 RECIBIDOS VS. ✅ ATENDIDOS
                </td>
                </tr>
                <tr>
                <td align="center" style="padding:6px;background:#FFFFFF;">
                    <img src="cid:{cids[0]}" width="430" style="display:block;width:430px;max-width:100%;height:auto;border:0;" alt="Total vs. Atendidos">
                </td>
                </tr>
            </table>
            </td>
            <td width="2%" style="width:2%;font-size:0;">
            &nbsp;
            </td>
            <td width="49%" valign="top" style="width:49%;background:#FFFFFF;border:1px solid #D9E1EC;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                <td align="center" style="padding:10px 6px;background:#FFF8E6;border-bottom:1px solid #D9E1EC;color:#B77900;font-size:12px;font-weight:bold;">
                    ⏳ TICKETS PENDIENTES
                </td>
                </tr>
                <tr>
                <td align="center" style="padding:6px;background:#FFFFFF;">
                    <img src="cid:{cids[1]}" width="430" style="display:block;width:430px;max-width:100%;height:auto;border:0;" alt="Tickets pendientes">
                </td>
                </tr>
            </table>
            </td>
        </tr>
        <tr>
            <td colspan="3" height="14" style="height:14px;font-size:0;">
            &nbsp;
            </td>
        </tr>
        <tr>
            <td width="49%" valign="top" style="width:49%;background:#FFFFFF;border:1px solid #D9E1EC;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                <td align="center" style="padding:10px 6px;background:#F4ECFF;border-bottom:1px solid #D9E1EC;color:#7549C7;font-size:12px;font-weight:bold;">
                    ⏱️ TIEMPO MEDIO DE RESOLUCIÓN
                </td>
                </tr>
                <tr>
                <td align="center" style="padding:6px;background:#FFFFFF;">
                    <img src="cid:{cids[2]}" width="430" style="display:block;width:430px;max-width:100%;height:auto;border:0;" alt="Tiempo medio de resolución">
                </td>
                </tr>
            </table>
            </td>
            <td width="2%" style="width:2%;font-size:0;">
            &nbsp;
            </td>
            <td width="49%" valign="top" style="width:49%;background:#FFFFFF;border:1px solid #D9E1EC;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                <td align="center" style="padding:10px 6px;background:#F0FFF5;border-bottom:1px solid #D9E1EC;color:#138A4D;font-size:12px;font-weight:bold;">
                    🎯 CUMPLIMIENTO SLA
                </td>
                </tr>
                <tr>
                <td align="center" style="padding:6px;background:#FFFFFF;">
                    <img src="cid:{cids[3]}" width="430" style="display:block;width:430px;max-width:100%;height:auto;border:0;" alt="Cumplimiento SLA">
                </td>
                </tr>
            </table>
            </td>
        </tr>
        </table>
        """

        mail.HTMLBody = f"""
        <html>
        <body style="margin:0;padding:0;background:#F3F6FA;font-family:Calibri,Arial,sans-serif;color:#14213D;">
            <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
                <td align="center">
                <table width="950" cellpadding="0" cellspacing="0" style="background:#FFFFFF;border-radius:10px;">
                    <tr>
                    <td style="padding:20px;background:#063B78;color:white;border-radius:10px 10px 0 0;">
                        <table width="100%">
                        <tr>
                            <td>
                            <div style="font-size:14px;font-weight:bold;color:#DCEAFF;">
                                💻 MESA DE AYUDA
                            </div>
                            <div style="font-size:30px;font-weight:bold;">
                                DASHBOARD MENSUAL Y DIARIO
                            </div>
                            </td>
                            <td align="right" style="font-size:20px;font-weight:bold;">
                            📅 {fecha}
                            </td>
                        </tr>
                        </table>
                    </td>
                    </tr>
                    <tr>
                    <td style="padding:18px 20px 8px;color:#1261C9;font-size:17px;font-weight:bold;">
                        1. KPIs EJECUTIVOS
                    </td>
                    </tr>
                    <tr>
                    <td style="padding:0 20px 20px;">
                        <table width="100%" cellpadding="0" cellspacing="8">
                        <tr>
                            <td align="center" style="background:#F0FFF5;border:1px solid #D9E1EC;border-radius:10px;padding:15px;">
                            <div style="font-size:30px;">
                                🎯
                            </div>
                            <div>
                                <b>
                                SLA
                                </b>
                            </div>
                            <div style="font-size:30px;font-weight:bold;color:#17A558;">
                                {self._f(kpis.get('slam'))}%
                            </div>
                            <div style="font-size:11px;">
                                Meta 80%
                            </div>
                            </td>
                            <td align="center" style="background:#EAF5FF;border:1px solid #D9E1EC;border-radius:10px;padding:15px;">
                            <div style="font-size:30px;">
                                📥
                            </div>
                            <div>
                                <b>
                                RECIBIDOS
                                </b>
                            </div>
                            <div style="font-size:30px;font-weight:bold;color:#1665D8;">
                                {self._n(kpis.get('totalm'))}
                            </div>
                            <div style="font-size:11px;">
                                Mensual
                            </div>
                            </td>
                            <td align="center" style="background:#ECFFF0;border:1px solid #D9E1EC;border-radius:10px;padding:15px;">
                            <div style="font-size:30px;">
                                ✅
                            </div>
                            <div>
                                <b>
                                ATENDIDOS
                                </b>
                            </div>
                            <div style="font-size:30px;font-weight:bold;color:#17A558;">
                                {self._n(kpis.get('atendidosm'))}
                            </div>
                            <div style="font-size:11px;">
                                Mensual
                            </div>
                            </td>
                            <td align="center" style="background:#F4ECFF;border:1px solid #D9E1EC;border-radius:10px;padding:15px;">
                            <div style="font-size:30px;">
                                ⏱️
                            </div>
                            <div>
                                <b>
                                TMR
                                </b>
                            </div>
                            <div style="font-size:30px;font-weight:bold;color:#7549C7;">
                                {self._f(kpis.get('tmrm'))}
                            </div>
                            <div style="font-size:11px;">
                                Mensual
                            </div>
                            </td>
                            <td align="center" style="background:#FFF8E6;border:1px solid #D9E1EC;border-radius:10px;padding:15px;">
                            <div style="font-size:30px;">
                                ⏳
                            </div>
                            <div>
                                <b>
                                BACKLOG
                                </b>
                            </div>
                            <div style="font-size:30px;font-weight:bold;color:#F59E0B;">
                                {self._n(kpis.get('backlogh'))}
                            </div>
                            <div style="font-size:11px;">
                                Acumulado
                            </div>
                            </td>
                        </tr>
                        </table>
                    </td>
                    </tr>
                    <tr>
                    <td style="padding:0 20px 8px;color:#1261C9;font-size:17px;font-weight:bold;">
                        2. RESUMEN DE INDICADORES
                    </td>
                    </tr>
                    <tr>
                    <td style="padding:0 20px 22px;">
                        <table width="100%" cellpadding="8" cellspacing="0" style="border-collapse:collapse;border:1px solid #CCD7E6;">
                        <tr style="background:#063B78;color:white;">
                            <th align="left">
                            INDICADOR
                            </th>
                            <th>
                            AÑO ACTUAL
                            </th>
                            <th>
                            MES ANTERIOR
                            </th>
                            <th>
                            MES ACTUAL
                            </th>
                            <th>
                            HOY
                            </th>
                        </tr>
                        <tr>
                            <td style="padding:8px;">
                            📌 Recibidos
                            </td>
                            <td align="center">
                            {self._n(kpis.get('totala'))}
                            </td>
                            <td align="center">
                            {self._n(kpis.get('totalmant'))}
                            </td>
                            <td align="center">
                            {self._n(kpis.get('totalm'))}
                            </td>
                            <td align="center">
                            {self._n(kpis.get('totalhoy'))}
                            </td>
                        </tr>
                        <tr style="baround:#F7F9FC;">
                            <td style="padding:8px;">
                            ✅ Atendidos
                            </td>
                            <td align="center">
                            {self._n(kpis.get('atendidosa'))}
                            </td>
                            <td align="center">
                            {self._n(kpis.get('atendidosmant'))}
                            </td>
                            <td align="center">
                            {self._n(kpis.get('atendidosm'))}
                            </td>
                            <td align="center">
                            {self._n(kpis.get('atendidoshoy'))}
                            </td>
                        </tr>
                        <tr>
                            <td style="padding:8px;">
                            ⏳ Pendientes
                            </td>
                            <td align="center">
                            {self._n(kpis.get('pendientesa'))}
                            </td>
                            <td align="center">
                            {self._n(kpis.get('pendientesmant'))}
                            </td>
                            <td align="center">
                            {self._n(kpis.get('pendientesm'))}
                            </td>
                            <td align="center">
                            {self._n(kpis.get('pendienteshoy'))}
                            </td>
                        </tr>
                        <tr style="background:#F7F9FC;">
                            <td style="padding:8px;">
                            ⏱️ TMR
                            </td>
                            <td align="center">
                            {self._f(kpis.get('tmra'))} días
                            </td>
                            <td align="center">
                            {self._f(kpis.get('tmrmant'))} días
                            </td>
                            <td align="center">
                            {self._f(kpis.get('tmrm'))} días
                            </td>
                            <td align="center">
                            {self._f(kpis.get('tmrhoy'))} días
                            </td>
                        </tr>
                        <tr>
                            <td style="padding:8px;">
                            🎯 SLA
                            </td>
                            <td align="center">
                            {self._f(kpis.get('slaa'))}%
                            </td>
                            <td align="center">
                            {self._f(kpis.get('slamant'))}%
                            </td>
                            <td align="center">
                            {self._f(kpis.get('slam'))}%
                            </td>
                            <td align="center">
                            {self._f(kpis.get('slahoy'))}%
                            </td>
                        </tr>
                        </table>
                    </td>
                    </tr>
                    <tr>
                    <td style="padding:0 20px 8px;color:#1261C9;font-size:17px;font-weight:bold;">
                        3. TENDENCIA 7 DÍAS
                    </td>
                    </tr>
                    <tr>
                    <td style="padding:0 20px 22px;">
                        {imagenes_html}
                    </td>
                    </tr>
                    <tr>
                    <td style="padding:0 20px 8px;color:#1261C9;font-size:17px;font-weight:bold;">
                        4. KPI POR EQUIPO
                    </td>
                    </tr>
                    <tr>
                    <td style="padding:0 20px 22px;">
                        <table width="100%" border="1" cellspacing="0" cellpadding="6" style="border-collapse:collapse;border-color:#CCD7E6;">
                        <tr style="background:#063B78;color:white;">
                            <th>
                            EQUIPO
                            </th>
                            <th>
                            RECIBIDOS
                            </th>
                            <th>
                            ATENDIDOS
                            </th>
                            <th>
                            PENDIENTES
                            </th>
                            <th>
                            TMR
                            </th>
                            <th>
                            SLA
                            </th>
                        </tr>
                        {filas_equipos}
                        </table>
                    </td>
                    </tr>
                    <tr>
                    <td style="padding:0 20px 8px;color:#1261C9;font-size:17px;font-weight:bold;">
                        5. TOP 10 TICKETS MÁS ANTIGUOS
                    </td>
                    </tr>
                    <tr>
                    <td style="padding:0 20px 22px;">
                        <table width="100%" border="1" cellspacing="0" cellpadding="6" style="border-collapse:collapse;border-color:#CCD7E6;font-size:10pt;">
                        <tr style="background:#063B78;color:white;">
                            <th>
                            TICKET
                            </th>
                            <th>
                            ASUNTO
                            </th>
                            <th>
                            EQUIPO
                            </th>
                            <th>
                            RESPONSABLE
                            </th>
                            <th>
                            ESTADO
                            </th>
                            <th>
                            DÍAS
                            </th>
                        </tr>
                        {filas_top}
                        </table>
                    </td>
                    </tr>
                    <tr>
                    <td style="padding:20px;background:#EEF4FC;border-left:4px solid #1665D8;">
                        🌐
                        <b>
                        Dashboard Ejecutivo:
                        </b>
                        <a href="https://app.powerbi.com/view?r=eyJrIjoiNmQ0NjFmMzQtOTgyOC00NDZhLWIxNWQtNGM1YjU3NGVmODVhIiwidCI6IjJiZDE2YzliLTdlMjEtNDI3NC05YzA2LTc5MTlmNzY0N2JiYiIsImMiOjh9">
                        Abrir Dashboard MDA 📊
                        </a>
                        <br>
                        <br>
                        📎
                        <b>
                        Archivo adjunto:
                        </b>
                        {html.escape(os.path.basename(adjunto))}
                    </td>
                    </tr>
                    <tr>
                    <td align="center" style="padding:12px;background:#F3F6FA;color:#697386;font-size:10px;">
                        Reporte MDA disponible, estado en marcha blanca. 🏳️
                        <br>
                        Por favor, revisa el documento y respóndenos con tu feedback para mejorarlo.📨
                        <br>
                        🗓️ Datos actualizados al {fecha_hora}.
                        <br>
                        🤖 Correo generado automáticamente.
                    </td>
                    </tr>
                </table>
                </td>
            </tr>
            </table>
        </body>
        </html>
        """
        mail.Attachments.Add(adjunto)
        if not mail.Recipients.ResolveAll():
            invalidos = [r.Name for r in mail.Recipients if not r.Resolved]
            raise ValueError("Outlook no reconoce: " + ", ".join(invalidos))
        mail.Save()
        mail.Send()
        logger.info("✅ Correo enviado en %.2f segundos", time.time() - inicio)

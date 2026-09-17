# MDA Automation Hub

## 📌 Descripción General

**MDA Automation Hub** es una solución integral de automatización y analítica desarrollada para optimizar la gestión operativa de la Mesa de Ayuda mediante la extracción automática de información desde Jira, el procesamiento y consolidación de datos en SQL Server, la construcción de indicadores en Power BI y la distribución automática de reportes ejecutivos.

La plataforma transforma actividades manuales y repetitivas en procesos automatizados, permitiendo disponer de información confiable, actualizada y orientada a la toma de decisiones.

---

# 🎯 Objetivo

Automatizar el proceso de captura, transformación, análisis y distribución de información operativa de Mesa de Ayuda, reduciendo tiempos operativos, minimizando errores manuales y mejorando la visibilidad de los indicadores críticos del servicio.

---

# 🏗 Arquitectura de la Solución

```text
Jira
 ↓
Python + Selenium
 ↓
SQL Server
 ↓
Power BI
 ↓
PDF + Correo Ejecutivo
```

---

# ⚙ Componentes Implementados

## 1. Automatización Jira

### Funcionalidades

- Inicio de sesión automatizado.
- Navegación mediante Selenium.
- Ejecución automática de filtros JQL.
- Descarga automática de tickets.
- Exportación CSV.
- Gestión de archivos temporales.
- Reintentos automáticos.
- Registro de logs de ejecución.
- Detección de errores operativos.

### Tecnologías

- Python
- Selenium
- ChromeDriver

---

## 2. Procesamiento y Consolidación de Datos

### Funcionalidades

- Lectura y validación de archivos CSV.
- Transformación de información.
- Homologación de estados.
- Conversión de campos fecha.
- Cálculo de indicadores operativos.
- Integración histórica de tickets.
- Gestión de consistencia de datos.

### Tecnologías

- Python
- SQL Server

---

## 3. Base de Datos Analítica

### Base

```text
TU_BASE_DATOS
```

### Tabla Principal

```text
TU_TABLA_PRINCIPAL
```

### Objetivo

Centralizar el histórico de tickets para análisis operativo y ejecutivo.

---

## 4. Modelo Semántico Power BI

### Componentes

- DimFecha
- DimEstado
- DimAnalistas
- DimTipoIncidencia
- Hecho TU_TABLA_PRINCIPAL
- Medidas

### Relaciones

- Fecha de Creación
- Fecha de Resolución

### Indicadores

- Tickets Totales
- Tickets Recibidos
- Tickets Atendidos
- Tickets Pendientes
- Backlog
- SLA %
- TMR Días
- TMR Horas
- Productividad por Analista

---

# 📊 Dashboards Desarrollados

## Dashboard Ejecutivo MDA

Visualización orientada a gestión operativa y seguimiento diario.

### Indicadores

- Tickets Recibidos
- Tickets Atendidos
- Tickets Pendientes
- SLA
- TMR
- Backlog
- Productividad por Analista

---

## Dashboard Ejecutivo Experis

Versión especializada para seguimiento de tickets gestionados por Experis.

### Indicadores

- Volumen de tickets
- Productividad
- SLA
- TMR
- Backlog
- Tendencias

---

## Dashboard Móvil

Versión optimizada para dispositivos móviles.

### Características

- KPIs principales
- Navegación simplificada
- Diseño responsive

---

# 📈 Indicadores Automatizados

## Operativos

### Tickets

- Recibidos
- Atendidos
- Pendientes
- Backlog

### Calidad

- SLA %
- Cumple SLA
- No Cumple SLA

### Productividad

- Tickets por Analista
- Productividad por Equipo

### Eficiencia

- TMR (Días)
- TMR (Horas)

---

# 📧 Distribución Automática

## Funcionalidades

- Exportación automática Power BI → PDF.
- Captura automática de tendencias.
- Renombrado dinámico.
- Generación de correos HTML.
- Distribución automática.

---

## Contenido del Correo Ejecutivo

### KPIs Ejecutivos

- SLA
- Recibidos
- Atendidos
- Pendientes
- TMR

### Tendencias Operativas

- Total vs Atendidos
- Pendientes
- TMR
- SLA

### KPI por Equipo

- Nivel 2
- Nivel 3
- Experis
- Externos

### Top 10 Tickets Más Antiguos

- Ticket
- Responsable
- Estado
- Días abiertos

### Dashboard Power BI

- Acceso rápido mediante enlace.
- PDF adjunto automáticamente.

---

# 🔄 Automatizaciones Implementadas

## Jira → SQL

Frecuencia:

```text
Cada hora
```

Flujo:

```text
Jira
↓
Exportación CSV
↓
Procesamiento Python
↓
Carga SQL Server
```

---

## Dashboard → PDF

Flujo:

```text
Power BI
↓
Exportación PDF
↓
Renombrado automático
↓
Histórico de reportes
```

---

## Correo Ejecutivo

Flujo:

```text
SQL Server
↓
Consultas KPI
↓
HTML dinámico
↓
PDF
↓
Outlook
↓
Stakeholders
```

---

# ✅ Beneficios Obtenidos

## Operacionales

- Eliminación de tareas manuales.
- Menor tiempo de procesamiento.
- Menor riesgo de error humano.
- Información centralizada.

## Analíticos

- Visibilidad en tiempo real.
- Seguimiento de SLA.
- Seguimiento de backlog.
- Análisis de productividad.

## Ejecutivos

- Reportes automáticos.
- Indicadores consolidados.
- Información disponible para toma de decisiones.

---

# 🛠 Stack Tecnológico

### Desarrollo

- Python
- Selenium

### Base de Datos

- SQL Server

### Analítica

- Power BI Desktop
- Power BI Service
- DAX
- Power Query

### Comunicación

- HTML
- CSS
- Outlook

### Automatización

- Scheduler Python
- Selenium Automation
- Logging Framework

---

# 📌 Estado Actual

## Componentes Productivos

✅ Extracción Jira

✅ Carga SQL Server

✅ Dashboard Ejecutivo

✅ KPI Automáticos

✅ Exportación PDF

✅ Captura de Tendencias

✅ Correo Ejecutivo Automatizado

✅ Históricos de Ejecución

✅ Control de Errores y Logs

---

## Autor

**Gerson Ronaldo Surco Alata**  - www.linkedin.com/in/gerson-ronaldo-surco-alata-53b42026a

---

**Nombre del Proyecto:**

# MDA Automation Hub

_Plataforma Integral de Automatización, Analítica y Distribución de Indicadores para Mesa de Ayuda._

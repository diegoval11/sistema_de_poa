# Sistema de Plan Operativo Anual (POA) – Alcaldía

![Status](https://img.shields.io/badge/Estado-Producción-success)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue?logo=docker)
![Django](https://img.shields.io/badge/Django-5.2-green?logo=django)
![License](https://img.shields.io/badge/Licencia-Privada-red)

Aplicación web empresarial diseñada para la **gestión, seguimiento y auditoría del Plan Operativo Anual (POA)**.

El sistema centraliza la planificación estratégica de la institución, permitiendo a las unidades administrativas definir metas, reportar avances periódicos con evidencias y visualizar el cumplimiento en tiempo real. La solución está **totalmente containerizada**, garantizando un despliegue agnóstico, seguro y escalable.

---

## 🚀 Características Principales

### 📊 Gestión Integral del POA
Administración completa de proyectos, objetivos estratégicos y metas anuales, segmentadas por unidad administrativa y ejercicio fiscal.

### 👥 Control de Acceso Basado en Roles (RBAC)
Sistema de permisos estricto para garantizar la integridad de la información:
* **UNIDAD:** Reporta avances y sube evidencias.
* **ADMINISTRADOR:** Gestiona usuarios, unidades y configuración global.
* **AUDITOR:** Acceso de solo lectura para validación y supervisión.

### 📈 Trazabilidad y Métricas
* Registro de **Avances Mensuales** con cálculo automático de porcentajes de ejecución.
* Alertas visuales de cumplimiento.

### 📁 Gestión de Evidencias
Repositorio digital integrado para respaldar cada reporte de avance mediante archivos (PDF, Imágenes, Docs).

### 🛡️ Auditoría y Seguridad
* **Logs inmutables:** Registro detallado de acciones críticas (quién, cuándo y qué modificó).
* **Protección:** Despliegue seguro tras proxy inverso.

---

## 🛠️ Stack Tecnológico

| Área | Tecnología | Detalles |
| :--- | :--- | :--- |
| **Infraestructura** | ![Docker](https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white) | Docker Compose V2, Nginx (Proxy Inverso) |
| **Backend** | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white) | Django 5.2.8, Gunicorn |
| **Frontend** | ![Tailwind](https://img.shields.io/badge/-Tailwind-38B2AC?logo=tailwind-css&logoColor=white) | HTML5, DaisyUI, JavaScript |
| **Base de Datos** | ![SQLite](https://img.shields.io/badge/-SQLite-003B57?logo=sqlite&logoColor=white) | Persistencia vía Docker Volumes |

---

## 📋 Prerrequisitos del Servidor

Para desplegar en un entorno de producción (**Ubuntu/Debian**), el servidor anfitrión solo requiere:

* **Git**
* **Docker Engine**
* **Docker Compose V2**

> **Nota:** No es necesario instalar Python, Node.js ni gestionar entornos virtuales en el servidor. Todo el entorno de ejecución está aislado en contenedores.

---

## ⚙️ Guía de Despliegue (Producción)

Siga estos pasos para levantar el sistema en un servidor limpio.

### 1. Clonar el Repositorio

```bash
git clone [https://github.com/diegoval11/sistema_de_poa/](https://github.com/diegoval11/sistema_de_poa/)
cd alcaldiaPOA
2. Configuración de Entorno
Cree el archivo de variables de entorno. Este paso es crítico para la seguridad.

Bash

cp .env.example .env
nano .env
⚠️ Atención: Dentro del archivo .env, asegúrese de establecer DEBUG=False y definir una SECRET_KEY robusta y única.

3. Construcción y Ejecución
Compile los estáticos, construya las imágenes y levante los servicios en segundo plano:

Bash

docker compose up -d --build
4. Inicialización de Base de Datos
Ejecute las migraciones para crear la estructura de datos. Este proceso incluye un script automático que genera la Unidad Administrativa (ID=0) requerida por el sistema.

Bash

docker compose exec web python manage.py migrate
5. Creación de Administrador
Genere el primer superusuario para acceder al panel de administración:

Bash

docker compose exec web python manage.py createsuperuser
🔄 Mantenimiento y Operaciones
Comandos útiles para la gestión diaria del servidor.

Ver logs en tiempo real (Depuración):

Bash

docker compose logs -f web
Reiniciar servicios (Tras cambios de configuración):

Bash

docker compose restart
Backup manual de Base de Datos:

Bash

cp db.sqlite3 backups/db_backup_$(date +%Y%m%d).sqlite3
Desarrollado por alumno de ITCA-FEPADE Regional Santa Ana.

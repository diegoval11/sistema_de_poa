# Sistema de Plan Operativo Anual (POA) - Alcaldía

Este proyecto es una aplicación web desarrollada con Django, diseñada para la gestión, seguimiento y auditoría del Plan Operativo Anual (POA) por unidades administrativas.
Permite a las unidades (`poa`) definir metas, planificar actividades y reportar avances, mientras que los roles de `administrador` y `auditor` supervisan y validan la información.

## 🚀 Características Principales

* **Gestión del POA:** Creación y administración de proyectos y objetivos por año.
* **Roles de Usuario:** Sistema de permisos para `UNIDAD`, `ADMINISTRADOR` y `AUDITOR` (definido en `login.Usuario`).
* **Metas y Actividades:** Definición de metas por proyecto y actividades detalladas.
* **Seguimiento Mensual:** Registro de avances (`AvanceMensual`) con cálculo de cumplimiento.
* **Gestión de Evidencias:** Subida de archivos (PDF, Fotos, etc.) para justificar avances.
* **Logs de Auditoría:** Registro de acciones importantes en la plataforma.

## 🛠️ Tecnologías Utilizadas

* **Backend:**
    * Python 3.10+
    * Django 5.2.8
* **Frontend:**
    * HTML5 / CSS3 / JavaScript
    * Tailwind CSS + Daisy UI
* **Base de Datos (Desarrollo):**
    * SQLite 3

## 📋 Prerrequisitos

Para correr este proyecto, necesitarás tener instalado:

* Python 3.10 o superior
* `pip` (manejador de paquetes de Python)
* Node.js y `npm` (para las dependencias de frontend y `node_modules`)
* Git





⚙️ Guía de Instalación: Sistema de POA (alcaldiaPOA)
Sigue estos pasos para configurar y ejecutar el proyecto en tu entorno de desarrollo local.

1. Configuración Inicial (Clonar y Entorno)
Primero, clona el repositorio y configura el entorno virtual de Python.

Bash

# 1. Clona el repositorio y entra a la carpeta
git clone https://github.com/diegoval11/sistema_de_poa/
cd alcaldiaPOA

# 2. Crea el entorno virtual
python -m venv venv

# 3. Activa el entorno virtual
# En Linux/Mac:
source venv/bin/activate

# (O) En Windows (cmd/PowerShell):
.\venv\Scripts\activate
2. Instalación de Dependencias
Instala todos los paquetes necesarios tanto para el backend (Python) como para el frontend (Node.js).

Bash

# 1. Instala las dependencias de Python
pip install -r requirements.txt

# 2. Instala las dependencias de Node.js
npm install
3. Configuración de la Base de Datos
Antes de ejecutar el proyecto, necesitas preparar la base de datos y crear los datos iniciales.

Bash

# 1. Aplica las migraciones de Django para crear las tablas
python manage.py migrate
Importante: El sistema requiere que exista una "Unidad" especial con id=0 antes de poder crear cualquier usuario.

Bash

# 2. Abre la shell de Django
python manage.py shell

# 3. Dentro de la shell (>>>), ejecuta el siguiente código:
from login.models import Unidad
unidad_obj, created = Unidad.objects.update_or_create(
    id=0,
    defaults={
       'nombre': "Unidad Administrativa",
       'activa': True,
       'sin_reporte': True
    }
)

# 4. Escribe 'exit()' y presiona Enter para salir
exit()
Bash

# 5. Ahora sí, crea tu cuenta de superusuario
python manage.py createsuperuser
4. ▶️ Ejecutar el Proyecto
Necesitarás dos terminales separadas (ambas en la carpeta del proyecto) para correr el backend y el frontend simultáneamente.

Terminal 1: Correr el Backend (Django) Asegúrate de tener el (venv) activado

Bash

python manage.py runserver
Terminal 2: Correr el Frontend (Vite/Node)

Bash

npm run dev










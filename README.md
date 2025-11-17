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

## ⚙️ Guía de Instalación Local

Sigue estos pasos para configurar el proyecto en tu entorno local.

**1. Clonar el Repositorio**
```bash
git clone https://github.com/diegoval11/sistema_de_poa/
cd alcaldiaPOA






** Crear el entorno virtual **
python -m venv venv

# Activar el entorno (Linux/Mac)
source venv/bin/activate

# Activar el entorno (Windows)
.\venv\Scripts\activate



**Instalar los requerimentos**
pip install -r requirements.txt


Instalar Dependencias del Frontend
-npm install

-python manage.py migrate


**ANTES DE CREAR UN USUARIO DEBE CREAR SU PRIMERA UNIDAD**
python manage shell
'''
from login.models import Unidad
nombre_unidad = "Unidad Administrativa"
unidad_obj, created = Unidad.objects.update_or_create(
   id = 0
   defaults = {
      'nombre': nombre_unidad,
      'activa':True,
      'sin_reporte':True
}

)
exit()
'''

-python manage.py createsuperuser

-python manage.py runserver


**Correr el frontend con:**
npm run dev













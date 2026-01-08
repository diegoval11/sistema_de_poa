Sistema de Plan Operativo Anual (POA) - Alcaldía
Aplicación web para la gestión, seguimiento y auditoría del Plan Operativo Anual (POA). Permite a las unidades administrativas definir metas y reportar avances, facilitando la supervisión por parte de administradores y auditores.

El sistema está containerizado con Docker para un despliegue rápido, seguro y escalable en servidores de producción (Ubuntu/Linux).

Características Principales
Gestión del POA: Creación y administración de proyectos y objetivos anuales.

Roles Jerárquicos: Sistema de permisos para UNIDAD, ADMINISTRADOR y AUDITOR.

Trazabilidad: Registro de avances (AvanceMensual) con cálculo automático de cumplimiento.

Evidencias: Carga de archivos (PDF, Imágenes) para justificar los reportes.

Logs de Auditoría: Registro inmutable de acciones críticas.

🛠️ Stack Tecnológico
Infraestructura: Docker & Docker Compose (Nginx + Gunicorn).

Backend: Python 3.10+ / Django 5.2.8.

Frontend: Tailwind CSS + Daisy UI (Servido vía Nginx/WhiteNoise).

Base de Datos: SQLite 3 (Persistente vía Volúmenes Docker).

Prerrequisitos del Servidor
Para desplegar este proyecto en un servidor Ubuntu, solo necesitas:

Docker Engine y Docker Compose V2.

Git.

No es necesario instalar Python, Node.js o pip en el sistema anfitrión, ya que todo corre dentro de los contenedores.

⚙️ Guía de Despliegue (Producción con Docker)
Sigue estos pasos para levantar el proyecto en un servidor limpio.

1. Clonar el Repositorio
Bash

git clone https://github.com/diegoval11/sistema_de_poa/
cd alcaldiaPOA
2. Configurar Variables de Entorno
Crea un archivo .env en la raíz del proyecto. Esto es crucial para la seguridad en producción.

Bash

cp .env.example .env
nano .env
Asegúrate de cambiar DEBUG=False y establecer una SECRET_KEY segura y única.

3. Construir y Levantar Contenedores
Este comando compilará el frontend, preparará el backend y levantará el servidor Nginx (Proxy Inverso).

Bash

docker compose up -d --build
(El flag -d ejecuta los contenedores en segundo plano).

4. Inicialización de la Base de Datos
Una vez los contenedores estén corriendo, ejecuta las migraciones. Este paso crea las tablas y automáticamente configura la Unidad Administrativa inicial (ID=0) necesaria para el sistema.

Bash

docker compose exec web python manage.py migrate
5. Crear Superusuario
Para acceder al panel de administración y gestionar las unidades, crea tu usuario administrador:

Bash

docker compose exec web python manage.py createsuperuser
Comandos Útiles de Mantenimiento
Ver logs del servidor (para depuración):

Bash

docker compose logs -f web
Reiniciar el sistema (tras cambios en código):

Bash

docker compose restart
Hacer backup de la base de datos (SQLite):

Bash

cp db.sqlite3 db_backup_$(date +%Y%m%d).sqlite3
--Notas sobre la Arquitectura Docker
Este despliegue utiliza un Proxy Inverso (Nginx) configurado automáticamente en el docker-compose.yml:

Nginx recibe las peticiones del puerto 80.

Sirve los archivos estáticos optimizados.

Protege y redirige el tráfico dinámico hacia el contenedor de Django (Gunicorn).

# Django Template

Este proyecto contiene un template de Django con las siguientes funcionalidades:

- ABM de usuarios
- Login utilizando token JWT

## Pasos a seguir una vez clonado el proyecto.

- Cambiar en project/apps.py ProjectConfig por <nombre proyecto>Config y el name = 'project' por name = 'nombre proyecto'
- Cambiar nombre de carpeta "project" por el nombre del proyecto
- Cambiar en server/settings.py todas las ocurrencias de "project" por el nombre del proyecto
- Cambier en server/settings.py el usuario y nombre de la base de datos

### Base de datos

Una vez hechos todos los cambios, correr el archivo deploy/mydql-db-create.sh 

`./mysql-db-create.sh dbname dbuser dbpass`

Para crear la base de datos. Puede ser que sea necesario hacer el script ejecutable

`chmod +x mysql-db-create.sh`

### Instalar librerias

`sudo apt-get install mysql-server`
`sudo apt-get install libmysqlclient-dev`
`pip3 install -r requirements.txt`

### Migraciones

Es necesario crear las migraciones default de Django. Para eso, se corren los siguientes comandos

`python3 manage.py makemigrations`

Deberia crear el archivo de migracion inicial (chequear que exista en <nombre del proyecto>/migrations/0001_initial.py)

Y luego aplicar la migración a la base

`python3 manage.py migrate`

### Correr el proyecto

En este punto ya se deberia poder levantar el servidor con el comando

`python3 manage.py runserver`


### Crear usuario admin

`python3 manage.py createsuperuser`

Este comando crea un usuario admin el cual podemos usar para acceder en localhost:8000/admin
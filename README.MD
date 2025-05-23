Step 1: Download the Project
- git clone https://github.com/b2k4rys/task
- cd olx

Step 2: Set Up the Project

Create a virtual env
- python -m venv env

Activate (on mac)
- source env/bin/activate

Install dependencies
- pip install -r requirements.txt

Configure the Database
- psql -U postgres
- CREATE DATABASE myproject_db;

Create a .env file in the olx folder: (on Mac)
- touch .env 

Open .env and add 
DB_NAME=myproject_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432

Replace your_postgres_password with your PostgreSQL password.

Initialize the Database:
- python manage.py migrate


Step 3: Launch the Project
- python manage.py runserver
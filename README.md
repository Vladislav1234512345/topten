### Step by step instruction to run the project

***

**Step-1:**
```shell
# Copying project on local
git clone https://github.com/Vladislav1234512345/topten .
```

***

**Step-2:**

Creating all dependencies:
1) Creating env_files and certs directories:

```shell
mkdir certs env_files
```

2) Creating files inside env_files directory:

```shell
touch certs/.env.db certs/.env.email certs/.env.tasks
```

3) Filling files in env_files directory:

* Filling a ".env.db" file:
```text
POSTGRES_USER=<username>
POSTGRES_PASSWORD=<password>
POSTGRES_HOST=<host>
POSTGRES_PORT=<port>
POSTGRES_DB=<database_name>
```

* Filling a ".env.email" file:
```text
EMAIL_NAME=<email_address>
EMAIL_APP_PASSWORD=<email_app_password>
```
Google email app password you can create here: https://myaccount.google.com/apppasswords

* Filling a ".env.tasks" file:
```text
REDIS_HOST=<host>
REDIS_PORT=<port>
RABBITMQ_HOST=<host>
RABBITMQ_PORT=<port>
```

4) Making rsa private and public keys:

Read certs/README.md file with instruction how to create rsa keys

***

**Step-3:**
```shell
# Install all requirements
pip install -r requirements.txt
```

***

**Step-4:**
```shell
# Run the redis
docker run --name redis --rm -p 6379:6379 redis
```

***

**Step-5:**
```shell
# Run the rabbitmq
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:4.0-management
```

***

**Step-6:**
```shell
# Run the celery
celery -A tasks worker --loglevel=INFO --pool=solo
```

***

**Step-7:**
```shell
# Run the project
python main.py
```

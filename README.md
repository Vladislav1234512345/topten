### Step by step instruction to run the project

***

**Step-1:**
```shell
# Copying project on local
git clone https://github.com/Vladislav1234512345/topten .
```

***

**Step-2:**
```shell
# Creating env_files directory with files
git clone https://github.com/Vladislav1234512345/topten .
```

***

**Step-2:**
```shell
# Install all requirements
pip install -r requirements.txt
```

***

**Step-3:**
```shell
# Run the redis
docker run --name redis --rm -p 6379:6379 redis
```

***

**Step-4:**
```shell
# Run the rabbitmq
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:4.0-management
```

***

**Step-5:**
```shell
# Run the celery
celery -A tasks worker --loglevel=INFO --pool=solo
```

***

**Step-6:**
```shell
# Run the project
python main.py
```

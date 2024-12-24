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
# Run the project
python main.py
```


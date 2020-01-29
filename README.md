# Test project for testing people
## Run
1) Up project `docker-compose up --build`
2) Add data to db (if you first start project)
```
docker-compose exec app sh
python init_db.py
```
Project bind to TCP 8080 port.  
User and admin user can pass tests.  
Admin user can add test, questions and answers.
## Login like admin
**email**: `alex@gmail.com`  
**password**: `123456`  
## Moments need to be finalized
1) **Session must be saved to Redis.** Now we have statefull service because we save session to Cookie Storage. But we need stateless service.
2) **App must work with semaphore.** If we have many requests, our app can use all RAM and exit.
3) **Update validation requests.** Views have simple validators now. But this validation not full complete.

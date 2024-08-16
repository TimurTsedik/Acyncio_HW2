### REST API Built on an Asynchronous Engine with User Password Hashing

### 1. Starting the Containers

docker-compose up --build

After starting the containers, our server application will be available at http://127.0.0.1:5001,
and the PostgreSQL database will be accessible at localhost:5431.

### 2. Running the Client

python3 client.py

### 3. Reading the Logs

Read the logs to see what actions the server performed in response to the requests.

# Cloud-Based File Storage System

## Deployment
We deploy the system with Docker and Docker Compose. Using Compose, we define the multi-container stack and connect Locust, Grafana, and Prometheus to Nextcloud. By editing docker-compose.yml, you can swap the database backend and modify Nextcloud settings.

To run the docker containers just go to the directory that contains the docker-compose.yml file and run the following command:
```
docker-compose up -d
```






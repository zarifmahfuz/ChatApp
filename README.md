# ChatApp
Simple multiparty chat application based on websockets

# Build

## Requirements

The Chat Application will be hosted on your local host! All you need to install is [Docker Engine](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/).

## Run

Ensure that your docker engine is running. From the top level directory of this git repository run the following command:

``` 
docker-compose up -d
```

This command will build the images of all the application services and it will launch all the services.

To stop the application and delete all the containers:
```
docker-compose down
```

To temporarily stop the application, but keep the containers and their associated data:
```
docker-compose stop
```

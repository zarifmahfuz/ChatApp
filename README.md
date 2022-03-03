# ChatApp
This is a socket-based multi-threaded chat application. 

<img src="https://github.com/zarifmahfuz/ChatApp/blob/main/docs/demo1.gif" width="1000" height="500" />


# Build

## Requirements

The Chat Application will be hosted on your local host! All you need to install is [Docker Engine](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/).

## Run

Ensure that your docker engine is running. From the top level directory of this git repository run the following command:

``` 
docker-compose up -d
```

This command will build the images of all the application services and it will launch all the services. Once you have your containers running, you want to start the server and client applications. 

To start the server, login to the server container as follows and run the server program.

```
docker exec -it chat_app_websocket /bin/sh
python3 server.py 5200
```

After this, login to the client container and start the client program(s).

```
docker exec -it chat_app_client /bin/sh
python3 client.py 5200
```

You can launch as many client programs as you want as this is a multi-party chat application.

To stop the application and delete all the containers:
```
docker-compose down
```

To temporarily stop the application, but keep the containers and their associated data:
```
docker-compose stop
```


# Design

## Architecture

The following diagram shows a high-level architecture of the application components.

<img src="https://github.com/zarifmahfuz/ChatApp/blob/main/docs/design/infra.jpg" width="405" height="370" />

- When a client starts the application, it talks to the web service to authenticate user credentials, join new rooms or view older messages. The webserver exposes REST APIs to the client to allow this to happen.
- When the client requests to join a chat room, it talks to the websocket server. The websocket server executes a handshake protocol to identify the client. Upon identification, the websocket server lets the client into the requested chat room by launching a dedicated thread for the client.
- The websocket server has a dedicated thread for each client, performing socket I/O. This allows the websocket server to achieve concurrency by interleaving I/O operations with CPU operations.
- The websocket server broadcasts the chat room's messages in real-time to all the clients present in the chat room.
- The websocket server also stores all chat messages into the database.

I built this application to be scalable. So, my implementation of the websocket and webserver can be scaled up and distributed across several nodes.

## Class Diagram

If you want to look at a more lower level details, check out my [objected-oriented design](https://github.com/zarifmahfuz/ChatApp/blob/main/docs/design/oop.jpg) of the application.

## References

This project wouldn't be possible without these valuable information resources.
1. https://towardsdatascience.com/ace-the-system-interview-design-a-chat-application-3f34fd5b85d0
2. http://faculty.salina.k-state.edu/tim/NPstudy_guide/servers/chat_background.html


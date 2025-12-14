# data_handler

## Real-time Monitoring and Data Ingestion System

### About This Project

This project demonstrates a **scalable architectural pattern** for efficiently managing data ingestion via **HTTP API requests** in a **Django (ASGI)** environment, while enabling **real-time monitoring** through WebSockets.

The core objective is a clean **separation of concerns** to maximize performance, scalability, and future extensibility:

- **Fast acceptance of API requests** handled by the ASGI server (Daphne)
- **Asynchronous processing and optimized storage** using Celery and a Lazy Insertion strategy
- **Real-time monitoring** of incoming data events via WebSockets

---

## Key Features

### API (HTTP) Ingestion
Data is ingested through standard HTTP API endpoints exposed by Django.

### PostgreSQL Backend
Configured to use **PostgreSQL** as the primary database for reliable, scalable, and production-grade data persistence.

### Background Processing with Celery
All heavy processing and storage operations are immediately delegated to **Celery workers**, keeping API response times minimal.

### WebSocket Notification System (Monitoring-Only)

- Celery dispatches notifications upon data arrival
- Notifications are sent through **WebSockets**
- Designed strictly for **real-time monitoring**

This approach ensures a clean architectural boundary and leaves room for future **authentication and authorization** mechanisms in the notification layer.

### Optimized Database Usage (Lazy Insertion)
Implements a **Lazy Insertion** mechanism to queue and batch incoming data, enabling efficient asynchronous inserts and reducing database transaction overhead.

### ASGI Architecture
Uses **Daphne** to manage HTTP requests and WebSocket connections under a unified ASGI-based architecture.

---

## Setup and Installation
> **Note:** In both Docker and manual setups, the repository must be cloned first.
### Option A: Run with Docker (Recommended)

The easiest way to run the entire stack is using Docker and Docker Compose.
> **Note:** You should create .env file from env.sample file

#### Prerequisites

- Docker
- Docker Compose

#### Clone the Repository

```bash
git clone https://github.com/parsaferdosi/data_handler.git
cd data_handler
```

#### Run

On **Windows**:

```bash
docker-compose up --build
```

On **Linux / macOS**:

```bash
docker compose up --build
```

Docker Compose will automatically start:

- PostgreSQL
- Redis
- Django (ASGI + Daphne)
- Celery Worker
- Celery Beat

---

### Option B: Manual Setup (Local Development)

### 1. Clone the Repository

```bash
git clone https://github.com/parsaferdosi/data_handler.git
cd data_handler
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Prerequisites

This project relies on the following services:

- **Database (PostgreSQL)**  
  Ensure a PostgreSQL instance is running and Django database settings are configured correctly.

- **Message Broker (Redis)**  
  Celery workers are fully dependent on **Redis** as the message broker. The Redis service must be running before starting Celery.

---

## How to Run and Observe Monitoring (Manual Mode)

To run the complete system without Docker, start each component in a **separate terminal**.

### 1. Start the Celery Worker

Responsible for background processing, Lazy Insertion, and WebSocket notifications.

```bash
celery -A data_handler worker -l info
```

### 2. Start Celery Beat Scheduler

Required for executing periodic tasks, such as committing queued data to the database.

```bash
celery -A data_handler beat -l info
```

### 3. Start the ASGI Server (Daphne)

Runs the Django application in ASGI mode to handle HTTP requests and WebSocket connections.

```bash
daphne data_handler.asgi:application
```

---

## Initial Application Setup

Before running the demo client, a Django superuser must be created.
> **Note:** This section is separate from the project setup.
> For instructions on how to connect to a Docker container shell, please refer to the Docker documentation.


Create a superuser with the following credentials:

- **Username:** `parsa`
- **Password:** `admin`

```bash
python manage.py createsuperuser
```

---

## Run the Demo Client

After the system is fully running and the superuser is created, execute the demo client:

```bash
python demo.py
```

### Observation

Once all components are running, data sent by `demo.py` will trigger:

- Background processing via Celery
- Lazy insertion into the database
- Real-time monitoring notifications delivered through WebSockets

---

## Contributing

Contributions are welcome. To contribute:

1. Fork the repository
2. Create a new feature branch
3. Commit your changes
4. Submit a Pull Request

---

## License

This project is released under the **MIT License**.

---

**Author**  
Parsa Ferdosi Zade

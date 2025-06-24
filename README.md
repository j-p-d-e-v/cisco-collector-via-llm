# Cisco Router Command Executor (LLM-Powered)

This proof of concept demonstrates how a Large Language Model (LLM) can be used to:

- **Collect logs** by executing show commands on a Cisco router.
- **Configure interfaces** remotely using natural language prompts.

---

## 🧪 Sample Prompts

### 🔍 Log Collection
```
Collect show clock, show route ipv4, show arp, show run interface, and show version from sandbox-iosxr-1.cisco.com with username admin and password mypassword
```

### 🔧 Configure Interface Description
```
Configure Loopback1 interface description to "hello cisco ai 123" of sandbox-iosxr-1.cisco.com with username admin and password mypassword
```

---

## 🚀 How to Run

### 🔧 Prerequisites
- Docker

---

### ⚙️ Setup

1. **Create `.env` File**

   Copy and modify the sample:
   ```sh
   cp .env.sample .env
   ```

   Example `.env` content:
   ```env
   LLM_BASE_URL=http://yourllmapi:8000
   SANDBOX_HOST=10.0.0.1
   SANDBOX_USERNAME=admin
   SANDBOX_PASSWORD=myrouterpassword
   SANDBOX_PORT=22
   ```

2. **Start the Docker Container**
   ```sh
   docker-compose up -d
   ```

3. **Get the Container ID**
   ```sh
   docker ps
   ```

4. **Access the Container**
   ```sh
   docker exec -it <container_id> bash
   ```

5. **Install Python Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

### Running via CLI

1. **Access the Container**
   ```sh
   docker exec -it <container_id> bash
   ```
2. **Run the Cli Script**
   ```sh
   python cli.py
   ```


## Web Based

### Running API Server

1. Launch the FastAPI dev server
```
fastapi dev api.py --host 0.0.0.0 --port 80
```
2. Since the container port 80 is mapped to host OS port 7080. Open your browser, then go to:
```
http://localhost:7080/docs
```
3. You can Swagger to send prompt.
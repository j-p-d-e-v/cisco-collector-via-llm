# Cisco Router Command Executor (LLM-Powered)

This proof of concept demonstrates how a Large Language Model (LLM) can be used to:

- **Collect logs** by executing show commands on a Cisco router.
- **Configure interfaces** remotely using natural language prompts.

---

## 🧪 Sample Prompts

### 🔍 Log Collection
```
Collect show clock, show route ipv4, show arp, show run interface, and show version from sandbox-iosxr-1.cisco.com with username admin and password C1sco12345
```

### 🔧 Configure Interface Description
```
Configure Loopback1 interface description to "hello cisco ai 123" of sandbox-iosxr-1.cisco.com with username admin and password C1sco12345
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

6. **Run the Main Script**
   ```sh
   python main.py
   ```
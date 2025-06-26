FROM python:3.12-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y curl npm && \
    apt-get clean

# Use Node 20 via NVM (Node Version Manager)
ENV NVM_DIR=/root/.nvm
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && \
    . "$NVM_DIR/nvm.sh" && \
    nvm install 20 && \
    nvm use 20 && \
    nvm alias default 20 && \
    npm install -g npm

# Ensure Node and NPM are available in PATH
ENV PATH="$NVM_DIR/versions/node/v20/bin:$PATH"

# Copy rest of the app (assuming there's a Python backend too)
WORKDIR /app
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt
# Default command (optional)
CMD ["bash"]

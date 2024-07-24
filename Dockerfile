# Start a new build stage
FROM python:3.12-slim

# Install gnupg
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        gnupg \
 && rm -rf /var/lib/apt/lists/*

# Install .NET SDK and Runtime
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        curl \
 && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
 && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
        dotnet-runtime-6.0 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Set working directory for Python code
WORKDIR /backend

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the assets directory into the Docker image
COPY app/assets /app/assets
COPY . .
COPY start.sh /start.sh

# Make the script executable
RUN chmod +x /start.sh

# Expose the port FastAPI runs on
EXPOSE 8000

# Run the application using the start script
CMD ["/start.sh"]
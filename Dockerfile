FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy dependency list
COPY requirements.txt /tmp/requirements.txt

# Install Python packages
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Start container with bash shell
CMD ["bash"]
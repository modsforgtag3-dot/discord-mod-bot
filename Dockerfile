# Use a lightweight Python image
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Copy project files into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port for the Flask companion app
EXPOSE 5000

# Start both apps
CMD ["./start.sh"]

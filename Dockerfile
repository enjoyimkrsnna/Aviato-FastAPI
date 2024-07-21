# Use the official Python image from the Docker Hub
FROM python:3.11-alpine

# Set the working directory in the container
WORKDIR /app

# Install build dependencies for Python packages
RUN apk add --no-cache gcc musl-dev libffi-dev

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . /app/

# Expose the port the FastAPI app runs on
EXPOSE 8000

# Run the FastAPI app using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

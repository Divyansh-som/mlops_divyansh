# 1. Base Image: Choose the operating system and language runtime
FROM python:3.9-slim

# 2. Working Directory: Set up where your files will live inside the container
WORKDIR /app

# 3. Cache Management: Copy dependencies file first to speed up future builds
COPY requirements.txt .

# 4. Install Dependencies: Run the setup command inside the container
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy Application: Bring the rest of your local source code into the container
COPY . .

# 6. Network Configuration: Expose the port your application listens on
EXPOSE 8000

# 7. Runtime Command: The command that executes when the container starts
CMD ["python", "app.py"]
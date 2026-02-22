# 1. specify the  Python version
FROM python:3.11-slim

# 2. Set the working directory to match the project
WORKDIR /app

# 3. Copy the requirements file
COPY requirements.txt .

# 4. Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy  entire project(Auratrack) into the container
COPY . .

# 6. Expose the port Django uses
EXPOSE 8000

# 7. Start the server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

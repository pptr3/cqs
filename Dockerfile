# pull official base image
FROM python:3.11.2-slim-buster

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy only requirements.txt initially
COPY requirements.txt .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy the rest of the application code
COPY . .

# set the PYTHONPATH to include /app
ENV PYTHONPATH="/app"

# expose the port that the FastAPI app runs on
EXPOSE 8000

# command to run the FastAPI app with uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

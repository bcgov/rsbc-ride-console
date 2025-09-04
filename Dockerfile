#
# Build the frontend
#
FROM node:20.19.2-alpine AS frontend

# Build Frontend
COPY /frontend /app
WORKDIR /app
RUN npm ci && npm run build

#
# Build the app
#
FROM python:3.12-alpine AS app
RUN apk update && apk upgrade --no-cache
# Build App
COPY requirements.txt /python/requirements.txt
# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /python/requirements.txt
COPY /app /python/app
COPY --from=frontend /app/dist /python/app/static_content
WORKDIR /python

# Expose port
EXPOSE 3000

# Run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]


#
# Build the frontend
#
FROM docker.io/node:20.19.2-alpine AS frontend
ENV NO_UPDATE_NOTIFIER=true

# Build Frontend
COPY . /app
WORKDIR /app
RUN npm ci && npm run build

#
# Create the final container image
#

FROM artifacts.developer.gov.bc.ca/dbe7-images/ubi8-nginx120:1.0
ARG VERSION
ENV VERSION=$VERSION
COPY nginx.conf /app/nginx.conf
WORKDIR /app
COPY --from=frontend /app/dist /app/build
# COPY dist /app/dist

CMD ["nginx", "-c", "/app/nginx.conf",  "-g", "daemon off;"]

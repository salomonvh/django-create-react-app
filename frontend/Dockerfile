# Frontend Dockerfile (CRA)

ARG NODE_VERSION=18-alpine
FROM node:${NODE_VERSION} as base

WORKDIR /app/frontend

# Install dependencies separately for better caching
COPY frontend/package*.json ./
RUN npm ci

# Copy source
COPY frontend/ .

# Default command suitable for development
CMD ["npm", "start"]

# Build stage for production assets
FROM base as build
RUN npm run build


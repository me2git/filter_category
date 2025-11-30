# Frontend Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files (use frontend/ prefix for cloud deployment)
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy application code from frontend directory
COPY frontend/ .

# Expose port
EXPOSE 3000

# Set environment variables
ENV CHOKIDAR_USEPOLLING=true
ENV WATCHPACK_POLLING=true

# Start development server
CMD ["npm", "start"]

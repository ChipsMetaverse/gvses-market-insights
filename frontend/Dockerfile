FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Cache bust for debug logging deployment - v1.2 (minify: false)
# Build the application
RUN npm run build

# Install serve to serve static files
RUN npm install -g serve

# Expose port 8080 (Fly.io default)
EXPOSE 8080

# Serve the built files on port 8080
CMD ["serve", "-s", "dist", "-l", "8080"]

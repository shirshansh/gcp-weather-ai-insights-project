# ---------- Stage 1: Build the React App ----------
FROM node:18 AS builder

# Set working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json first (cache optimization)
COPY package*.json ./

# Install dependencies
RUN npm install --silent

# Copy all source code
COPY . .

# Build the React app
RUN npm run build

# ---------- Stage 2: Serve with Nginx ----------
FROM nginx:stable-alpine

# Copy React build output into Nginx's web root
COPY --from=builder /app/build /usr/share/nginx/html

EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
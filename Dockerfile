# Use a lightweight Node image
FROM node:18-alpine

# Set working dir
WORKDIR /app

# Copy dependency info and install
COPY package*.json ./
RUN npm install

# Copy the rest of your site
COPY . .

# Listen on all interfaces so Docker publishes correctly
CMD ["npm", "start", "--", "--host", "0.0.0.0"]

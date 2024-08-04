FROM oven/bun:1.1
# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json ./
COPY bun.lockb ./

# Install dependencies
RUN bun install

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 3000

# Command to run the application
ENTRYPOINT ["bun", "run", "src/api/index.ts"]

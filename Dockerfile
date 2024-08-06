FROM oven/bun:1.1

ENV WEBHOOK_URL ""

# Install Linux dependencies
RUN apt-get update && apt-get install -y python3 python3-dev

RUN apt-get install -y python3-pip

# Check pip version
RUN pip3 --version

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json ./
COPY bun.lockb ./
COPY requirements.txt ./

# Install Node dependencies
RUN bun install

# Install python dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 3000

# Command to run the application
ENTRYPOINT ["bun", "run", "start"]

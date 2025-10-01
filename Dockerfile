FROM python:3.12-bullseye

# Create and set permissions for the bot directory
RUN mkdir /bot && chmod 755 /bot
WORKDIR /bot

RUN DEBIAN_FRONTEND=noninteractive apt-get update -qq && \
    apt-get install -y --no-install-recommends \
    git wget pv jq python3-dev ffmpeg fontconfig && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies first (better caching)
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy remaining files
COPY . .

# Run the bot
CMD ["python", "bot.py"]

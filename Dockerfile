
FROM python:3.8.5

WORKDIR /bowling

# Copy python dependencies
COPY requirements.txt .

# Install debian build dependencies if needed
RUN apt-get update && apt-get install -y \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev \
    libasound-dev \
    libsndfile1-dev \
    python3-dev \
    build-essential \
    libgl1-mesa-glx \
    libglu1-mesa

# Update pip and install python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY position_tracker ./position_tracker
COPY models ./models
COPY images ./images
COPY config ./config
COPY ble ./ble
COPY main ./main

# Change wd for correct entry point
WORKDIR /bowling/main

CMD ["python", "main.py", "-ds"]

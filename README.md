# RTSP-streamer

Starts an RTSP server, using opencv and gstreamer.
Implementation improved from: <https://github.com/prabhakar-sivanesan/OpenCV-rtsp-server>

## Install gstreamer and related plugins

```bash
sudo apt-get install -y \
    libgirepository1.0-dev \
    libcairo2-dev \
    gir1.2-gtk-3.0 \
    python3-gi \
    python3-gi-cairo \
    libgstreamer1.0-0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-tools \
    gstreamer1.0-x \
    gstreamer1.0-alsa \
    gstreamer1.0-gl \
    gstreamer1.0-pulseaudio \
    gstreamer1.0-rtsp \
    libglib2.0-dev \
    libgstrtspserver-1.0-dev
```

## Setup virtual environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running

Make the script executable:

```bash
chmod +x run_streams.sh
```

### Finally run the script

```bash
./run_streams.sh
```

This should run 4 vehicle and 2 pedestrian streams.

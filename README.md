# Robot Face Animation with Live Audio Visualization

An interactive web-based robot face animation that responds to live audio input through WebSocket connections and Cloudflare tunnels. Features two different face designs (Emo and Steve) with real-time audio analysis visualization.

## Project Overview

- **`server.py`** - Main Python backend: Captures audio, performs FFT analysis, streams data via WebSocket
- **`start_robot.py`** - Automation script: Starts servers, creates Cloudflare tunnels, updates HTML files with live URLs
- **`find_devices.py`** - Utility: Lists available audio input devices to find correct device index
- **`index.html`** - Emo robot face UI with animated eyes and mouth
- **`steve.html`** - Steve robot face UI (bald design) with additional expressions

## Prerequisites

### System Requirements
- **Python 3.8+**
- **Windows, macOS, or Linux**
- **Active internet connection** (for Cloudflare tunnels)
- **Microphone/Audio input device**

### Required External Tools

#### 1. **Cloudflared CLI** (Required for Tunneling)
This is NOT a Python package - it must be installed separately.

**Windows:**
```bash
# Download from Cloudflare
# https://pkg.cloudflare.com/cloudflared-release/windows/amd64/cloudflared-windows-amd64.exe
# Or use PowerShell:
choco install cloudflare-warp
# Or use scoop:
scoop install cloudflared
```

**macOS:**
```bash
brew install cloudflare/cloudflare/cloudflared
```

**Linux:**
```bash
wget https://github.com/cloudflare/cloudflared/releases/download/2024.1.0/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
```

Verify installation:
```bash
cloudflared --version
```

## Installation

### Step 1: Install Python Dependencies

#### On Windows (PyAudio Issues):
PyAudio can be tricky on Windows. Try one of these approaches:

**Option A: Using pre-compiled wheels (Recommended)**
```bash
python -m pip install --only-binary :all: -r requirements.txt
```

**Option B: Using pipwin**
```bash
pip install pipwin
pipwin install pyaudio
pip install websockets numpy
```

**Option C: WSL2 or Linux**
Install Windows Subsystem for Linux and use the Linux approach below.

#### On macOS:
```bash
# Install PortAudio first
brew install portaudio
pip install -r requirements.txt
```

#### On Linux:
```bash
# Install PortAudio development files
sudo apt-get install portaudio19-dev python3-dev
pip install -r requirements.txt
```

### Step 2: Find Your Audio Device Index

Before running the automation, identify which audio device to use:

```bash
python find_devices.py
```

**Example Output:**
```
--- Available Audio Input Devices ---
Index 0: Microphone (USB Audio)
Index 3: Stereo Mix
Index 5: Line In
```

**Note the index of your microphone.** If you need to change it, edit `server.py` line 11:
```python
AUDIO_INDEX = 3  # Change this number to your device index
```

## Usage

### Quick Start

```bash
python start_robot.py
```

This will:
1. Launch the Python audio backend
2. Create a WebSocket tunnel (port 7000)
3. Create an HTTP tunnel (port 8000)
4. Display the public URL to access from your tablet/browser
5. Automatically inject tunnel URLs into HTML files

**Output example:**
```
=== Robot Face Auto-Starter ===

Starting local backend (server.py)...
[OK] Audio Stream is live at: wss://xyz123.trycloudflare.com
[OK] Webpage Tunnel is live at: https://abc789.trycloudflare.com

==================================================
🎉 ALL SYSTEMS GO! 🎉
==================================================
Open this exact link on your Android tablet browser:

👉  https://abc789.trycloudflare.com  👈

Press Ctrl+C in this window to shut everything down cleanly.
```

### Manual Server Running

If you prefer to run servers separately:

**Terminal 1 - Start the audio server:**
```bash
python server.py
```
- Listens on `ws://localhost:7000` for WebSocket connections
- Serves HTTP on `http://localhost:8000`

**Terminal 2 - Open in browser:**
```bash
# Local access
http://localhost:8000

# For remote access, create your own tunnels:
cloudflared tunnel --url http://127.0.0.1:8000
cloudflared tunnel --url http://127.0.0.1:7000
```

## Features

### Audio Analysis
- **Real-time audio capture** from selected device
- **Volume detection** (RMS calculation)
- **Frequency analysis** (FFT) for low and mid-range frequencies
- **Live streaming** via WebSocket

### UI Controls

Both HTML interfaces provide:
- **Fullscreen** - Toggle fullscreen mode
- **Face Switch** - Toggle between Emo and Steve designs
- **Eye Shape** - Toggle between Squircle and Circle eye shapes
- **Audio Sliders** - Manual control for Volume, Low Freq, Mid Freq
- **Blink Interval** - Adjust how often the robot blinks
- **Animation Toggle** - Enable/disable facial animations

### Animation Features
- Responsive eye tracking to audio
- Realistic blinking behavior
- Breathing animation
- Dynamic mouth movement
- Expression variety (smile, open mouth, etc.)

## Troubleshooting

### PyAudio Installation Fails on Windows
```
ERROR: Could not find a version that satisfies the requirement pyaudio
```

**Solution:**
```bash
# Method 1: Download pre-compiled wheel
pip install pipwin
pipwin install pyaudio

# Method 2: Use only binary distributions
python -m pip install --only-binary :all: pyaudio

# Method 3: Alternative audio library
pip uninstall pyaudio
pip install sounddevice
# Then modify server.py to use sounddevice
```

### "cloudflared: command not found"
**Solution:**
- Download from: https://pkg.cloudflare.com/cloudflared-release
- Add to PATH or run with full path
- Verify: `cloudflared --version`

### No Audio Devices Found
**Solution:**
1. Check audio input is enabled in system settings
2. Run `python find_devices.py` to verify devices
3. Try a different AUDIO_INDEX value
4. Check system audio settings aren't muted

### WebSocket Connection Failed
**Possible causes:**
- `server.py` not running
- Firewall blocking ports 7000 or 8000
- Invalid cloudflared URL (copy exact URL from output)
- Browser doesn't support WebSocket (use modern browser)

**Solution:**
```bash
# Test if server is running
netstat -an | findstr :7000   # Windows
lsof -i :7000                 # macOS/Linux

# Restart server
python server.py
```

### HTML Not Updating with New URLs
**Solution:**
- Ensure HTML files are in the same directory as `start_robot.py`
- Check file permissions (should be writable)
- Look for error message in console output
- Manually update `wsUrl` in HTML if needed

## Configuration

### Audio Settings (in `server.py`)
```python
AUDIO_INDEX = 3        # Audio device index
WS_PORT = 7000        # WebSocket port
HTTP_PORT = 8000      # HTTP server port
CHUNK = 1024          # Samples per buffer
RATE = 44100          # Sample rate (Hz)
CHANNELS = 1          # Mono audio
```

### Network Configuration
- **Local**: Change port numbers if conflicts exist
- **Remote**: Cloudflare tunnels auto-generate URLs (public/temporary)

## File Structure

```
Project/
├── server.py              # Audio backend & WebSocket server
├── start_robot.py         # Automation launcher
├── find_devices.py        # Audio device lister
├── index.html             # Emo robot face interface
├── steve.html             # Steve robot face interface
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Requirements

See `requirements.txt`:
- **websockets** (14.1+) - WebSocket server/client
- **pyaudio** (0.2.13+) - Audio capture
- **numpy** (1.24.4+) - Audio analysis & FFT

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: No module named 'pyaudio'` | PyAudio not installed | Run `pip install -r requirements.txt` |
| `Port 7000 already in use` | Another process using port | Change `WS_PORT` in `server.py` |
| Cloudflare tunnel appears stuck | Network issue | Press Ctrl+C, wait 5s, retry |
| No audio detected | Wrong AUDIO_INDEX | Run `find_devices.py` |
| Websocket fails on tablet | Wrong URL copied | Copy exact URL from `start_robot.py` output |

## Development

### Adding New Faces
1. Create new `face.html` with same WebSocket structure
2. Update `start_robot.py` to include in `update_html_file()` calls
3. Add navigation button in existing HTML files

### Modifying Audio Analysis
Edit these sections in `server.py`:
- **Lines 45-50**: FFT frequency boundaries
- **Lines 51-53**: Frequency range summation
- **Lines 54-57**: State object sent to WebSocket

### Customizing UI
Edit CSS in HTML files:
- Sidebar colors: `#controls` background
- Button styles: `.ui-btn` class
- Slider appearance: `.ui-slider` class

## Performance Notes

- **WebSocket sent every 10ms** (100 updates/second)
- **Audio latency**: ~23ms per buffer (1024 samples @ 44.1kHz)
- **Total E2E latency**: ~40-50ms typical
- **CPU usage**: ~5-15% on modern systems

For lower latency, reduce `CHUNK` size (trade-off: noisier analysis)

## License & Attribution

This project uses:
- **Cloudflare Warp**: Free tunnel service for remote access
- **numpy**: Scientific computing
- **websockets**: Real-time communication

## Support

For issues:
1. Check Troubleshooting section above
2. Verify all prerequisites installed
3. Check file permissions (Python files should be readable)
4. Test with `find_devices.py` first
5. Run `python server.py` separately to debug

---

**Last Updated:** February 2026
**Tested On:** Windows 10+, macOS 11+, Ubuntu 20.04+

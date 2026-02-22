# 🤖 Real-Time AI Robot Face Lip-Sync

A low-latency, real-time web interface that animates a robot face based on system audio. This project captures audio from an AI assistant (like Gemini) running on your PC, analyzes the volume and frequency in real-time, and streams the mouth movements to a mobile tablet over the internet using WebSockets and Cloudflare Tunnels.

## ✨ Features
* **Real-Time Audio Analysis:** Uses Fast Fourier Transform (FFT) in Python to calculate dynamic mouth shapes based on volume and frequency.
* **Dual Faces:** Seamlessly switch between a 2D "Squircle/Emo" face and a 3D blocky "Steve" face.
* **Network Automation:** Automatically spins up Cloudflare Quick Tunnels to bypass local network restrictions and browser security blocks (fixes Android screen-sleeping issues).
* **Zero-Config Frontend:** The Python launcher automatically injects the secure WebSocket URL into the HTML files on startup and cleans them up on exit.

---

## 🛠️ Prerequisites & Setup

### 1. Python 3
Download and install [Python](https://www.python.org/downloads/). 
* **CRITICAL:** During installation, ensure you check the box that says **"Add Python.exe to PATH"**.

### 2. Cloudflare Tunnel CLI (`cloudflared`)
This securely exposes your local servers to the internet so your tablet can connect.
1. Download the Windows installer from the [Cloudflare Tunnel Downloads page](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/).
2. Install it. It runs silently in the background and adds itself to your system PATH.

---

## 🎛️ Detailed Audio Routing (VB-Audio Virtual Cable)



To make the mouth move without causing feedback loops from your main microphone, you must route the AI's voice through a virtual cable. 

**Step 1: Installation**
1. Download [VB-Cable](https://vb-audio.com/Cable/).
2. Extract the ZIP file completely (do not run the installer from inside the ZIP).
3. Right-click `VBCABLE_Setup_x64.exe` and select **"Run as Administrator"**.
4. Click "Install Driver" and **reboot your computer** when finished.

**Step 2: Route Your Browser to the Virtual Cable**
We need to force your browser (running Gemini) to output sound to the virtual cable instead of your main speakers.
1. Open your browser and play some audio (like a YouTube video or Gemini speaking).
2. Open Windows Settings -> **System** -> **Sound**.
3. Scroll down to **Volume mixer**.
4. Find your browser in the list of apps.
5. Change its **Output device** from "Default" to **CABLE Input (VB-Audio Virtual Cable)**.
*(Note: You will suddenly stop hearing the browser. This is normal and expected!)*

**Step 3: Hear the AI and Let Python Listen**
We need to send that virtual audio back to your physical speakers so you can hear it, while Python listens to it simultaneously.
1. Open Windows Settings -> **System** -> **Sound**.
2. Scroll down and click **More sound settings** (this opens the classic Sound Control Panel).
3. Click the **Recording** tab.
4. Right-click **CABLE Output** and select **Properties**.
5. Go to the **Listen** tab.
6. Check the box for **"Listen to this device"**.
7. In the dropdown menu below it, select your physical Bluetooth speaker or headphones.
8. Click Apply and OK.

---

## 📦 Project Installation

### 1. Install Dependencies (`requirements.txt`)
Create a new text file named `requirements.txt` in your project folder and paste these exact lines inside it:
```text
pyaudio
numpy
websockets
python-dotenv

```

Open your terminal in the project folder and run this command to install them all at once:

```bash
pip install -r requirements.txt

```

If pyaudio download failed. Try this:

```bash
python -m pip install pyaudio
```

### 2. Find Your Audio Device Index

The Python script needs to know which "microphone" to listen to. Run the device finder script:

```bash
python find_devices.py

```

Look through the terminal output for **CABLE Output (VB-Audio Virtual Cable)** and note its **Index Number** (e.g., `Index 2`).

### 3. Setup the `.env` File

Create a file named exactly `.env` in your project folder and paste the following, replacing `2` with your actual device index from the previous step:

```env
# The PyAudio index number of your VB-Cable Output
AUDIO_INDEX=2

# Network Ports
WS_PORT=7000
HTTP_PORT=8000

```

---

## 🚀 Running the Project

1. Double-click the `start.bat` file (or run `python start_robot.py` in your terminal).
2. The automation script will:
* Start the audio listener.
* Spawn two secure Cloudflare tunnels.
* Inject the secure WebSocket URL into both HTML files.


3. Look at the terminal output for the **final link** (it will look like `https://random-words.trycloudflare.com`).
4. Type that exact link into the browser on your Android tablet or phone.
5. Tap **"Connect to Backend"** to wake up the face!

*(To shut everything down cleanly, simply press `Ctrl+C` in the terminal window. This will automatically revert your HTML files back to local testing URLs and close the tunnels.)*

---

## ⚠️ Troubleshooting

* **Tablet says "Error: Cannot connect to Python backend"**
Make sure `cloudflared` is properly installed and accessible in your system PATH.
* **The face isn't moving when the AI speaks**
1. Check the terminal window. If "Volume:" is printing `0.00`, your audio routing is incorrect. Double-check your Windows Volume Mixer settings.
2. If the terminal shows volume spikes but the face doesn't move, check the **"Noise Gate"** slider in the tablet's sidebar UI. Lower the threshold until the face reacts.


* **Tablet screen goes to sleep**
Ensure you are accessing the UI using the secure `https://` link provided by the Cloudflare script. Modern browsers disable the Wake Lock API on insecure local IP addresses.

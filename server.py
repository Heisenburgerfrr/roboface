import asyncio
import websockets
import pyaudio
import numpy as np
import json
import http.server
import socketserver
import threading

AUDIO_INDEX = 3  # Audio device index (run find_devices.py to list available devices)
WS_PORT = 7000 # WebSocket port for audio data
HTTP_PORT = 8000 # We will use port 8000 for the webpage

# --- AUDIO SETTINGS ---
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100 

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=AUDIO_INDEX, 
                frames_per_buffer=CHUNK)

# --- HTTP SERVER SETUP ---
def start_http_server():
    Handler = http.server.SimpleHTTPRequestHandler
    # Serve files from the current directory
    with socketserver.TCPServer(("", HTTP_PORT), Handler) as httpd:
        print(f"--> Webpage hosted at: http://localhost:{HTTP_PORT}")
        httpd.serve_forever()

# --- WEBSOCKET AUDIO ANALYZER ---
async def audio_analyzer(websocket):
    print("Tablet/Browser connected to audio stream!")
    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            normalized_data = audio_data / 32768.0
            rms = np.sqrt(np.mean(normalized_data**2))
            volume = float(rms * 100)

            fft_data = np.abs(np.fft.rfft(normalized_data))
            scaled_fft = np.clip(fft_data * 10, 0, 255)

            lowSum = np.sum(scaled_fft[3:11])
            midSum = np.sum(scaled_fft[11:31])
            
            lowAvg = float(lowSum / 8)
            midAvg = float(midSum / 20)

            state = {"v": volume, "l": lowAvg, "m": midAvg}
            await websocket.send(json.dumps(state))
            await asyncio.sleep(0.01) 
            
    except websockets.exceptions.ConnectionClosed:
        print("Tablet/Browser disconnected.")

# --- MAIN LOOP ---
async def main():
    # 1. Start the HTTP server in the background
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()

    # 2. Start the WebSocket server
    print(f"--> Audio Stream active on port {WS_PORT}")
    async with websockets.serve(audio_analyzer, "0.0.0.0", WS_PORT):
        await asyncio.Future()  

if __name__ == "__main__":
    asyncio.run(main())
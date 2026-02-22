import pyaudio

p = pyaudio.PyAudio()

print("--- Available Audio Input Devices ---")
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    # We only care about devices that can capture audio (inputs)
    if dev.get('maxInputChannels') > 0:
        print(f"Index {i}: {dev.get('name')}")

p.terminate()
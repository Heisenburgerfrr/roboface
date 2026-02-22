import subprocess
import re
import time
import sys

def get_cloudflare_url(port, name):
    print(f"Starting {name} tunnel (Port {port})...")
    
    # Launch cloudflared silently in the background
    process = subprocess.Popen(
        ['cloudflared', 'tunnel', '--url', f'http://127.0.0.1:{port}'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    url = None
    # Cloudflare prints the generated URLs to the 'stderr' stream
    for line in process.stderr:
        match = re.search(r'(https://[a-zA-Z0-9-]+\.trycloudflare\.com)', line)
        if match:
            url = match.group(1)
            break
            
    return process, url

def update_html_file(filename, wss_url):
    """Helper function to cleanly inject the URL into any HTML file."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            html_content = file.read()
            
        # This regex finds the exact wsUrl line and replaces it
        updated_html = re.sub(
            r"const\s+wsUrl\s*=\s*['\"`].*?['\"`];", 
            f"const wsUrl = '{wss_url}';", 
            html_content
        )
        
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(updated_html)
        print(f"[OK] {filename} updated successfully.")
        return True
    except FileNotFoundError:
        print(f"Error: {filename} not found! Make sure it is in the same folder.")
        return False

def main():
    print("=== Robot Face Auto-Starter ===\n")
    
    # 1. Start your Python backend
    print("Starting local backend (server.py)...")
    server_process = subprocess.Popen([sys.executable, 'server.py'])
    time.sleep(2) # Give the audio engine a second to warm up
    
    # 2. Start the WebSocket Tunnel (Port 7000)
    ws_process, ws_url = get_cloudflare_url(7000, "WebSocket")
    if not ws_url:
        print("Error: Could not get WebSocket URL. Is cloudflared installed properly?")
        server_process.kill()
        return
        
    print(f"[OK] Audio Stream is live at: {ws_url}")
    
    # 3. Automatically rewrite BOTH HTML files
    wss_url = ws_url.replace("https://", "wss://")
    print(f"Injecting new URL into HTML files...")
    
    # Update index.html AND steve.html
    if not update_html_file('index.html', wss_url) or not update_html_file('steve.html', wss_url):
        print("Failed to update HTML files. Shutting down.")
        server_process.kill()
        ws_process.kill()
        return

    # 4. Start the HTTP Webpage Tunnel (Port 8000)
    http_process, http_url = get_cloudflare_url(8000, "Webpage")
    if not http_url:
        print("Error: Could not get HTTP Cloudflare URL.")
        server_process.kill()
        ws_process.kill()
        return
        
    print(f"[OK] Webpage Tunnel is live at: {http_url}")
    
    # 5. Display the final result
    print("\n" + "="*50)
    print("🎉 ALL SYSTEMS GO! 🎉")
    print("="*50)
    print("Open this exact link on your Android tablet browser:")
    print(f"\n👉  {http_url}  👈\n")
    print("You can now seamlessly switch between faces using the UI buttons!")
    print("Press Ctrl+C in this window to shut everything down cleanly.")
    print("="*50)
    
    try:
        # Keep the script running so the tunnels don't close
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down servers and tunnels... Goodbye!")
        server_process.kill()
        ws_process.kill()
        http_process.kill()

if __name__ == "__main__":
    main()
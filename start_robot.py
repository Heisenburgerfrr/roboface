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
            found_url = match.group(1)
            # Ignore Cloudflare's internal background links
            if "api.trycloudflare.com" not in found_url and "update.trycloudflare.com" not in found_url:
                url = found_url
                break
            
    return process, url

def update_html_file(filename, wss_url):
    """Helper function to cleanly inject the URL into any HTML file."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            html_content = file.read()
            
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
    
    server_process = None
    ws_process = None
    http_process = None
    
    try:
        # 1. Start your Python backend
        print("Starting local backend (server.py)...")
        server_process = subprocess.Popen([sys.executable, 'server.py'])
        time.sleep(2) 
        
        # 2. Start the WebSocket Tunnel (Port 7000)
        ws_process, ws_url = get_cloudflare_url(7000, "WebSocket")
        if not ws_url:
            print("Error: Could not get WebSocket URL.")
            return
            
        print(f"[OK] Audio Stream is live at: {ws_url}")
        
        # 3. Automatically rewrite BOTH HTML files
        wss_url = ws_url.replace("https://", "wss://")
        print(f"Injecting new URL into HTML files...")
        
        if not update_html_file('index.html', wss_url) or not update_html_file('steve.html', wss_url):
            print("Failed to update HTML files.")
            return

        # 4. Start the HTTP Webpage Tunnel (Port 8000)
        http_process, http_url = get_cloudflare_url(8000, "Webpage")
        if not http_url:
            print("Error: Could not get HTTP Cloudflare URL.")
            return
            
        print(f"[OK] Webpage Tunnel is live at: {http_url}")
        
        # 5. Display the final result
        print("\n" + "="*50)
        print("🎉 ALL SYSTEMS GO! 🎉")
        print("="*50)
        print("Open this exact link on your Android tablet browser:")
        print(f"\n👉  {http_url}  👈\n")
        print("Press Ctrl+C in this window to shut everything down cleanly.")
        print("="*50)
        
        # Keep the script running so the tunnels don't close
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down servers and tunnels...")
        
    finally:
        # --- THIS BLOCK ALWAYS RUNS ON EXIT ---
        print("\nReverting HTML files back to local WebSocket URL...")
        update_html_file('index.html', 'ws://localhost:7000')
        update_html_file('steve.html', 'ws://localhost:7000')
        
        if server_process: server_process.kill()
        if ws_process: ws_process.kill()
        if http_process: http_process.kill()
        
        print("Cleanup complete. Goodbye!")

if __name__ == "__main__":
    main()
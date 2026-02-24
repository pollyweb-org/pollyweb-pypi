import argparse
import socket

def listen(port=8000):
    print(f"Listening for inbound messages on port {port}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", port))
        s.listen(1)
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                data = conn.recv(4096)
                if data:
                    print(f"Received: {data.decode(errors='replace')}")
                else:
                    print("Connection closed by peer.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Listen for inbound messages.")
    parser.add_argument("port", type=int, nargs="?", default=8000, help="Port to listen on")
    args = parser.parse_args()
    listen(args.port)

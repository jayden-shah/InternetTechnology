import random
import socket


ASSIGNED_PORT = 30037
SERVER_HOST = "0.0.0.0"


def server():
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("[S]: Server socket created")
    except OSError as err:
        print(f"[S]: Socket open error: {err}")
        return

    try:
        server_socket.bind((SERVER_HOST, ASSIGNED_PORT))
        server_socket.listen(1)
        print(f"[S]: Server host is {SERVER_HOST}")
        print(f"[S]: Server port is {ASSIGNED_PORT}")

        client_socket, client_address = server_socket.accept()
        print(f"[S]: Got a connection request from {client_address}")
        with client_socket:
            receive_buffer = b""
            for chunk in iter(lambda: client_socket.recv(4096), b""):
                receive_buffer += chunk
                records = receive_buffer.split(b"\n")
                receive_buffer = records.pop()

                for request_bytes in records:
                    try:
                        request = request_bytes.decode("utf-8")
                        line_number, message = request.split("|", 1)
                        int(line_number)
                    except (UnicodeDecodeError, ValueError):
                        print(f"[S]: Ignoring malformed request: {request_bytes!r}")
                        continue

                    transformed = message[::-1].swapcase()
                    actual_length = len(transformed.encode("utf-8"))
                    if random.random() < 0.10:
                        reported_length = actual_length + random.randint(1, 1000)
                    else:
                        reported_length = actual_length

                    response = (
                        f"{line_number}|{reported_length}|{transformed}\n"
                    )
                    client_socket.sendall(response.encode("utf-8"))

            if receive_buffer:
                print(f"[S]: Ignoring unterminated request: {receive_buffer!r}")
    except OSError as err:
        print(f"[S]: Server error: {err}")
    finally:
        server_socket.close()


if __name__ == "__main__":
    server()

"""CS 352 Project 1 starter client, separated from proj.py."""

import socket
import sys

ASSIGNED_PORT = 30037
SERVER_HOST = sys.argv[1] if len(sys.argv) > 1 else "localhost"

def client():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[C]: Client socket created")
    except OSError as err:
        print(f"[C]: Socket open error: {err}")
        return

    try:
        client_socket.connect((SERVER_HOST, ASSIGNED_PORT))
        with open("in-proj.txt", "r") as infile, open("out-proj.txt", "w") as outfile:
            receive_buffer = b""
            for line_number, line in enumerate(infile, 1):
                message = line.rstrip('\r\n')
                request_str = f"{line_number}|{message}\n"
                client_socket.sendall(request_str.encode("utf-8"))
                print(f"[C]: Data sent to server: {message}")

                record_bytes = None
                while b"\n" not in receive_buffer:
                    chunk = client_socket.recv(4096)
                    if not chunk:
                        break
                    receive_buffer += chunk
                if b"\n" in receive_buffer:
                    record_bytes, receive_buffer = receive_buffer.split(b"\n", 1)

                if record_bytes is None:
                    print(f"[C]: Server closed before responding to line {line_number}")
                    break
                try:
                    response = record_bytes.decode("utf-8")
                    parts = response.split("|", 2)
                    if len(parts) != 3:
                        raise ValueError("response must contain three fields")
                    recv_line_num, reported_len, transformed_msg = parts
                    recv_line_num = int(recv_line_num)
                    reported_len = int(reported_len)
                except (UnicodeDecodeError, ValueError) as err:
                    print(
                        f"[C]: Malformed response for line {line_number}: {err}"
                    )
                    continue

                print(f"[C]: Data received from server: {transformed_msg}")
                actual_len = len(transformed_msg.encode("utf-8"))

                if recv_line_num == line_number and reported_len == actual_len:
                    outfile.write(f"{recv_line_num}|{reported_len}|{transformed_msg}\n")
                else:
                    print(
                        f"[C]: Invalid response for line {line_number}: "
                        f"returned line {recv_line_num}, reported length "
                        f"{reported_len}, actual length {actual_len}"
                    )
                    outfile.write(
                        f"{line_number}|ERROR|reported-length={reported_len}|"
                        f"actual-length={actual_len}\n"
                    )
    except OSError as err:
        print(f"[C]: Client error: {err}")
    finally:
        client_socket.close()


if __name__ == "__main__":
    client()

"""CS 352 Project 1 starter client, separated from proj.py."""

import socket


ASSIGNED_PORT = 30037
SERVER_HOST = "127.0.0.1"


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
                
                record_found = False
                while not record_found:
                    if b'\n' in receive_buffer:
                        record_bytes, receive_buffer = receive_buffer.split(b'\n', 1)
                        parts = record_bytes.decode("utf-8").split('|', 2)
                        
                        if len(parts) == 3:
                            recv_line_num, reported_len, transformed_msg = parts
                            reported_len = int(reported_len)
                            actual_len = len(transformed_msg.encode("utf-8"))
                            
                            if int(recv_line_num) == line_number and reported_len == actual_len:
                                outfile.write(f"{recv_line_num}|{reported_len}|{transformed_msg}\n")
                            else:
                                outfile.write(f"{line_number} | ERROR | reported-length={reported_len} | actual-length={actual_len}\n")
                        record_found = True
                    else:
                        chunk = client_socket.recv(4096)
                        if not chunk:
                            break
                        receive_buffer += chunk
    except OSError as err:
        print(f"[C]: Client error: {err}")
    finally:
        client_socket.close()


if __name__ == "__main__":
    client()

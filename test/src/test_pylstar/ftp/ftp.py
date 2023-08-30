from socket import *
import os
import sys
import bcrypt
import traceback

BUFFER_SIZE = 1024

# Authorized users -----------------------------------------------------
global users
users = dict()
users["admin"] = bcrypt.hashpw("password".encode('utf8'), bcrypt.gensalt())

# Create contained folder if inexistant & CD TO FOLDER --------------
root_dir = './confined_folder'
if not os.path.exists(root_dir):
    os.mkdir(root_dir)

os.chdir(root_dir)

# We save the abs path of the confined_folder (the cwd) in order
# to be able to tell later if the users tries to go outsite this 
# folder when he uses CD command.
global CONFINED_FOLDER_ABSPATH
CONFINED_FOLDER_ABSPATH = os.getcwd()

# Functions --------------------------------------------------------

def is_path_in_confined_folder(path):
    """ Return true if the directory path is a subpath of the confined folder """

    return CONFINED_FOLDER_ABSPATH in os.path.abspath(path)


def PWD():
    """ Return the current work directory """

    abs_path_cwd = os.getcwd()
    relative_path = os.path.relpath(abs_path_cwd, start=CONFINED_FOLDER_ABSPATH)
    return relative_path


def CD(path):
    """return True if authorized, False otherwise"""

    # check if the requested path is authorized
    if not is_path_in_confined_folder(path):
        return False
    # if path is not a dir
    elif not os.path.isdir(path):
        print(f"[ERR_CD] {path} is not a dir")
        return False
    # change directory
    try:
        os.chdir(path)
        return True
    except FileNotFoundError:
        print("[CHDIR] File not found")
        return False
    except Exception as e:
        print("[CHDIR_ERR] =>", e)
        return False


def LIST():
    """ Return a string containing all files in the CWD """

    output = ''
    for files in os.listdir(os.getcwd()):
        if os.path.isdir(files):
            output += files + '/\n'
        else:
            output += files + '\n'
    return output


def SEND_FILE(client_socket, filepath):
    """ Send the following to client:
    "SENDING:<filename>__<filesize>:END_METADATA<file_content>:END_SENDING"

    Return True if the file is sent successfully.
    """

    # Check if the requested file is in the confined folder
    if not is_path_in_confined_folder(filepath):
        client_socket.send("ERR: Unauthorized path.\n".encode("utf8"))
        return False
    
    # Check if the requested path is a file
    if not os.path.isfile(filepath):
        client_socket.send(f"ERR: '{filepath}' is not a file.\n".encode("utf8"))
        return False
    
    # Send file
    try :
        # get metadata
        filename = os.path.basename(filepath)       # '../file.txt' => 'file.txt'
        filesize = os.path.getsize(filepath)

        # get file content 
        f = open(filepath, "rb")
        file_content = f.read()
        f.close()

        # construct sending message 
        metadata = f"SENDING:{filename}__{filesize}:END_METADATA".encode("utf8")
        data = file_content + b":END_SENDING"
        package = metadata + data

        # send to client
        q, r = len(package) // BUFFER_SIZE, len(package) % BUFFER_SIZE
        for i in range(q):
            client_socket.sendall(package[i:i+BUFFER_SIZE])
        client_socket.sendall(package[-r:])
        return True

    except Exception as e:
        print("[ERR_SEND] =>", e)
        client_socket.send(f"ERR: '{filepath}' is not a file.\n".encode("utf8"))
        return False


def RECEIVE_FILE(client_socket):
    """ Receive a file from the client.
    1) Send "REVEIVING" to client
    2) Wait for "SENDING:<filename>__<filesize>:END_METADATA<file_content>:END_SENDING"
       if "ERR" is received, cancel.
    
    Return True if upload successful. False otherwise.
    """

    # confirm to client he can send the file...........
    client_socket.send(b"RECEIVING")

    # receiving data ...................................
    bytes_received = client_socket.recv(BUFFER_SIZE)

    if b"ERR" in bin_message:
            return False

    while b":END_SENDING" not in bytes_received:
        bytes_received += client_socket.recv(BUFFER_SIZE)

    # extract metadata
    idx_end_metadata = bytes_received.find(b":END_METADATA") + len(":END_METADATA")
    metadata = bytes_received[len('SENDING:'):idx_end_metadata - len(':END_METADATA')]
    filename, filesize = metadata.decode("utf8").split('__')
    print(filename, filesize)

    # ectract file content
    data = bytes_received[idx_end_metadata:-len(":END_SENDING")]

    # Security check, if the filename is sth like ".../../file.ext"
    # We make sure that the file will be in the confined folder
    if not is_path_in_confined_folder(os.path.abspath(filename)):
        client_socket.send("ERR: Unauthorized path.\n".encode("utf8"))
        return False

    # write file
    f = open(filename, "wb")
    f.write(data)
    f.close()

    # check if file is entirely received
    if os.path.getsize(filename) == int(filesize):
        print(f"File {filename} received.")
        client_socket.sendall(f"File {filename} uploaded.".encode("utf8"))
        return True
    else:
        client_socket.sendall(f"File {filename} was not uploaded.".encode("utf8"))
        os.remove(filename)
        return False
    

# Check user parameters ------------------------------------------------

if len(sys.argv) != 5:
    print ("Usage: ./prog  -h <host> -p 21")
    sys.exit()

if sys.argv[1] != "-h":
    print(f"Invalid parameter: {sys.argv[2]}")
    print ("Usage: ./prog  -h <host> -p 21")
    sys.exit()

if sys.argv[3] != "-p":
    print(f"Invalid parameter: {sys.argv[3]}")
    print ("Usage: ./prog  -h <host> -p 21")
    sys.exit()

if sys.argv[4] != "21":
    print(f"Invalid port: {sys.argv[4]}")
    print ("Usage: ./prog  -h <host> -p 21")
    sys.exit()


# Create socket ----------------------------------------------------

server = socket(AF_INET, SOCK_STREAM)
server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

try:
    host, port = sys.argv[2], int(sys.argv[4])
    address = (host, port)
    server.bind(address)
except Exception as e:
    print (f"Exception: {str(e)}")
    server.close()
    sys.exit()

# start listening -------------------------------------------------

server.listen(1)

while True:

    # accept connexion --------------------------------------------
    print(f"[TCP] Waiting for connection on {address[0]} : {address[1]}")
    client, client_address = server.accept()
    print(f"[OK] Connexion established with {client_address}")

    # authentification  --------------------------------------------
    try:
        # client.send("Username: ".encode("utf8"))
        received_data = client.recv(BUFFER_SIZE)
        username = received_data.decode("utf8").strip('\n')

        # client.send("Password: ".encode("utf8"))

        if username in users.keys():
            # compare hash
            client.send("Enter Password".encode("utf8"))
            received_data = client.recv(BUFFER_SIZE)
            bin_password = received_data.decode("utf8").strip('\n').encode("utf8")
            hash = users[username]
            if bcrypt.hashpw(bin_password, hash) == hash:
                client.send(f"Welcome {username} !\n".encode("utf8"))
                print(f"[LOG] User '{client_address}' logged in as '{username}'")
            else:
                client.send("ERR: Wrong login".encode("utf8"))
                print(f"[END] Connexion ended with {client_address}")
                client.close()
        else:
            client.send("ERR: Wrong login".encode("utf8"))
            print(f"[END] Connexion ended with {client_address}")
            client.close()

    except BrokenPipeError:
        client.close()
    except Exception as e:
        print("[ERR_AUTH] =>", e)
        client.close()
    
    # ftp ---------------------------------------------------

    while True:
        try:
            # will generate an error if not authentified (socket closed)
            # client.send(f"\n{PWD()}/$ ".encode("utf8"))
            bin_message = client.recv(BUFFER_SIZE)
            message = bin_message.decode("utf8").strip('\n')
            print(f"Command received : {message}")
        
            # "PWD" ...............................................

            if message == "PWD":
                client.send("{}/ \n".format(PWD()).encode("utf8"))

            # "CD <path>" ........................................
            # check if at least one arg and a space between CD and the arg

            elif message[0:3] == "CD " and len(message.split("CD ")) == 2: 
                path = message.split("CD ")[1]
                if not CD(path):
                    client.send("ERR: File not found or unauthorized.\n".encode("utf8"))

            # "LIST" ...............................................

            elif message == "LIST":
                resultat = LIST()
                client.send(resultat.encode("utf8"))

            # "GET <file_path>"......................................

            elif message[0:3] == "GET" and len(message.split("GET ")) == 2:
                filepath = message.split("GET ")[1]
                if SEND_FILE(client, filepath):
                    # we dont want to send any data before the file is downloaded from client
                    print("[WAIT] Waiting for any message from client before continue...")
                    client.recv(BUFFER_SIZE)
                    print("[OK] Waiting for commands...")

            # "PUT"...................................................

            elif message == "PUT":
                RECEIVE_FILE(client)
            
            # "HELP"...................................................

            elif message == "HELP":
                help = "\nPWD - Display current work directory\n" + \
                            "CD <path> - Change directory (do not use \" \" for files with spaces)\n" +\
                            "LIST - List all files in cwd\n" + \
                            "GET <path> - Download file\n" + \
                            "PUT - Upload file. Follow the instructions.\n" + \
                            "HELP - Display this message\n" + \
                            "QUIT - Disconnect from server\n"
                client.send(help.encode("utf8"))

            # "QUIT" ..................................................

            elif message == "QUIT":
                client.close()
                print(f"[END] Connexion ended with {username}")
                # Returning to confined folder directory (in case CD where made by users)
                CD(CONFINED_FOLDER_ABSPATH)
                break

            # NO COMMAND ..................................................

            else:
                client.send("ERR: Invalid/Unknown command.Please retry.\n".encode("utf8"))

        except KeyboardInterrupt:
            print("Quitting...")
            client.close()
            server.close()
            sys.exit()
        except ConnectionResetError:
            client.close()
            break
        except Exception as e:
            traceback_output = traceback.format_exc()
            print("[ERROR_RECV] =>", e)
            print(traceback_output)
            client.close()
            break

server.close()
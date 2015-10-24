from threading import Thread
import socket
import time

IP_BASE = "141.37.168."
TCP_IP = '141.37.168.38'
TCP_PORTS = [i for i in range(50000, 50006)]
BUFFER_SIZE = 1024
NICK = input("Please enter nickname: ")

localPort = -1
localIp = ""

quit_flag = False

from threading import Lock
connectedSocketsMutex = Lock()
connectedSockets = []
nick2sock = {}
sock2nick = {}


def getchar():
    #Returns a single character from standard input
    try:
        import sys, tty, termios

        fd = sys.stdin.fileno()
        # save original terminal settings
        old_settings = termios.tcgetattr(fd)

        # change terminal settings to raw read
        tty.setraw(sys.stdin.fileno())

        ch = sys.stdin.read(1)

        # restore original terminal settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    except:
        import msvcrt
        return msvcrt.getch()


# Function add buddy
def addBuddy(nickname, sock):
    if nickname in nick2sock.keys():
        sockTmp = nick2sock[nickname]
        del sock2nick[sockTmp]
        connectedSockets.remove(sockTmp)
    nick2sock[nickname] = sock
    sock2nick[sock] = nickname


def delBuddy(nickname):
    sock=getSockByNick(nickname)
    del nick2sock[nickname]
    del sock2nick[sock]
    return


def getNickBySock(sock):
    return sock2nick[sock]


def getSockByNick(nick):
    return nick2sock[nick]

def isBuddyInList(nick):
    if nick in nick2sock:
        return True
    return False

def addConnectedSocket(sock, nick):
    # this function is thread safe
    global connectedSocketsMutex
    global connectedSockets

    connectedSocketsMutex.acquire()
    addBuddy(nick, sock)
    connectedSockets.append(sock)
    connectedSocketsMutex.release()

# API
def scan():
    threads = []

    for portNo in TCP_PORTS:
        for i in range(1,255):
            ip_addr = IP_BASE + str(i)
            if (ip_addr == TCP_IP and portNo == localPort):
                # skip the addr:port for this instance
                # also clients hosts which are connected already
                continue
            thread = Thread(target=scanPort,args=(ip_addr,portNo,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

def listNicks():
    global nick2sock
    print("Nickname\t| Adresse\t\t| Port")
    for nick in nick2sock.keys():
        print(nick + "\t\t| " + nick2sock[nick].getpeername()[0] + "\t\t| " + str(nick2sock[nick].getpeername()[1]))

def chat():
    global nick2sock
    counter = 0
    chatpartners = []
    print("Choose chat partner:\n")
    print("Nickname")
    for nick in nick2sock.keys():
        print("[" + str(counter) + "] " + nick)
        chatpartners.append(nick)
        counter += 1
    chatpartner=input('Enter number of chat partner:'+'\n')
    message=input('Enter chat message:'+'\n')
    conn = getSockByNick(chatpartners[int(chatpartner)])
    conn.send(("\\start " + message + " \\end\n").encode('utf-8'))


def groupChat():
    message=input('Enter group-chat message:'+'\n')
    for nick in nick2sock.keys():
        conn = getSockByNick(nick)
        conn.send(("\\all " + message + " \\end\n").encode('utf-8'))

def listenForNewIngoingConnections():
    global localPort

    socketOpen = False
    i = 0

    while not socketOpen:
        if i >= len(TCP_PORTS):
            # if all available ports in use already
            print("ERROR: All available ports in use already!")
            import os
            os._exit(os.EX_UNAVAILABLE)

        portNo = TCP_PORTS[i]
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((TCP_IP, portNo))
            socketOpen = True
            localPort = portNo
        except OSError as e:
            i += 1  # if port is in use already, try next port

    print("")
    print("Listening on port " + str(portNo) + "\r")
    print("")

    while True:
        # get nick of remote and answer with my nick
        sock.listen(1)
        conn, addr = sock.accept()
        conn.send(("\\myNick " + NICK + "\n").encode('utf-8'))

        data = conn.recv(BUFFER_SIZE)
        remoteNick = data.decode('utf-8').rstrip()[9:]  # remove trailing "\getNick "

        if isBuddyInList(remoteNick) is False:
            print("<Info> Buddy " + remoteNick + " joined the chat!")
        addConnectedSocket(conn, remoteNick)


def listen(sock):
    BUFFER_SIZE = 1024
    sock.settimeout(0.01)

    try:
        data = sock.recv(BUFFER_SIZE)
    except socket.timeout:
        sock.close()
        return

    handleData(sock, data)

import select
def retrieveData():
    global quit_flag
    global connectedSockets

    while True and not quit_flag:
        while not quit_flag:
            if len(connectedSockets) == 0:
                # no clients connected
                time.sleep(0.01)
                break

            try:
                readyToRead, readyToWrite, inError = \
                   select.select(
                      connectedSockets,
                      connectedSockets,
                      connectedSockets,
                      100)
            except:
                continue

            time.sleep(0.02)

            # iterate over all sockets and retrieve data
            for sock in readyToRead:
                try:
                    data = sock.recv(BUFFER_SIZE)
                    handleData(sock, data)
                except socket.timeout:
                    continue
                except OSError as e:
                    if e.errno == 107:
                        # Transport endpoint is not connected
                        print(e)
                    else:
                        print(str(e))


def handleData(sock, data):
    global connectedSocketsMutex
    global connectedSockets

    if not data:
        return

    data = data.decode('utf-8')
    splitData = data.split()
    command = splitData[0][1:]
    message = data[len("\\" + command + " "):].rstrip().lstrip()
    #print("data:", data + "\r")
    #print("cmd :", command + "\r")
    #print("message:", message + "\r")

    if command == "myNick":
        addConnectedSocket(sock, message)
    elif command == "start":
        nick = getNickBySock(sock)
        if message.endswith("\\end"):
            message = message[:-4].rstrip()
        print("<private> " + nick + ": " + message + "\r")
    elif command == "quit":
        nick = getNickBySock(sock)
        print("<Info> Buddy " + str(nick) + " left chat!\r")
        delBuddy(nick)
    elif command == "all":
        nick = getNickBySock(sock)
        if message.endswith(" \\end"):
            message = message[:-5]
        print("<all> " + nick + ": " + message)


def scanPort(destIp, portNo):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.01)
    try:
        s.connect((destIp, portNo))
        thread = Thread(target=listen,args=(s,))
        thread.start()
        s.send(("\getNick " + NICK).encode("utf-8"))
        thread.join()
    except socket.error as msg:
        pass


def info():
    print("\nAvailable Options: ")
    print("i (info)       : print this info")
    print("s (scan)       : Scan for open connection")
    print("l (list)       : Output Buddy-list")
    print("c (chat)       : Send message to a buddy")
    print("g (group chat) : Send group-message")
    print("q (quit)       : End application", "\r")


def shortInfo():
    print("\nAvailable Options: i (info), s (scan), l (list), c (chat), g (group chat), q (quit)\n")

def quit():
    global quit_flag
    quit_flag = True

    for nick in nick2sock.keys():
        conn = getSockByNick(nick)
        conn.send(("\\quit\n").encode('utf-8'))
        conn.close()

    try:
        retrieveThread.join()
    except NameError:
        pass

# Main
def main():
    global retrieveThread

    listenForNewIngoingConnectionsThread = Thread(target=listenForNewIngoingConnections)
    listenForNewIngoingConnectionsThread.start()

    retrieveThread = Thread(target=retrieveData)
    retrieveThread.start()

    info()
    scan()

    while(True):
        print("")
        shortInfo()

        key = getchar()
        if type(key) == str:
            key_decoded = key
        else:
            key_decoded = key.decode("utf-8", "ignore")
        if key_decoded == "q" or key == b'\x03' or key == '\x03':
            print("INFO: Leaving...")
            quit()
            print("INFO: Offline")
            break
        elif key_decoded == "i":
            info()
        elif key_decoded == "s":
            print("INFO: Scanning...")
            scan()
            print("INFO: Scan end")
        elif key_decoded == "l":
            listNicks()
        elif key_decoded == "c":
            chat()
        elif key_decoded == "g":
            groupChat()


if __name__ == "__main__":
    main()

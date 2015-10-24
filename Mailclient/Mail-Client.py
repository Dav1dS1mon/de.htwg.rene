import socket

TCP_IP = 'imap.htwg-konstanz.de'
TCP_PORT = 143
BUFFER_SIZE = 1024

# Show INBOX + Mail
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send('. login rnetin ntsmobil\r\n'.encode('utf-8'))
data = s.recv(BUFFER_SIZE)
print('\nLogin: \n', data.decode('utf-8') + '\n')
s.send(". select INBOX\r\n".encode('utf-8'))
data = s.recv(BUFFER_SIZE)
print('\nEnter INBOX: \n', data.decode('utf-8') + '\n')

email_number = input("View email number: ")

s.send((". fetch " + email_number + " full\r\n").encode('utf-8'))
data = s.recv(BUFFER_SIZE)
print('\nINBOX: \n', data.decode('utf-8') + '\n')
s.send(". logout\r\n".encode('utf-8'))
data = s.recv(BUFFER_SIZE)
print('\nE-Mail Content: \n', data.decode('utf-8') + '\n')
s.close()

# Send Mail
TCP_IP = 'asmtp.htwg-konstanz.de'
TCP_PORT = 25
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

s.send('auth login\r\n'.encode('utf-8'))
data = s.recv(BUFFER_SIZE)
print('\nAnswer: \n', data.decode('utf-8') + '\n')
s.send('cm5ldGlu\r\n'.encode('utf-8'))
data = s.recv(BUFFER_SIZE)
print('\nAnswer: \n', data.decode('utf-8') + '\n')
s.send('bnRzbW9iaWw=\r\n'.encode('utf-8'))
data = s.recv(BUFFER_SIZE)
print('\nAnswer: \n', data.decode('utf-8') + '\n')
s.send('mail from: rnetin@htwg-konstanz.de\r\n'.encode('utf-8'))
data = s.recv(BUFFER_SIZE)
print('\nAnswer: \n', data.decode('utf-8') + '\n')

email_address = input("Receiver Mail: ")

s.send(("rcpt to: " + email_address + "\r\n").encode('utf-8'))
data = s.recv(BUFFER_SIZE)
print('\nAnswer: \n', data.decode('utf-8') + '\n')
s.send('data\r\n'.encode('utf-8'))
data = s.recv(BUFFER_SIZE)
print('\nAnswer: \n', data.decode('utf-8') + '\n')

subject = input("Input Subject: ")

s.send(("Subject: " + subject + "\r\n").encode('utf-8'))
data = s.recv(BUFFER_SIZE)
print('\nAnswer: \n', data.decode('utf-8') + '\n')

content = input("Input Content: ")

s.send((content + "\r\n").encode('utf-8'))
print('\nAnswer: \n', data.decode('utf-8') + '\n')
s.send('\r\n.\r\n'.encode('utf-8'))
data = s.recv(BUFFER_SIZE)
print('\nAnswer: \n', data.decode('utf-8') + '\n')
s.send('quit\r\n'.encode('utf-8'))
data = s.recv(BUFFER_SIZE)
print('\nAnswer: \n', data.decode('utf-8') + '\n')
s.close()

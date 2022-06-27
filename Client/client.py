import socket
import sys
import os
import struct
from Tkinter import *
import tkMessageBox



# Initialise socket stuff
TCP_IP = "127.0.0.1" # Only a local server
TCP_PORT = 1456 # Just a random choice
BUFFER_SIZE = 1024 # Standard chioce
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def conn():
    # Connect to the server
    
    try:
        s.connect((TCP_IP, TCP_PORT))
        tkMessageBox.showinfo("","Connection sucessful")
    except:
        tkMessageBox.showinfo("","Connection unsucessful. Make sure the server is online.")

def upld(file_name):
    # Upload a file
    #print "\nUploading file: {}...".format(file_name)
    try:
        # Check the file exists
        content = open(file_name, "rb")
    except:
        #print "Couldn't open file. Make sure the file name was entered correctly."
        tkMessageBox.showinfo("","Couldn't open file. Make sure the file name was entered correctly.")
        return
    try:
        # Make upload request
        s.send("UPLD")
    except:
        tkMessageBox.showinfo("","Couldn't make server request. Make sure a connection has bene established.")
        #print "Couldn't make server request. Make sure a connection has bene established."
        return
    try:
        # Wait for server acknowledgement then send file details
        # Wait for server ok
        s.recv(BUFFER_SIZE)
        # Send file name size and file name
        s.send(struct.pack("h", sys.getsizeof(file_name)))
        s.send(file_name)
        # Wait for server ok then send file size
        s.recv(BUFFER_SIZE)
        s.send(struct.pack("i", os.path.getsize(file_name)))
    except:
        #print "Error sending file details"
        tkMessageBox.showinfo("","Error sending file details")
    try:
        # Send the file in chunks defined by BUFFER_SIZE
        # Doing it this way allows for unlimited potential file sizes to be sent
        l = content.read(BUFFER_SIZE)
        #print "\nSending..."
        while l:
            s.send(l)
            l = content.read(BUFFER_SIZE)
        content.close()
        # Get upload performance details
        upload_time = struct.unpack("f", s.recv(4))[0]
        upload_size = struct.unpack("i", s.recv(4))[0]
        #print "\nSent file: {}\nTime elapsed: {}s\nFile size: {}b".format(file_name, upload_time, upload_size)
        tkMessageBox.showinfo("","file sent!!")
    except:
	tkMessageBox.showinfo("","Error sending file")
        #print "Error sending file"
        return
    return

def list_files():
    # List the files avaliable on the file server
    # Called list_files(), not list() (as in the format of the others) to avoid the standard python function list()
    #print "Requesting files...\n"
    try:
        # Send list request
        s.send("LIST")
    except:
        tkMessageBox.showinfo("" ,"Couldn't make server request. Make sure a connection has bene established.")
        return
    try:
        # First get the number of files in the directory
        number_of_files = struct.unpack("i", s.recv(4))[0]
        # Then enter into a loop to recieve details of each, one by one
        for i in range(int(number_of_files)):
            # Get the file name size first to slightly lessen amount transferred over socket
            file_name_size = struct.unpack("i", s.recv(4))[0]
            file_name = s.recv(file_name_size)
            # Also get the file size for each item in the server
            file_size = struct.unpack("i", s.recv(4))[0]
            labelText2.set(str("\t{} - {}b".format(file_name, file_size)))
            # Make sure that the client and server are syncronised
            s.send("1")
        # Get total size of directory
        total_directory_size = struct.unpack("i", s.recv(4))[0]
        tkMessageBox.showinfo("" ,str("Total directory size: {}b".format(total_directory_size)))
    except:
        tkMessageBox.showinfo("" ,"Couldn't retrieve listing")
        return
    try:
        # Final check
        s.send("1")
        return
    except:
        tkMessageBox.showinfo("" , "Couldn't get final server confirmation")
        return


def dwld(file_name):
    # Download given file
    #print "Downloading file: {}".format(file_name)
    try:
        # Send server request
        s.send("DWLD")
    except:
        tkMessageBox.showinfo("","Couldn't make server request. Make sure a connection has bene established.")
        return
    try:
        # Wait for server ok, then make sure file exists
        s.recv(BUFFER_SIZE)
        # Send file name length, then name
        s.send(struct.pack("h", sys.getsizeof(file_name)))
        s.send(file_name)
        # Get file size (if exists)
        file_size = struct.unpack("i", s.recv(4))[0]
        if file_size == -1:
            # If file size is -1, the file does not exist
            tkMessageBox.showinfo("","File does not exist. Make sure the name was entered correctly")
            return
    except:
        tkMessageBox.showinfo("","Error checking file")
    try:
        # Send ok to recieve file content
        s.send("1")
        # Enter loop to recieve file
        output_file = open(file_name, "wb")
        bytes_recieved = 0
        #print "\nDownloading..."
        while bytes_recieved < file_size:
            # Again, file broken into chunks defined by the BUFFER_SIZE variable
            l = s.recv(BUFFER_SIZE)
            output_file.write(l)
            bytes_recieved += BUFFER_SIZE
        output_file.close()
        tkMessageBox.showinfo("","Successfully downloaded")
        # Tell the server that the client is ready to recieve the download performance details
        s.send("1")
        # Get performance details
        time_elapsed = struct.unpack("f", s.recv(4))[0]
        #print "Time elapsed: {}s\nFile size: {}b".format(time_elapsed, file_size)
    except:
        tkMessageBox.showinfo("","Error downloading file")
        return
    return


def quit():
   # s.send("QUIT")
    # Wait for server go-ahead
    #s.recv(BUFFER_SIZE)
    s.close()
    tkMessageBox.showinfo("" ,  "Server connection ended")
    app.quit()
    return
print "\n\nWelcome to the FTP client.\n\nCall one of the following functions:\nCONN           : Connect to server\nUPLD file_path : Upload file\nLIST           : List files\nDWLD file_path : Download file\nDELF file_path : Delete file\nQUIT           : Exit"


  

app = Tk()
app.title("ftp socket")
app.geometry("500x400+200+200")

labelText = StringVar()
labelText.set("Enter the command: \n\n 1.CONN: Make connection to server \n 2.UPLD path: upload file to server \n 3.LIST: show files in server \n 4.DWLD path: download file to client \n 5.QUIT: quit the program")
label1 = Label(app , textvariable=labelText , height=12)
label1.pack()





custname = StringVar(None)
yourname = Entry(app,textvariable=custname)
yourname.pack()

def runcommand():
    if yourname.get()[:4] == "CONN":
        conn()
    elif yourname.get()[:4] == "UPLD":
        upld(yourname.get()[5:])
    elif yourname.get()[:4] == "LIST":
        list_files()
    elif yourname.get()[:4] == "DWLD":
        dwld(yourname.get()[5:])
    elif yourname.get()[:4] == "QUIT":
        quit()

button1 = Button(app , text = "run Command!" , width=20 , command=runcommand )
button1.pack(side='bottom' , padx=15,pady=15)

app.mainloop()

from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import serial



class RootGUI():
    def __init__(self):
        '''Initializing the root GUI and other comps of the program'''
        self.root = Tk()
        self.root.title("Serial communication")
        self.root.geometry("360x120")
        self.root.config(bg="white")


# Class to setup and create the communication manager with MCU
class ComGui():
    def __init__(self, root, serial):
        '''
        Initialize the connexion GUI and initialize the main widgets 
        '''
        # Initializing the Widgets
        self.root = root
        self.serial = serial
        self.frame = LabelFrame(root, text="Com Manager",
                                padx=5, pady=5, bg="white")
        self.label_com = Label(
            self.frame, text="Available Port(s): ", bg="white", width=15, anchor="w")
        self.label_bd = Label(
            self.frame, text="Baud Rate: ", bg="white", width=15, anchor="w")

        # Setup the Drop option menu
        self.baudOptionMenu()
        self.ComOptionMenu()

        # Add the control buttons for refreshing the COMs & Connect
        self.btn_refresh = Button(self.frame, text="Refresh",
                                  width=10,  command=self.com_refresh)
        self.btn_connect = Button(self.frame, text="Connect",
                                  width=10, state="disabled",  command=self.serial_connect)

        # Optional Graphic parameters
        self.padx = 20
        self.pady = 5

        # Put on the grid all the elements
        self.publish()

    def publish(self):
        '''
         Method to display all the Widget of the main frame
        '''
        self.frame.grid(row=0, column=0, rowspan=3,
                        columnspan=3, padx=5, pady=5)
        self.label_com.grid(column=1, row=2)
        self.label_bd.grid(column=1, row=3)

        self.drop_baud.grid(column=2, row=3, padx=self.padx, pady=self.pady)
        self.drop_com.grid(column=2, row=2, padx=self.padx)

        self.btn_refresh.grid(column=3, row=2)
        self.btn_connect.grid(column=3, row=3)

    def ComOptionMenu(self):
        '''
         Method to Get the available COMs connected to the PC
         and list them into the drop menu
        '''
        # Generate the list of available coms

        self.serial.getCOMList()

        self.clicked_com = StringVar()
        self.clicked_com.set(self.serial.com_list[0])
        self.drop_com = OptionMenu(
            self.frame, self.clicked_com, *self.serial.com_list, command=self.connect_ctrl)

        self.drop_com.config(width=10)

    def baudOptionMenu(self):
        '''
         Method to list all the baud rates in a drop menu
        '''
        self.clicked_bd = StringVar()
        bds = ["-",
               "9600",
               "19200",
               "38400",
               "57600",
               "115200",
               "230400",
               "460800",
               "921600"]
        self.clicked_bd .set(bds[0])
        self.drop_baud = OptionMenu(
            self.frame, self.clicked_bd, *bds, command=self.connect_ctrl)
        self.drop_baud.config(width=10)

    def connect_ctrl(self, widget):
        '''
        Mehtod to keep the connect button disabled if all the 
        conditions are not cleared
        '''
        print("Connect ctrl")
        # Checking the logic consistency to keep the connection btn
        if "-" in self.clicked_bd.get() or "-" in self.clicked_com.get():
            self.btn_connect["state"] = "disabled"
        else:
            self.btn_connect["state"] = "active"

    def com_refresh(self):
        print("Refresh")
        # Get the Widget destroyed
        self.drop_com.destroy()

        # Refresh the list of available Coms
        self.ComOptionMenu()

        # Publish the this new droplet
        self.drop_com.grid(column=2, row=2, padx=self.padx)

        # Just in case to secure the connect logic
        logic = []
        self.connect_ctrl(logic)

    def serial_connect(self):
        '''
        Method that Updates the GUI during connect / disconnect status
        Manage serials and data flows during connect / disconnect status
        '''
        if self.btn_connect["text"] in "Connect":
            # Start the serial communication
            self.serial.SerialOpen(self)

            # If connection established move on
            if self.serial.ser.status:
                # Update the COM manager
                self.btn_connect["text"] = "Disconnect"
                self.btn_refresh["state"] = "disable"
                self.drop_baud["state"] = "disable"
                self.drop_com["state"] = "disable"
                InfoMsg = f"Successful UART connection using {self.clicked_com.get()}"
                messagebox.showinfo("showinfo", InfoMsg)

                # Display the channel manager
                self.conn = ConnGUI(self.root, self.serial)

            else:
                ErrorMsg = f"Failure to estabish UART connection using {self.clicked_com.get()} "
                messagebox.showerror("showerror", ErrorMsg)
        else:

            # Closing the Serial COM
            # Close the serial communication
            self.serial.SerialClose(self)

            # Closing the Conn Manager
            # Destroy the channel manager
            self.conn.ConnGUIClose()

            InfoMsg = f"UART connection using {self.clicked_com.get()} is now closed"
            messagebox.showwarning("showinfo", InfoMsg)
            self.btn_connect["text"] = "Connect"
            self.btn_refresh["state"] = "active"
            self.drop_baud["state"] = "active"
            self.drop_com["state"] = "active"


class ConnGUI():
    def __init__(self, root, serial):
        '''
        Initialize main Widgets for communication GUI
        '''
        self.root = root
        self.serial = serial

        # Build ConnGui Static Elements
        self.frame = LabelFrame(root, text="Connection Manager",
                                padx=5, pady=5, bg="white", width=60)
        self.label_ch = Label(
            self.frame, text="Number of channels: ", bg="white", width=15, anchor="w")

        self.framech = LabelFrame(root, text="Baud rate selection",
                                padx=5, pady=5, bg="white", width=60)
        
        #setup the drop option menu for channels
        self.numChannelMenu()
        """
        self.btn_start_stream = Button(self.frame, text="Start", state="disabled",
                                       width=5, command=self.start_stream)

        self.btn_stop_stream = Button(self.frame, text="Stop", state="disabled",
                                      width=5, command=self.stop_stream)

        self.btn_add_chart = Button(self.frame, text="+", state="disabled",
                                    width=5, bg="white", fg="#098577",
                                    command=self.new_chart)

        self.btn_kill_chart = Button(self.frame, text="-", state="disabled",
                                     width=5, bg="white", fg="#CC252C",
                                     command=self.kill_chart)
        
        self.save = False
        self.SaveVar = IntVar()
        self.save_check = Checkbutton(self.frame, text="Save data", variable=self.SaveVar,
                                      onvalue=1, offvalue=0, bg="white", state="disabled",
                                      command=self.save_data)

        self.separator = ttk.Separator(self.frame, orient='vertical')
        """
        # Optional Graphic parameters
        self.padx = 20
        self.pady = 15

        # Extending the GUI
        self.ConnGUIOpen()

    def numChannelMenu(self):
        # Method to list number of channels in a drop menu

        self.clicked_ch = StringVar()
        chs = ["-",
               "1",
               "2",
               "3",
               "4"]
        self.clicked_ch .set(chs[0])
        self.drop_ch = OptionMenu(
            self.frame, self.clicked_ch, *chs, command=self.baudrate_ctrl)
        self.drop_ch.config(width=10)

    def baudrate_ctrl(self,widget):

        bauds = [
               "9600",
               "19200",
               "38400",
               "57600",
               "115200",
               "230400",
               "460800",
               "921600"]

        self.btn_configure = Button(self.frame, text="Configure", width=10, state="disabled")
        
        #if one channel is selected
        if "1" in self.clicked_ch.get():

            #text
            self.framech = LabelFrame(self.root, text="Baud rate selection",
                                padx=5, pady=5, bg="white", width=60)
            self.label_ch_one = Label(self.framech, text="Baud rate of Ch 1", bg="white", width=15, anchor="w")
            self.framech.grid(row=0, column=15, rowspan=3,
                        columnspan=5, padx=5, pady=5)

            self.label_ch_one.grid(column=1, row=1)

            #dropdown button
            self.clicked_baud1 = StringVar()
            self.clicked_baud1 .set(bauds[0])
            self.drop_baud1 = OptionMenu(
            self.framech, self.clicked_baud1, *bauds, command=self.confi_ctrl)
            self.drop_baud1.config(width=10)

            self.drop_baud1.grid(column=2, row=1)

            #configure
    
            self.btn_configure = Button(self.framech, text="Configure", width=15, state="active", command = self.startTransmission1)
            self.btn_configure.grid(column=2, row=6, padx= self.padx, pady = self.pady)



          #if two channel is selected  
        elif "2" in self.clicked_ch.get():
            self.framech = LabelFrame(self.root, text="Baud rate selection",
                                padx=5, pady=5, bg="white", width=60)
            self.label_ch_one = Label(self.framech, text="Baud rate of Ch 1", bg="white", width=15, anchor="w")
            self.label_ch_two = Label(self.framech, text="Baud rate of Ch 2", bg="white", width=15, anchor="w")
            self.framech.grid(row=0, column=15, rowspan=3,
                        columnspan=5, padx=5, pady=5)

            self.label_ch_one.grid(column=1, row=1) 
            self.label_ch_two.grid(column=1, row=2)

        #dropdown button
            self.clicked_baud1 = StringVar()
            self.clicked_baud2 = StringVar()
            self.clicked_baud1 .set(bauds[0])
            self.clicked_baud2 .set(bauds[0])

            self.drop_baud1 = OptionMenu(
            self.framech, self.clicked_baud1, *bauds, command=self.confi_ctrl)
            self.drop_baud1.config(width=10)

            self.drop_baud2 = OptionMenu(
            self.framech, self.clicked_baud2, *bauds, command=self.confi_ctrl)
            self.drop_baud2.config(width=10)

            self.drop_baud1.grid(column=2, row=1)
            self.drop_baud2.grid(column=2, row=2)

            self.btn_configure = Button(self.framech, text="Configure", width=15, state="active", command = self.startTransmission2)
            self.btn_configure.grid(column=2, row=6, padx= self.padx, pady = self.pady)
            
        #if three channel is selected
        elif "3" in self.clicked_ch.get():
            self.framech = LabelFrame(self.root, text="Baud rate selection",
                                padx=5, pady=5, bg="white", width=60)
            self.label_ch_one = Label(self.framech, text="Baud rate of Ch 1", bg="white", width=15, anchor="w")
            self.label_ch_two = Label(self.framech, text="Baud rate of Ch 2", bg="white", width=15, anchor="w")
            self.label_ch_three = Label(self.framech, text="Baud rate of Ch 3", bg="white", width=15, anchor="w")
            self.framech.grid(row=0, column=15, rowspan=3,
                        columnspan=5, padx=5, pady=5)

            self.label_ch_one.grid(column=1, row=1) 
            self.label_ch_two.grid(column=1, row=2)
            self.label_ch_three.grid(column=1, row=3)

            #dropdown button
            self.clicked_baud1 = StringVar()
            self.clicked_baud2 = StringVar()
            self.clicked_baud3 = StringVar()
            self.clicked_baud1 .set(bauds[0])
            self.clicked_baud2 .set(bauds[0])
            self.clicked_baud3 .set(bauds[0])

            self.drop_baud1 = OptionMenu(
            self.framech, self.clicked_baud1, *bauds, command=self.confi_ctrl)
            self.drop_baud1.config(width=10)
            
            self.drop_baud2 = OptionMenu(
            self.framech, self.clicked_baud2, *bauds, command=self.confi_ctrl)
            self.drop_baud2.config(width=10)

            self.drop_baud3 = OptionMenu(
            self.framech, self.clicked_baud3, *bauds, command=self.confi_ctrl)
            self.drop_baud3.config(width=10)

            self.drop_baud1.grid(column=2, row=1)
            self.drop_baud2.grid(column=2, row=2)
            self.drop_baud3.grid(column=2, row=3)

            self.btn_configure = Button(self.framech, text="Configure", width=15, state="active", command = self.startTransmission3)
            self.btn_configure.grid(column=2, row=6, padx= self.padx, pady = self.pady)

        #if four channel is selected
        elif "4" in self.clicked_ch.get():
            self.framech = LabelFrame(self.root, text="Baud rate selection",
                                padx=5, pady=5, bg="white", width=60)
            self.label_ch_one = Label(self.framech, text="Baud rate of Ch 1", bg="white", width=15, anchor="w")
            self.label_ch_two = Label(self.framech, text="Baud rate of Ch 2", bg="white", width=15, anchor="w")
            self.label_ch_three = Label(self.framech, text="Baud rate of Ch 3", bg="white", width=15, anchor="w")
            self.label_ch_four = Label(self.framech, text="Baud rate of Ch 4", bg="white", width=15, anchor="w")
            self.framech.grid(row=0, column=15, rowspan=3,
                        columnspan=5, padx=5, pady=5)

            self.label_ch_one.grid(column=1, row=1) 
            self.label_ch_two.grid(column=1, row=2)
            self.label_ch_three.grid(column=1, row=3)
            self.label_ch_four.grid(column=1, row=4)

            #dropdown button
            self.clicked_baud1 = StringVar()
            self.clicked_baud2 = StringVar()
            self.clicked_baud3 = StringVar()
            self.clicked_baud4 = StringVar()
            self.clicked_baud1 .set(bauds[0])
            self.clicked_baud2 .set(bauds[0])
            self.clicked_baud3 .set(bauds[0])
            self.clicked_baud4 .set(bauds[0])

            self.drop_baud1 = OptionMenu(
            self.framech, self.clicked_baud1, *bauds, command=self.confi_ctrl)
            self.drop_baud1.config(width=10)
            
            self.drop_baud2 = OptionMenu(
            self.framech, self.clicked_baud2, *bauds, command=self.confi_ctrl)
            self.drop_baud2.config(width=10)

            self.drop_baud3 = OptionMenu(
            self.framech, self.clicked_baud3, *bauds, command=self.confi_ctrl)
            self.drop_baud3.config(width=10)

            self.drop_baud4 = OptionMenu(
            self.framech, self.clicked_baud4, *bauds, command=self.confi_ctrl)
            self.drop_baud4.config(width=10)

            self.drop_baud1.grid(column=2, row=1)
            self.drop_baud2.grid(column=2, row=2)
            self.drop_baud3.grid(column=2, row=3)
            self.drop_baud4.grid(column=2, row=4)

            self.btn_configure = Button(self.framech, text="Configure", width=15, state="active", command = self.startTransmission4)
            self.btn_configure.grid(column=2, row=6, padx= self.padx, pady = self.pady)
        


    def confi_ctrl(self,widget):
        '''
        Method to keep the configuration button disabled if all the 
        conditions are not met
        '''
        '''
        # Checking the logic consistency to keep the connection btn
        if "-" in self.clicked_bd.get() or "-" in self.clicked_com.get():
            self.btn_connect["state"] = "disabled"
        else:
            self.btn_connect["state"] = "active"
        '''
    
    #sends to port for one channel
    def startTransmission1(self):
        
        print(self.clicked_baud1.get())
        a = self.clicked_baud1.get()
        

        if a == '9600':
            a = b'0'
        elif a == '19200':
            a = b'1'
        elif a == '38400':
            a = b'2'
        elif a == '57600':
            a = b'3'
        elif a == '115200':
            a = b'4'
        elif a == '230400':
            a = b'5' 
        elif a == '460800':
            a = b'6'
        elif a == '921600':
            a = b'7'
        
        print('creating serial object')
        #ser1 = serial.Serial('COM7', 115200)
        

        print('sending serial comm')
        self.serial.ser.write(b"#c#1#" + a + b"#0#0#0#\n")
        print('sent serial comm')

    #sends to port for two channels
    def startTransmission2(self):
        
        a = self.clicked_baud1.get()
        print(self.clicked_baud2.get())
        b = self.clicked_baud2.get()
        

        if a == '9600':
            a = b'0'
        elif a == '19200':
            a = b'1'
        elif a == '38400':
            a = b'2'
        elif a == '57600':
            a = b'3'
        elif a == '115200':
            a = b'4'
        elif a == '230400':
            a = b'5' 
        elif a == '460800':
            a = b'6'
        elif a == '921600':
            a = b'7'

        
        if b == '9600':
            b = b'0'
        elif b == '19200':
            b = b'1'
        elif b == '38400':
            b = b'2'
        elif b == '57600':
            b = b'3'
        elif b == '115200':
            b = b'4'
        elif b == '230400':
            b = b'5' 
        elif b == '460800':
            b = b'6'
        elif b == '921600':
            b = b'7'
        
        print('creating serial object')
        #ser1 = serial.Serial('COM7', 115200)
        

        print('sending serial comm')
        self.serial.ser.write(b"#c#2#" + a + b"#" + b +b"#0#0#\n")
        print('sent serial comm')

    
    #sends to port for three channels
    def startTransmission3(self):
        
        a = self.clicked_baud1.get()
        print(self.clicked_baud2.get())
        b = self.clicked_baud2.get()
        c = self.clicked_baud3.get()
    
        

        if a == '9600':
            a = b'0'
        elif a == '19200':
            a = b'1'
        elif a == '38400':
            a = b'2'
        elif a == '57600':
            a = b'3'
        elif a == '115200':
            a = b'4'
        elif a == '230400':
            a = b'5' 
        elif a == '460800':
            a = b'6'
        elif a == '921600':
            a = b'7'

        
        if b == '9600':
            b = b'0'
        elif b == '19200':
            b = b'1'
        elif b == '38400':
            b = b'2'
        elif b == '57600':
            b = b'3'
        elif b == '115200':
            b = b'4'
        elif b == '230400':
            b = b'5' 
        elif b == '460800':
            b = b'6'
        elif b == '921600':
            b = b'7'


        if c == '9600':
            c = b'0'
        elif c == '19200':
            c = b'1'
        elif c == '38400':
            c = b'2'
        elif c == '57600':
            c = b'3'
        elif c == '115200':
            c = b'4'
        elif c == '230400':
            c = b'5' 
        elif c == '460800':
            c = b'6'
        elif c == '921600':
            c = b'7'
        
        print('creating serial object')
        #ser1 = serial.Serial('COM7', 115200)
        

        print('sending serial comm')
        self.serial.ser.write(b"#c#3#" + a + b"#" + b + b"#" + c + b"#0#\n")
        print('sent serial comm')

    #sends to port for four channel
    def startTransmission4(self):
        
        a = self.clicked_baud1.get()
        print(self.clicked_baud2.get())
        b = self.clicked_baud2.get()
        c = self.clicked_baud3.get()
        d = self.clicked_baud4.get()
        

        if a == '9600':
            a = b'0'
        elif a == '19200':
            a = b'1'
        elif a == '38400':
            a = b'2'
        elif a == '57600':
            a = b'3'
        elif a == '115200':
            a = b'4'
        elif a == '230400':
            a = b'5' 
        elif a == '460800':
            a = b'6'
        elif a == '921600':
            a = b'7'

        
        if b == '9600':
            b = b'0'
        elif b == '19200':
            b = b'1'
        elif b == '38400':
            b = b'2'
        elif b == '57600':
            b = b'3'
        elif b == '115200':
            b = b'4'
        elif b == '230400':
            b = b'5' 
        elif b == '460800':
            b = b'6'
        elif b == '921600':
            b = b'7'


        if c == '9600':
            c = b'0'
        elif c == '19200':
            c = b'1'
        elif c == '38400':
            c = b'2'
        elif c == '57600':
            c = b'3'
        elif c == '115200':
            c = b'4'
        elif c == '230400':
            c = b'5' 
        elif c == '460800':
            c = b'6'
        elif c == '921600':
            c = b'7'

        if d == '9600':
            d = b'0'
        elif d == '19200':
            d = b'1'
        elif d == '38400':
            d = b'2'
        elif d == '57600':
            d = b'3'
        elif d == '115200':
            d = b'4'
        elif d == '230400':
            d = b'5' 
        elif d == '460800':
            d = b'6'
        elif d == '921600':
            d = b'7'

        
        
        print('creating serial object')
        #ser1 = serial.Serial('COM7', 115200)
        

        print('sending serial comm')
        self.serial.ser.write(b"#c#4#" + a + b"#" + b + b"#" + c + b"#" + d + b"#\n")
        print('sent serial comm')

    def ConnGUIOpen(self):
        '''
        Method to display all the widgets 
        '''
        self.root.geometry("950x240")
        self.frame.grid(row=0, column=5, rowspan=3,
                        columnspan=5, padx=5, pady=5)

        self.label_ch.grid(column=1, row=1)
        self.drop_ch.grid(column=2, row=1, padx=self.padx, pady=self.pady)
        
        

        
        
        
        '''
        self.btn_start_stream.grid(column=3, row=1, padx=self.padx)
        self.btn_stop_stream.grid(column=3, row=2, padx=self.padx)

        self.btn_add_chart.grid(column=4, row=1, padx=self.padx)
        self.btn_kill_chart.grid(column=5, row=1, padx=self.padx)

        self.save_check.grid(column=4, row=2, columnspan=2)
        self.separator.place(relx=0.58, rely=0, relwidth=0.001, relheight=1)

        '''
    def ConnGUIClose(self):
        '''
        Method to close the connection GUI and destorys the widgets
        '''
        # Must destroy all the element so they are not kept in Memory
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        self.root.geometry("360x120")

    def start_stream(self):
        pass

    def stop_stream(self):
        pass

    def new_chart(self):
        pass

    def kill_chart(self):
        pass

    def save_data(self):
        pass


if __name__ == "__main__":
    RootGUI()
    ComGui()
    ConnGUI()
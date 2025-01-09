import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports
from tkinter import scrolledtext
import threading
import serial


class TerminalGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Serial Terminal")
        self.serial_port = None
        self.is_running = False
    
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
        # COM port selection
        self.port_label = ttk.Label(self.main_frame, text="COM Port:")
        self.port_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(self.main_frame, textvariable=self.port_var)
        self.port_combo['values'] = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
    
        # Baud rate selection
        self.baud_label = ttk.Label(self.main_frame, text="Baud Rate:")
        self.baud_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    
        self.baud_var = tk.StringVar(value='115200')
        self.baud_combo = ttk.Combobox(self.main_frame, textvariable=self.baud_var)
        self.baud_combo['values'] = ['9600', '19200', '38400', '57600', '115200']
        self.baud_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
    
        # Connect button
        self.connect_button = ttk.Button(self.main_frame, text="Connect", command=self.connect)
        self.connect_button.grid(row=2, column=0, columnspan=2, pady=10)

    def connect(self):
        if not self.serial_port:
            try:
                self.serial_port = serial.Serial(
                    port=self.port_var.get(),
                    baudrate=int(self.baud_var.get()),
                    timeout=0.1
                )
                self.is_running = True
                self.connect_button.config(text="Disconnect")
                self.create_terminal_window()
                self.receive_thread = threading.Thread(target=self.receive_data, daemon=True)
                self.receive_thread.start()
                self.input_field.focus()
            except serial.SerialException as e:
                if hasattr(self,'text_area'):
                    self.text_area.insert(tk.END, f"Error: {str(e)}\n")
        else:
            self.is_running = False
            self.serial_port.close()
            self.serial_port = None
            self.connect_button.config(text="Connect")
            self.terminal_window.destroy()

    def create_terminal_window(self):
        self.terminal_window = tk.Toplevel(self.root)
        self.terminal_window.title("Terminal")
        self.terminal_window.geometry("800x600")
        self.terminal_window.protocol("WM_DELETE_WINDOW", self.connect)
    
        # Create text area
        self.text_area = scrolledtext.ScrolledText(self.terminal_window, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill='both', padx=10, pady=(10,5))
    
        # Create input frame
        input_frame = ttk.Frame(self.terminal_window)
        input_frame.pack(fill='x', padx=10, pady=(0,10))
    
        # Create input field
        self.input_field = ttk.Entry(input_frame)
        self.input_field.pack(side='left', fill='x', expand=True, padx=(0,5))
    
        # Create send button
        send_button = ttk.Button(input_frame, text="Send", command=self.send_message)
        send_button.pack(side='right')
    
        # Bind enter key
        self.input_field.bind('<Return>', lambda e: self.send_message())

    def send_message(self):
        message = self.input_field.get()
        if message and self.serial_port:
            try:
                self.serial_port.write((message + '\n').encode())
                self.text_area.insert(tk.END, f"Sent: {message}\n")
                self.input_field.delete(0, tk.END)
                self.text_area.see(tk.END)
            except serial.SerialException as e:
                self.text_area.insert(tk.END, f"Error sending: {str(e)}\n")

    def receive_data(self):
        while self.is_running:
            if self.serial_port and self.serial_port.in_waiting:
                try:
                    data = self.serial_port.readline().decode().strip()
                    if data:
                        self.root.after(0, self.update_text_area, f"Received: {data}\n")
                except serial.SerialException as e:
                    self.root.after(0, self.update_text_area, f"Error receiving: {str(e)}\n")
                except UnicodeDecodeError:
                    pass

    def update_text_area(self, message):
        self.text_area.insert(tk.END, message)
        self.text_area.see(tk.END)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = TerminalGUI()
    app.run()
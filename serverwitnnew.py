from flask import Flask, request, jsonify
import os
import threading
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import subprocess
import time
import qrcode
from PIL import Image, ImageTk
from io import BytesIO

app = Flask(__name__)
UPLOAD_FOLDER = 'received_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class PrintKioskGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Print Kiosk System")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        # Main container
        main_frame = tk.Frame(root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="🖨️ Print Kiosk", 
            font=("Arial", 32, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=(0, 20))
        
        # QR Code Section
        qr_frame = tk.Frame(main_frame, bg="white", relief=tk.RAISED, borderwidth=2)
        qr_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            qr_frame,
            text="Scan to Upload Your Document",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=(15, 5))
        
        # Generate and display QR code
        self.qr_label = tk.Label(qr_frame, bg="white")
        self.qr_label.pack(pady=10)
        self.generate_qr_code("https://printervendingmachine.onrender.com/")
        
        tk.Label(
            qr_frame,
            text="printervendingmachine.onrender.com",
            font=("Arial", 11),
            bg="white",
            fg="#7f8c8d"
        ).pack(pady=(0, 15))
        
        # Status card
        self.status_frame = tk.Frame(main_frame, bg="white", relief=tk.RAISED, borderwidth=2)
        self.status_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Status indicator
        self.status_label = tk.Label(
            self.status_frame,
            text="● Ready",
            font=("Arial", 24, "bold"),
            bg="white",
            fg="#27ae60"
        )
        self.status_label.pack(pady=20)
        
        # File info frame
        info_frame = tk.Frame(self.status_frame, bg="white")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # File name
        tk.Label(info_frame, text="File:", font=("Arial", 14, "bold"), 
                bg="white", fg="#7f8c8d").grid(row=0, column=0, sticky="w", pady=10)
        self.filename_label = tk.Label(
            info_frame, 
            text="No file received", 
            font=("Arial", 14),
            bg="white",
            fg="#2c3e50",
            wraplength=500,
            justify="left"
        )
        self.filename_label.grid(row=0, column=1, sticky="w", padx=20, pady=10)
        
        # File size
        tk.Label(info_frame, text="Size:", font=("Arial", 14, "bold"),
                bg="white", fg="#7f8c8d").grid(row=1, column=0, sticky="w", pady=10)
        self.filesize_label = tk.Label(
            info_frame,
            text="—",
            font=("Arial", 14),
            bg="white",
            fg="#2c3e50"
        )
        self.filesize_label.grid(row=1, column=1, sticky="w", padx=20, pady=10)
        
        # Cost
        tk.Label(info_frame, text="Cost:", font=("Arial", 14, "bold"),
                bg="white", fg="#7f8c8d").grid(row=2, column=0, sticky="w", pady=10)
        self.cost_label = tk.Label(
            info_frame,
            text="—",
            font=("Arial", 14),
            bg="white",
            fg="#2c3e50"
        )
        self.cost_label.grid(row=2, column=1, sticky="w", padx=20, pady=10)
    
        # Payment status
        tk.Label(info_frame, text="Payment:", font=("Arial", 14, "bold"),
                bg="white", fg="#7f8c8d").grid(row=3, column=0, sticky="w", pady=10)
        self.payment_label = tk.Label(
            info_frame,
            text="Pending",
            font=("Arial", 14),
            bg="white",
            fg="#e67e22"
        )
        self.payment_label.grid(row=3, column=1, sticky="w", padx=20, pady=10)
        
        # Progress bar
        self.progress_frame = tk.Frame(self.status_frame, bg="white")
        self.progress_frame.pack(fill=tk.X, padx=30, pady=20)
        
        tk.Label(
            self.progress_frame,
            text="Print Progress:",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#7f8c8d"
        ).pack(anchor="w", pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            length=600,
            mode='determinate',
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill=tk.X)
        
        self.progress_text = tk.Label(
            self.progress_frame,
            text="0%",
            font=("Arial", 11),
            bg="white",
            fg="#7f8c8d"
        )
        self.progress_text.pack(anchor="e", pady=(5, 0))
        
        # Activity log frame
        log_frame = tk.Frame(main_frame, bg="white", relief=tk.RAISED, borderwidth=2)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        tk.Label(
            log_frame,
            text="Activity Log",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=10)
        
        # Scrollable log
        log_scroll_frame = tk.Frame(log_frame, bg="white")
        log_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(log_scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(
            log_scroll_frame,
            height=6,
            font=("Courier", 10),
            bg="#ecf0f1",
            fg="#2c3e50",
            yscrollcommand=scrollbar.set,
            state=tk.DISABLED,
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        # Configure progress bar style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor='#ecf0f1',
            background='#3498db',
            thickness=25
        )
        
        self.current_file = None
        self.add_log("System initialized and ready")
    
    def generate_qr_code(self, url):
        """Generate QR code for the given URL"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Resize for display
        qr_img = qr_img.resize((200, 200), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        qr_photo = ImageTk.PhotoImage(qr_img)
        
        # Keep a reference to prevent garbage collection
        self.qr_photo = qr_photo
        self.qr_label.config(image=qr_photo)
    
    def add_log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def update_status(self, status, color):
        self.status_label.config(text=f"● {status}", fg=color)
    
    def set_file_received(self, filename, filesize, cost):
        self.current_file = filename
        self.filename_label.config(text=filename)
        self.filesize_label.config(text=f"{filesize / 1024:.2f} KB")
        self.cost_label.config(text=f"₹{cost:.2f}")
        self.update_status("File Received", "#3498db")
        self.add_log(f"File received: {filename}")
    
    def set_payment_confirmed(self):
        self.payment_label.config(text="✓ Confirmed", fg="#27ae60")
        self.update_status("Payment Confirmed", "#27ae60")
        self.add_log("Payment confirmed - Starting print job")
    
    def start_printing(self):
        self.update_status("Printing...", "#9b59b6")
        self.add_log("Sending document to printer")
        self.progress_bar['value'] = 0
        self.progress_text.config(text="0%")
    
    def update_progress(self, value):
        self.progress_bar['value'] = value
        self.progress_text.config(text=f"{int(value)}%")
        self.root.update_idletasks()
    
    def complete_printing(self, success=True):
        if success:
            self.update_status("Complete ✓", "#27ae60")
            self.add_log("Print job completed successfully")
            self.progress_bar['value'] = 100
            self.progress_text.config(text="100%")
        else:
            self.update_status("Failed ✗", "#e74c3c")
            self.add_log("Print job failed - Please check printer")
        
        self.root.after(5000, self.reset_display)
    
    def reset_display(self):
        self.update_status("Ready", "#27ae60")
        self.filename_label.config(text="No file received")
        self.filesize_label.config(text="—")
        self.cost_label.config(text="—")
        self.payment_label.config(text="Pending", fg="#e67e22")
        self.progress_bar['value'] = 0
        self.progress_text.config(text="0%")
        self.current_file = None
        self.add_log("Ready for next print job")

# Global GUI instance
gui = None

def calculate_cost(filepath):
    file_size = os.path.getsize(filepath)
    pages = max(1, file_size // (100 * 1024))
    cost_per_page = 2.0
    return pages * cost_per_page

def print_file(filepath):
    try:
        gui.start_printing()
        for i in range(0, 101, 10):
            time.sleep(0.3)
            gui.update_progress(i)
        gui.complete_printing(success=True)
        return True
    except Exception as e:
        gui.add_log(f"Printing error: {str(e)}")
        gui.complete_printing(success=False)
        return False

@app.route('/print', methods=['POST'])
def receive_file():
    """Receive file and immediately start printing"""
    if 'file' not in request.files:
        return jsonify({"error": "No file received"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    file_size = os.path.getsize(filepath)
    cost = calculate_cost(filepath)
    
    if gui:
        gui.set_file_received(file.filename, file_size, cost)
        gui.set_payment_confirmed()
        threading.Thread(target=print_file, args=(filepath,), daemon=True).start()
    
    return jsonify({
        "message": f"File {file.filename} received and printing started",
        "filename": file.filename,
        "size": file_size,
        "cost": cost
    }), 200

def run_flask():
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)

if __name__ == '__main__':
    root = tk.Tk()
    gui = PrintKioskGUI(root)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    root.mainloop()
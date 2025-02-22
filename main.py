import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
import sqlite3
from datetime import datetime
import bcrypt
from PIL import Image, ImageTk

class FinanceManager(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Personal Finance Manager")
        self.geometry("1200x800")
        
        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Load images for navigation
        self.images = {
            "dashboard": ctk.CTkImage(Image.open("assets/dashboard.png"), size=(20, 20)),
            "income": ctk.CTkImage(Image.open("assets/income.png"), size=(20, 20)),
            "expense": ctk.CTkImage(Image.open("assets/expense.png"), size=(20, 20)),
            "loans": ctk.CTkImage(Image.open("assets/loans.png"), size=(20, 20)),
            "reports": ctk.CTkImage(Image.open("assets/reports.png"), size=(20, 20)),
            "settings": ctk.CTkImage(Image.open("assets/settings.png"), size=(20, 20))
        }

        # Create navigation frame
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(7, weight=1)

        self.nav_label = ctk.CTkLabel(self.navigation_frame, text="Finance Manager",
                                     compound="left", font=ctk.CTkFont(size=15, weight="bold"))
        self.nav_label.grid(row=0, column=0, padx=20, pady=20)

        # Create navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("Dashboard", self.show_dashboard),
            ("Income", self.show_income),
            ("Expense", self.show_expense),
            ("Loans", self.show_loans),
            ("Reports", self.show_reports),
            ("Settings", self.show_settings)
        ]

        for idx, (text, command) in enumerate(nav_items, start=1):
            button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                 border_spacing=10, text=text,
                                 fg_color="transparent", text_color=("gray10", "gray90"),
                                 hover_color=("gray70", "gray30"),
                                 image=self.images.get(text.lower()),
                                 anchor="w", command=command)
            button.grid(row=idx, column=0, sticky="ew")
            self.nav_buttons[text.lower()] = button

        # Create main frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Create frames for different sections
        self.frames = {}
        for frame_name in ["dashboard", "income", "expense", "loans", "reports", "settings"]:
            frame = ctk.CTkFrame(self.main_frame, corner_radius=0, fg_color="transparent")
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[frame_name] = frame

        # Show default frame (dashboard)
        self.show_dashboard()

    def show_frame(self, frame_name):
        # Hide all frames
        for frame in self.frames.values():
            frame.grid_remove()
        # Show selected frame
        self.frames[frame_name].grid()
        # Update button colors
        for name, button in self.nav_buttons.items():
            if name == frame_name:
                button.configure(fg_color=("gray75", "gray25"))
            else:
                button.configure(fg_color="transparent")

    def show_dashboard(self):
        self.show_frame("dashboard")
        # Implement dashboard view

    def show_income(self):
        self.show_frame("income")
        # Implement income view

    def show_expense(self):
        self.show_frame("expense")
        # Implement expense view

    def show_loans(self):
        self.show_frame("loans")
        # Implement loans view

    def show_reports(self):
        self.show_frame("reports")
        # Implement reports view

    def show_settings(self):
        self.show_frame("settings")
        # Implement settings view

if __name__ == "__main__":
    # Create assets directory if it doesn't exist
    if not os.path.exists("assets"):
        os.makedirs("assets")
        
    # Initialize database
    from db.schema import create_database
    create_database()
    
    app = FinanceManager()
    app.mainloop()

import customtkinter as ctk
from src.ui.app import PlanEstudiosApp

if __name__ == "__main__":
    root = ctk.CTk()
    app = PlanEstudiosApp(root)
    root.mainloop()

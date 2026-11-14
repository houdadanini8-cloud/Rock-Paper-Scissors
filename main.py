import tkinter as tk
import json
import os
from datetime import datetime

from playervsplayer import PvPFrame
from playervsAi import AIFrame
from camera_test import CameraAIFrame

DATA_FILE = "game_data.json"

class RPSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rock Paper Scissors")

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        self.geometry(f"{screen_w}x{screen_h}+0+0")
        self.state("zoomed")
        self.resizable(True, True)
        self.configure(bg="#120e1c")

        self.fullscreen = False
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)

        self.init_json()

        # --- TOP HEADER ---
        header = tk.Frame(self, bg="#120e1c")
        header.pack(pady=(16, 6))

        tk.Label(header, text="👑", font=("Segoe UI Emoji", 20), bg="#120e1c", fg="#f3e8ff").pack()
        tk.Label(header, text="✦✦  Rock Paper Scissors ✦✦", font=("Georgia", 26, "bold"), bg="#120e1c", fg="#f5f3ff").pack()

        # --- TOP MODE NAVIGATION BAR ---
        nav_bar = tk.Frame(self, bg="#1b1528", highlightbackground="#2e2442", highlightthickness=1, padx=8, pady=6)
        nav_bar.pack(pady=(8, 6))

        self.nav_buttons = {}
        modes = (
            ("PvPFrame", "👥  Player vs Player"),
            ("AIFrame", "🤖  Player vs AI"),
            ("CameraAIFrame", "📷  Camera Mode")
        )

        for frame_name, label in modes:
            btn = tk.Button(
                nav_bar, text=label, font=("Segoe UI", 12, "bold"),
                bd=0, padx=24, pady=8, cursor="hand2",
                command=lambda fn=frame_name: self.show_frame(fn)
            )
            btn.pack(side=tk.LEFT, padx=5)
            self.nav_buttons[frame_name] = btn

        # Global Reset Game Button in Top Bar
        tk.Button(
            nav_bar, text="🔄  Reset Game", font=("Segoe UI", 12, "bold"),
            bg="#2b2140", fg="#f87171", activebackground="#3f2e5e", activeforeground="#fca5a5",
            bd=0, padx=20, pady=8, cursor="hand2", command=self.reset_entire_game
        ).pack(side=tk.LEFT, padx=(14, 5))

        # --- CONTENT CONTAINER ---
        container = tk.Frame(self, bg="#120e1c")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (PvPFrame, AIFrame, CameraAIFrame):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("PvPFrame")

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)

    def exit_fullscreen(self, event=None):
        self.fullscreen = False
        self.attributes("-fullscreen", False)

    def show_frame(self, page_name):
        if page_name != "CameraAIFrame":
            self.frames["CameraAIFrame"].stop_camera()
        else:
            self.frames["CameraAIFrame"].start_camera()

        for name, btn in self.nav_buttons.items():
            if name == page_name:
                btn.config(bg="#9333ea", fg="white")
            else:
                btn.config(bg="#1b1528", fg="#cbd5e1")

        self.frames[page_name].tkraise()

    def init_json(self):
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({"matches": []}, f, indent=4)

    def save_match(self, mode, p1_move, opponent_move, result):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["matches"].append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": mode,
            "player_1": p1_move,
            "opponent": opponent_move,
            "result": result
        })

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def get_mode_stats(self, mode):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        matches = [m for m in data.get("matches", ()) if m.get("mode") == mode]
        p1_wins = sum(1 for m in matches if m["result"] in ("Player 1 Win", "Player Win"))
        draws = sum(1 for m in matches if m["result"] == "Draw")
        opp_wins = sum(1 for m in matches if m["result"] in ("Player 2 Win", "AI Win"))
        return p1_wins, draws, opp_wins

    def reset_mode_stats(self, mode):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["matches"] = [m for m in data.get("matches", ()) if m.get("mode") != mode]
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def reset_entire_game(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"matches": []}, f, indent=4)

        for frame in self.frames.values():
            if hasattr(frame, "reset_all"):
                frame.reset_all()

if __name__ == "__main__":
    app = RPSApp()
    app.mainloop()
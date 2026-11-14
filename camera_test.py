import tkinter as tk
import cv2
import time
from cvzone.HandTrackingModule import HandDetector
from PIL import Image, ImageTk
import random
import os

try:
    from google import genai
except ImportError:
    genai = None

class CameraAIFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#120e1c")
        self.controller = controller
        self.cap = None
        self.running = False
        self.detected_sign = "None"
        self.history = []
        self.emojis = {"Rock": "✊", "Paper": "✋", "Scissors": "✌️", "None": "📷", "Unknown": "❓"}

        self.stable_sign = None
        self.stable_start_time = None
        self.round_played_for_hold = False

        self.detector = HandDetector(maxHands=1, detectionCon=0.7)

        api_key = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if (genai and api_key != "YOUR_GEMINI_API_KEY") else None

        body = tk.Frame(self, bg="#120e1c")
        body.pack(fill="both", expand=True, padx=35, pady=8)

        # --- LEFT PANEL: Live Webcam Feed ---
        cam_panel = tk.Frame(body, bg="#1b1528", highlightbackground="#9333ea", highlightthickness=2, padx=14, pady=12)
        cam_panel.pack(side=tk.LEFT, fill="y", padx=(0, 24))

        tk.Label(cam_panel, text="📷 Hold Hand Steady for 4s", font=("Segoe UI", 12, "bold"), bg="#1b1528", fg="#e9d5ff").pack(pady=(0, 6))

        video_box = tk.Frame(cam_panel, bg="#0d0a14", width=330, height=250)
        video_box.pack()
        video_box.pack_propagate(False)

        self.video_label = tk.Label(video_box, bg="#0d0a14")
        self.video_label.pack(fill="both", expand=True)

        self.live_sign_lbl = tk.Label(cam_panel, text="Detected: None", font=("Segoe UI", 12, "bold"), bg="#1b1528", fg="#facc15")
        self.live_sign_lbl.pack(pady=(8, 2))

        self.hold_timer_lbl = tk.Label(cam_panel, text="Show ✊ ✋ or ✌️ to auto-play", font=("Segoe UI", 10, "bold"), bg="#1b1528", fg="#c084fc")
        self.hold_timer_lbl.pack(pady=(2, 2))

        # --- RIGHT PANEL: Arena ---
        arena = tk.Frame(body, bg="#161122", highlightbackground="#2e2442", highlightthickness=1, padx=25, pady=12)
        arena.pack(side=tk.LEFT, fill="both", expand=True)

        tk.Label(arena, text="Camera Mode vs AI", font=("Segoe UI", 16, "bold"), bg="#161122", fg="#e9d5ff").pack(pady=(0, 6))

        cards_row = tk.Frame(arena, bg="#161122")
        cards_row.pack(pady=4)

        self.you_card = tk.Frame(cards_row, bg="#1f1830", highlightbackground="#9333ea", highlightthickness=2, width=175, height=165)
        self.you_card.pack(side=tk.LEFT, padx=16)
        self.you_card.pack_propagate(False)
        tk.Label(self.you_card, text="You (Cam)", font=("Segoe UI", 10, "bold"), bg="#9333ea", fg="white", padx=12, pady=2).pack(pady=(6, 0))
        self.you_emoji_lbl = tk.Label(self.you_card, text="✊", font=("Segoe UI Emoji", 54), bg="#1f1830", fg="#facc15")
        self.you_emoji_lbl.pack(expand=True)

        tk.Label(cards_row, text="⚡ VS ⚡", font=("Segoe UI", 20, "bold"), bg="#161122", fg="#f3e8ff").pack(side=tk.LEFT, padx=12)

        self.ai_card = tk.Frame(cards_row, bg="#1f1830", highlightbackground="#9333ea", highlightthickness=2, width=175, height=165)
        self.ai_card.pack(side=tk.LEFT, padx=16)
        self.ai_card.pack_propagate(False)
        tk.Label(self.ai_card, text="AI", font=("Segoe UI", 10, "bold"), bg="#9333ea", fg="white", padx=22, pady=2).pack(pady=(6, 0))
        self.ai_emoji_lbl = tk.Label(self.ai_card, text="✋", font=("Segoe UI Emoji", 54), bg="#1f1830", fg="#facc15")
        self.ai_emoji_lbl.pack(expand=True)

        self.banner_lbl = tk.Label(
            arena, text="Hold sign steady for 4s to play!", font=("Segoe UI", 12, "bold"),
            bg="#261e38", fg="#f3e8ff", highlightbackground="#7e22ce", highlightthickness=1, padx=26, pady=6
        )
        self.banner_lbl.pack(pady=8)

        score_row = tk.Frame(arena, bg="#161122")
        score_row.pack(pady=4)

        self.you_score_lbl = self._make_stat_box(score_row, "🏆 Wins", "0")
        self.draw_score_lbl = self._make_stat_box(score_row, "🤝 Draws", "0")
        self.ai_score_lbl = self._make_stat_box(score_row, "🤖 AI Wins", "0")

        action_row = tk.Frame(arena, bg="#161122")
        action_row.pack(pady=(8, 4))

        tk.Button(
            action_row, text="▶  Next Round", font=("Segoe UI", 11, "bold"),
            bg="#9333ea", fg="white", activebackground="#7e22ce", activeforeground="white",
            bd=0, padx=24, pady=8, cursor="hand2", command=self.reset_hold_state
        ).pack(side=tk.LEFT, padx=8)

        tk.Button(
            action_row, text="🔄  Reset Scores", font=("Segoe UI", 11, "bold"),
            bg="#2b2140", fg="#f87171", activebackground="#3f2e5e", activeforeground="#fca5a5",
            bd=0, padx=20, pady=8, cursor="hand2", command=self.reset_all
        ).pack(side=tk.LEFT, padx=8)

        self.refresh_scores()

    def _make_stat_box(self, parent, title, val):
        box = tk.Frame(parent, bg="#1f1830", highlightbackground="#32264a", highlightthickness=1, width=115, height=52)
        box.pack(side=tk.LEFT, padx=10)
        box.pack_propagate(False)
        tk.Label(box, text=title, font=("Segoe UI", 9), bg="#1f1830", fg="#cbd5e1").pack(pady=(3, 0))
        lbl = tk.Label(box, text=val, font=("Segoe UI", 13, "bold"), bg="#1f1830", fg="white")
        lbl.pack()
        return lbl

    def start_camera(self):
        if self.running:
            return
        self.reset_hold_state()
        for index in (0, 1):
            for backend in (cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY):
                cap = cv2.VideoCapture(index, backend)
                if cap is not None and cap.isOpened():
                    ret, _ = cap.read()
                    if ret:
                        self.cap = cap
                        self.running = True
                        self.banner_lbl.config(text="Hold sign steady for 4s to play!")
                        self.update_frame()
                        return
                if cap:
                    cap.release()
        self.banner_lbl.config(text="⚠️ Camera not accessible!")

    def stop_camera(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None

    def update_frame(self):
        if not self.running:
            return
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            hands, frame = self.detector.findHands(frame, draw=True, flipType=False)

            if hands:
                hand = next(iter(hands))
                fingers = self.detector.fingersUp(hand)
                total_up = sum(fingers)

                if total_up == 0:
                    self.detected_sign = "Rock"
                elif tuple(fingers) == (0, 1, 1, 0, 0) or total_up == 2:
                    self.detected_sign = "Scissors"
                elif total_up >= 4:
                    self.detected_sign = "Paper"
                else:
                    self.detected_sign = "Unknown"
            else:
                self.detected_sign = "None"

            self.process_auto_hold()

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.live_sign_lbl.config(text=f"Detected: {self.detected_sign} {self.emojis.get(self.detected_sign, '')}")

            img = Image.fromarray(rgb_frame).resize((330, 250))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.after(25, self.update_frame)

    def process_auto_hold(self):
        valid_moves = ("Rock", "Paper", "Scissors")

        if self.detected_sign not in valid_moves:
            self.stable_sign = None
            self.stable_start_time = None
            self.round_played_for_hold = False
            self.hold_timer_lbl.config(text="Show ✊ ✋ or ✌️ to auto-play", fg="#c084fc")
            return

        if self.detected_sign != self.stable_sign:
            self.stable_sign = self.detected_sign
            self.stable_start_time = time.time()
            self.round_played_for_hold = False

        if self.round_played_for_hold:
            self.hold_timer_lbl.config(text="✅ Played! Change/lower hand for next round", fg="#4ade80")
            return

        elapsed = time.time() - self.stable_start_time
        remaining = max(0.0, 4.0 - elapsed)

        if remaining > 0:
            self.hold_timer_lbl.config(text=f"⏳ Holding {self.stable_sign}: {remaining:.1f}s...", fg="#facc15")
        else:
            self.round_played_for_hold = True
            self.hold_timer_lbl.config(text=f"🔥 Locked {self.stable_sign}!", fg="#4ade80")
            self.play_detected_sign(self.stable_sign)

    def get_ai_move(self):
        if self.client and self.history:
            try:
                prompt = f"Rock Paper Scissors history: {self.history[-5:]}. Reply ONLY with Rock, Paper, or Scissors."
                res = self.client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                choice = res.text.strip().capitalize()
                if choice in ("Rock", "Paper", "Scissors"):
                    return choice
            except Exception:
                pass
        return random.choice(("Rock", "Paper", "Scissors"))

    def play_detected_sign(self, player_move):
        ai_move = self.get_ai_move()
        self.history.append(player_move)

        self.you_emoji_lbl.config(text=self.emojis[player_move])
        self.ai_emoji_lbl.config(text=self.emojis[ai_move])

        if player_move == ai_move:
            outcome = "Draw"
            msg = "It's a Draw!"
        elif (
            (player_move == "Rock" and ai_move == "Scissors")
            or (player_move == "Paper" and ai_move == "Rock")
            or (player_move == "Scissors" and ai_move == "Paper")
        ):
            outcome = "Player Win"
            msg = "You Win!"
        else:
            outcome = "AI Win"
            msg = "AI Wins!"

        self.banner_lbl.config(text=msg)
        self.controller.save_match("Camera vs AI", player_move, ai_move, outcome)
        self.refresh_scores()

    def reset_hold_state(self):
        self.stable_sign = None
        self.stable_start_time = None
        self.round_played_for_hold = False
        self.banner_lbl.config(text="Hold sign steady for 4s to play!")

    def reset_all(self):
        self.history.clear()
        self.controller.reset_mode_stats("Camera vs AI")
        self.refresh_scores()
        self.reset_hold_state()
        self.you_emoji_lbl.config(text="✊")
        self.ai_emoji_lbl.config(text="✋")
        self.banner_lbl.config(text="Scores Reset! Hold sign for 4s.")

    def refresh_scores(self):
        p_w, draws, ai_w = self.controller.get_mode_stats("Camera vs AI")
        self.you_score_lbl.config(text=str(p_w))
        self.draw_score_lbl.config(text=str(draws))
        self.ai_score_lbl.config(text=str(ai_w))
            
import tkinter as tk
import random
import os

try:
    from google import genai
except ImportError:
    genai = None

class AIFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#120e1c")
        self.controller = controller
        self.history = []
        self.emojis = {"Rock": "✊", "Paper": "✋", "Scissors": "✌️"}

        api_key = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if (genai and api_key != "YOUR_GEMINI_API_KEY") else None

        body = tk.Frame(self, bg="#120e1c")
        body.pack(fill="both", expand=True, padx=35, pady=8)

        # --- LEFT PANEL ---
        left_panel = tk.Frame(body, bg="#1b1528", highlightbackground="#2e2442", highlightthickness=1, padx=20, pady=16)
        left_panel.pack(side=tk.LEFT, fill="y", padx=(0, 24))

        tk.Label(left_panel, text="Choose:", font=("Segoe UI", 14, "bold"), bg="#1b1528", fg="#e2d9f3").pack(anchor="w", pady=(0, 12))

        for move in ("Rock", "Paper", "Scissors"):
            tk.Button(
                left_panel, text=f"  {self.emojis[move]}    {move}", font=("Segoe UI", 14, "bold"),
                bg="#231c34", fg="#f3e8ff", activebackground="#3b2d59", activeforeground="white",
                bd=0, width=15, pady=14, anchor="w", padx=14, cursor="hand2",
                command=lambda m=move: self.play_round(m)
            ).pack(pady=8)

        # --- RIGHT PANEL ---
        arena = tk.Frame(body, bg="#161122", highlightbackground="#2e2442", highlightthickness=1, padx=25, pady=12)
        arena.pack(side=tk.LEFT, fill="both", expand=True)

        tk.Label(arena, text="Player vs AI", font=("Segoe UI", 16, "bold"), bg="#161122", fg="#e9d5ff").pack()

        diff_row = tk.Frame(arena, bg="#161122")
        diff_row.pack(pady=(2, 6))
        tk.Label(diff_row, text="Difficulty: ", font=("Segoe UI", 10), bg="#161122", fg="#cbd5e1").pack(side=tk.LEFT)
        self.diff_var = tk.StringVar(value="Medium")
        diff_menu = tk.OptionMenu(diff_row, self.diff_var, "Easy", "Medium", "AI API (Hard)")
        diff_menu.config(font=("Segoe UI", 10), bg="#231c34", fg="white", bd=0, highlightthickness=0, activebackground="#3b2d59")
        diff_menu["menu"].config(bg="#231c34", fg="white")
        diff_menu.pack(side=tk.LEFT)

        cards_row = tk.Frame(arena, bg="#161122")
        cards_row.pack(pady=4)

        self.you_card = tk.Frame(cards_row, bg="#1f1830", highlightbackground="#9333ea", highlightthickness=2, width=175, height=165)
        self.you_card.pack(side=tk.LEFT, padx=18)
        self.you_card.pack_propagate(False)
        tk.Label(self.you_card, text="You", font=("Segoe UI", 10, "bold"), bg="#9333ea", fg="white", padx=20, pady=2).pack(pady=(6, 0))
        self.you_emoji_lbl = tk.Label(self.you_card, text="✊", font=("Segoe UI Emoji", 54), bg="#1f1830", fg="#facc15")
        self.you_emoji_lbl.pack(expand=True)

        tk.Label(cards_row, text="⚡ VS ⚡", font=("Segoe UI", 20, "bold"), bg="#161122", fg="#f3e8ff").pack(side=tk.LEFT, padx=14)

        self.ai_card = tk.Frame(cards_row, bg="#1f1830", highlightbackground="#9333ea", highlightthickness=2, width=175, height=165)
        self.ai_card.pack(side=tk.LEFT, padx=18)
        self.ai_card.pack_propagate(False)
        tk.Label(self.ai_card, text="AI", font=("Segoe UI", 10, "bold"), bg="#9333ea", fg="white", padx=22, pady=2).pack(pady=(6, 0))
        self.ai_emoji_lbl = tk.Label(self.ai_card, text="✋", font=("Segoe UI Emoji", 54), bg="#1f1830", fg="#facc15")
        self.ai_emoji_lbl.pack(expand=True)

        self.banner_lbl = tk.Label(
            arena, text="Choose a move to start!", font=("Segoe UI", 12, "bold"),
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
            action_row, text="▶  Play Again", font=("Segoe UI", 11, "bold"),
            bg="#9333ea", fg="white", activebackground="#7e22ce", activeforeground="white",
            bd=0, padx=24, pady=8, cursor="hand2", command=self.reset_display
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

    def get_ai_move(self):
        diff = self.diff_var.get()
        if diff == "AI API (Hard)" and self.client and self.history:
            try:
                prompt = f"Rock Paper Scissors history: {self.history[-5:]}. Reply ONLY with Rock, Paper, or Scissors to counter my next move."
                res = self.client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                choice = res.text.strip().capitalize()
                if choice in ("Rock", "Paper", "Scissors"):
                    return choice
            except Exception:
                pass
        elif diff == "Medium" and self.history:
            counters = {"Rock": "Paper", "Paper": "Scissors", "Scissors": "Rock"}
            if random.random() < 0.5:
                return counters[self.history[-1]]
        return random.choice(("Rock", "Paper", "Scissors"))

    def play_round(self, player_move):
        ai_move = self.get_ai_move()
        self.history.append(player_move)

        self.you_emoji_lbl.config(text=self.emojis[player_move])
        self.ai_emoji_lbl.config(text=self.emojis[ai_move])

        if player_move == ai_move:
            outcome = "Draw"
            msg = "It's a Draw!"
        elif (player_move == "Rock" and ai_move == "Scissors") or \
             (player_move == "Paper" and ai_move == "Rock") or \
             (player_move == "Scissors" and ai_move == "Paper"):
            outcome = "Player Win"
            msg = "You Win!"
        else:
            outcome = "AI Win"
            msg = "AI Wins!"

        self.banner_lbl.config(text=msg)
        self.controller.save_match("Player vs AI", player_move, ai_move, outcome)
        self.refresh_scores()

    def reset_display(self):
        self.you_emoji_lbl.config(text="✊")
        self.ai_emoji_lbl.config(text="✋")
        self.banner_lbl.config(text="Pick your next move!")

    def reset_all(self):
        self.history.clear()
        self.controller.reset_mode_stats("Player vs AI")
        self.refresh_scores()
        self.reset_display()
        self.banner_lbl.config(text="Scores Reset! Choose a move.")

    def refresh_scores(self):
        p_w, draws, ai_w = self.controller.get_mode_stats("Player vs AI")
        self.you_score_lbl.config(text=str(p_w))
        self.draw_score_lbl.config(text=str(draws))
        self.ai_score_lbl.config(text=str(ai_w))
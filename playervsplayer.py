import tkinter as tk

class PvPFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#120e1c")
        self.controller = controller
        self.p1_choice = None
        self.p2_choice = None
        self.locked = False

        self.emojis = {"Rock": "✊", "Paper": "✋", "Scissors": "✌️"}

        body = tk.Frame(self, bg="#120e1c")
        body.pack(fill="both", expand=True, padx=35, pady=8)

        # --- LEFT PANEL ---
        left_panel = tk.Frame(body, bg="#1b1528", highlightbackground="#2e2442", highlightthickness=1, padx=20, pady=16)
        left_panel.pack(side=tk.LEFT, fill="y", padx=(0, 24))

        tk.Label(left_panel, text="Choose:", font=("Segoe UI", 14, "bold"), bg="#1b1528", fg="#e2d9f3").pack(anchor="w", pady=(0, 12))

        for move in ("Rock", "Paper", "Scissors"):
            btn = tk.Button(
                left_panel, text=f"  {self.emojis[move]}    {move}", font=("Segoe UI", 14, "bold"),
                bg="#231c34", fg="#f3e8ff", activebackground="#3b2d59", activeforeground="white",
                bd=0, relief="flat", width=15, pady=14, anchor="w", padx=14, cursor="hand2",
                command=lambda m=move: self.select_move(m)
            )
            btn.pack(pady=8)

        # --- RIGHT PANEL ---
        arena = tk.Frame(body, bg="#161122", highlightbackground="#2e2442", highlightthickness=1, padx=25, pady=12)
        arena.pack(side=tk.LEFT, fill="both", expand=True)

        tk.Label(arena, text="Player vs Player", font=("Segoe UI", 16, "bold"), bg="#161122", fg="#e9d5ff").pack()
        self.turn_label = tk.Label(arena, text="Player 1: Pick your move", font=("Segoe UI", 11), bg="#161122", fg="#c084fc")
        self.turn_label.pack(pady=(2, 8))

        cards_row = tk.Frame(arena, bg="#161122")
        cards_row.pack(pady=4)

        self.p1_card = tk.Frame(cards_row, bg="#1f1830", highlightbackground="#9333ea", highlightthickness=2, width=175, height=165)
        self.p1_card.pack(side=tk.LEFT, padx=18)
        self.p1_card.pack_propagate(False)
        tk.Label(self.p1_card, text="Player 1", font=("Segoe UI", 10, "bold"), bg="#9333ea", fg="white", padx=16, pady=2).pack(pady=(6, 0))
        self.p1_emoji_lbl = tk.Label(self.p1_card, text="❓", font=("Segoe UI Emoji", 54), bg="#1f1830", fg="#facc15")
        self.p1_emoji_lbl.pack(expand=True)

        tk.Label(cards_row, text="⚡ VS ⚡", font=("Segoe UI", 20, "bold"), bg="#161122", fg="#f3e8ff").pack(side=tk.LEFT, padx=14)

        self.p2_card = tk.Frame(cards_row, bg="#1f1830", highlightbackground="#9333ea", highlightthickness=2, width=175, height=165)
        self.p2_card.pack(side=tk.LEFT, padx=18)
        self.p2_card.pack_propagate(False)
        tk.Label(self.p2_card, text="Player 2", font=("Segoe UI", 10, "bold"), bg="#9333ea", fg="white", padx=16, pady=2).pack(pady=(6, 0))
        self.p2_emoji_lbl = tk.Label(self.p2_card, text="❓", font=("Segoe UI Emoji", 54), bg="#1f1830", fg="#facc15")
        self.p2_emoji_lbl.pack(expand=True)

        self.banner_lbl = tk.Label(
            arena, text="Waiting for Player 1...", font=("Segoe UI", 12, "bold"),
            bg="#261e38", fg="#f3e8ff", highlightbackground="#7e22ce", highlightthickness=1, padx=26, pady=6
        )
        self.banner_lbl.pack(pady=8)

        # Scoreboard Row
        score_row = tk.Frame(arena, bg="#161122")
        score_row.pack(pady=4)

        self.p1_score_lbl = self._make_stat_box(score_row, "🏆 P1 Wins", "0")
        self.draw_score_lbl = self._make_stat_box(score_row, "🤝 Draws", "0")
        self.p2_score_lbl = self._make_stat_box(score_row, "🏆 P2 Wins", "0")

        # Bottom Buttons Row
        action_row = tk.Frame(arena, bg="#161122")
        action_row.pack(pady=(8, 4))

        tk.Button(
            action_row, text="▶  Play Again", font=("Segoe UI", 11, "bold"),
            bg="#9333ea", fg="white", activebackground="#7e22ce", activeforeground="white",
            bd=0, padx=24, pady=8, cursor="hand2", command=self.reset_round
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

    def select_move(self, move):
        if self.locked:
            return

        if self.p1_choice is None:
            self.p1_choice = move
            self.p1_emoji_lbl.config(text="🔒")
            self.turn_label.config(text="Player 1 Locked! Player 2: Pick your move")
            self.banner_lbl.config(text="Player 1 Choice Hidden")
        elif self.p2_choice is None:
            self.p2_choice = move
            self.p2_emoji_lbl.config(text="🔒")
            self.locked = True
            self.start_countdown(3)

    def start_countdown(self, seconds):
        if seconds > 0:
            self.turn_label.config(text=f"Revealing moves in {seconds}s...")
            self.banner_lbl.config(text=f"⏳ {seconds}...")
            self.after(1000, lambda: self.start_countdown(seconds - 1))
        else:
            self.reveal_and_score()

    def reveal_and_score(self):
        p1, p2 = self.p1_choice, self.p2_choice
        self.p1_emoji_lbl.config(text=self.emojis[p1])
        self.p2_emoji_lbl.config(text=self.emojis[p2])

        if p1 == p2:
            outcome = "Draw"
            msg = "It's a Draw!"
        elif (p1 == "Rock" and p2 == "Scissors") or (p1 == "Paper" and p2 == "Rock") or (p1 == "Scissors" and p2 == "Paper"):
            outcome = "Player 1 Win"
            msg = "Player 1 Wins!"
        else:
            outcome = "Player 2 Win"
            msg = "Player 2 Wins!"

        self.turn_label.config(text="Round Complete!")
        self.banner_lbl.config(text=msg)
        self.controller.save_match("PvP", p1, p2, outcome)
        self.refresh_scores()

    def reset_round(self):
        self.p1_choice = None
        self.p2_choice = None
        self.locked = False
        self.p1_emoji_lbl.config(text="❓")
        self.p2_emoji_lbl.config(text="❓")
        self.turn_label.config(text="Player 1: Pick your move")
        self.banner_lbl.config(text="Waiting for Player 1...")

    def reset_all(self):
        self.controller.reset_mode_stats("PvP")
        self.refresh_scores()
        self.reset_round()
        self.banner_lbl.config(text="Scores Reset! Waiting for Player 1...")

    def refresh_scores(self):
        p1_w, draws, p2_w = self.controller.get_mode_stats("PvP")
        self.p1_score_lbl.config(text=str(p1_w))
        self.draw_score_lbl.config(text=str(draws))
        self.p2_score_lbl.config(text=str(p2_w))
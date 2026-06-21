"""Polished Tkinter renderer over the interactive SDK session."""

from pathlib import Path
from tkinter import Canvas, DoubleVar, StringVar, Tk, filedialog, messagebox, ttk

from cops_and_robbers_rl.gui.theme import COLORS, configure_theme
from cops_and_robbers_rl.sdk import (
    DEFAULT_SCREENSHOT_DIR,
    CopsAndRobbersSDK,
    InteractiveSession,
    InteractiveSnapshot,
)

CELL_SIZE = 76


class GameWindow:
    """Render immutable SDK snapshots and forward explicit user commands."""

    def __init__(self, root: Tk, session: InteractiveSession) -> None:
        self.root = root
        self.session = session
        self.round_text = StringVar()
        self.move_text = StringVar()
        self.score_text = StringVar()
        self.status_text = StringVar()
        self.progress = DoubleVar()
        root.title("Cops and Robbers RL")
        root.geometry("980x680")
        root.resizable(False, False)
        configure_theme(root)
        self._build_layout()
        self.render(session.snapshot)

    def _build_layout(self) -> None:
        header = ttk.Frame(self.root, style="Header.TFrame", padding=(28, 14))
        header.pack(fill="x")
        ttk.Label(header, text="COPS & ROBBERS", style="Title.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            header,
            text="Multi-agent pursuit-evasion lab",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(3, 0))
        ttk.Label(
            header,
            text="SDK BACKED  /  LOCAL OBSERVATIONS",
            style="Badge.TLabel",
        ).grid(row=0, column=1, rowspan=2, sticky="e")
        header.columnconfigure(0, weight=1)

        body = ttk.Frame(self.root, style="Page.TFrame", padding=(28, 16, 28, 12))
        body.pack(fill="both", expand=True)
        board_card = ttk.Frame(body, style="Card.TFrame", padding=16)
        board_card.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        self.canvas = Canvas(
            board_card,
            width=5 * CELL_SIZE,
            height=5 * CELL_SIZE,
            background=COLORS["board"],
            highlightthickness=0,
        )
        self.canvas.pack()

        panel = ttk.Frame(body, style="Page.TFrame")
        panel.grid(row=0, column=1, sticky="nsew")
        self._metric(panel, "MATCH", self.round_text, 0)
        self._metric(panel, "PROGRESS", self.move_text, 1)
        self._metric(panel, "SCORE", self.score_text, 2)
        self._metric(panel, "STATUS", self.status_text, 3, accent=True)
        ttk.Progressbar(
            panel,
            variable=self.progress,
            maximum=100,
            style="Game.Horizontal.TProgressbar",
        ).grid(row=4, column=0, sticky="ew", pady=(4, 8))
        self._legend(panel).grid(row=5, column=0, sticky="ew")

        controls = ttk.Frame(self.root, style="Controls.TFrame", padding=(28, 10, 28, 12))
        controls.pack(fill="x")
        actions = (
            ("Reset match", self._reset, "Secondary.TButton"),
            ("Step", self._step, "Secondary.TButton"),
            ("Finish sub-game", self._run_sub_game, "Secondary.TButton"),
            ("Run full match", self._run_full_match, "Accent.TButton"),
            ("Export board", self._export, "Secondary.TButton"),
        )
        for column, (text, command, style) in enumerate(actions):
            ttk.Button(controls, text=text, command=command, style=style).grid(
                row=0, column=column, padx=5, sticky="ew"
            )
            controls.columnconfigure(column, weight=1)
        ttk.Label(
            controls,
            text="Blue = cop  |  Red = thief  |  Slate = barrier",
            style="Footer.TLabel",
        ).grid(row=1, column=0, columnspan=5, pady=(7, 0))

    def _metric(
        self,
        parent: ttk.Frame,
        title: str,
        variable: StringVar,
        row: int,
        *,
        accent: bool = False,
    ) -> None:
        card = ttk.Frame(parent, style="AccentCard.TFrame" if accent else "Card.TFrame", padding=10)
        card.grid(row=row, column=0, sticky="ew", pady=(0, 6))
        prefix = "Accent" if accent else ""
        ttk.Label(card, text=title, style=f"{prefix}MetricTitle.TLabel").pack(anchor="w")
        ttk.Label(card, textvariable=variable, style=f"{prefix}MetricValue.TLabel").pack(
            anchor="w", pady=(4, 0)
        )

    def _legend(self, parent: ttk.Frame) -> ttk.Frame:
        legend = ttk.Frame(parent, style="Card.TFrame", padding=10)
        ttk.Label(legend, text="LIVE BOARD", style="MetricTitle.TLabel").pack(anchor="w")
        ttk.Label(
            legend,
            text="Seed 42 / heuristic policies\n6 sub-games / 25 move limit",
            style="Body.TLabel",
            justify="left",
        ).pack(anchor="w", pady=(4, 0))
        return legend

    def render(self, snapshot: InteractiveSnapshot) -> None:
        """Draw one renderer-safe snapshot without applying game rules."""
        self.canvas.delete("all")
        rows, columns = snapshot.grid_size
        for row in range(rows):
            for column in range(columns):
                x0, y0 = column * CELL_SIZE, row * CELL_SIZE
                fill = COLORS["cell_a"] if (row + column) % 2 == 0 else COLORS["cell_b"]
                self.canvas.create_rectangle(
                    x0 + 2,
                    y0 + 2,
                    x0 + CELL_SIZE - 2,
                    y0 + CELL_SIZE - 2,
                    fill=fill,
                    outline=COLORS["grid"],
                    width=1,
                )
                self.canvas.create_text(
                    x0 + 10,
                    y0 + 9,
                    text=f"{row + 1},{column + 1}",
                    fill=COLORS["coordinate"],
                    font=("Segoe UI", 7),
                )
        for barrier in snapshot.barriers:
            self._barrier(barrier.row, barrier.column)
        self._agent(snapshot.cop_position.row, snapshot.cop_position.column, COLORS["cop"], "C")
        self._agent(
            snapshot.thief_position.row,
            snapshot.thief_position.column,
            COLORS["thief"],
            "T",
        )
        winner = snapshot.winner.value.title() if snapshot.winner else "In progress"
        if snapshot.full_match_complete:
            winner = f"{winner} - match complete"
        self.round_text.set(f"Sub-game {snapshot.sub_game_id} of {snapshot.num_games}")
        self.move_text.set(f"Move {snapshot.moves_completed} of {snapshot.max_moves}")
        self.score_text.set(
            f"Cop {snapshot.match_score.cop}  /  Thief {snapshot.match_score.thief}"
        )
        self.status_text.set(winner)
        self.progress.set(100 * snapshot.moves_completed / max(snapshot.max_moves, 1))

    def _agent(self, row: int, column: int, color: str, label: str) -> None:
        margin = 15
        x0, y0 = column * CELL_SIZE + margin, row * CELL_SIZE + margin
        x1, y1 = (column + 1) * CELL_SIZE - margin, (row + 1) * CELL_SIZE - margin
        self.canvas.create_oval(x0 + 4, y0 + 6, x1 + 4, y1 + 6, fill=COLORS["shadow"], outline="")
        self.canvas.create_oval(x0, y0, x1, y1, fill=color, outline="white", width=3)
        self.canvas.create_text(
            (x0 + x1) / 2,
            (y0 + y1) / 2,
            text=label,
            fill="white",
            font=("Segoe UI", 18, "bold"),
        )

    def _barrier(self, row: int, column: int) -> None:
        margin = 20
        x0, y0 = column * CELL_SIZE + margin, row * CELL_SIZE + margin
        x1, y1 = (column + 1) * CELL_SIZE - margin, (row + 1) * CELL_SIZE - margin
        self.canvas.create_rectangle(
            x0, y0, x1, y1, fill=COLORS["barrier"], outline="white", width=2
        )
        self.canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text="B", fill="white")

    def _reset(self) -> None:
        self.render(self.session.reset())

    def _step(self) -> None:
        self.render(self.session.step())

    def _run_sub_game(self) -> None:
        self.render(self.session.run_sub_game())

    def _run_full_match(self) -> None:
        self.render(self.session.run_full_match())

    def _export(self) -> None:
        DEFAULT_SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        destination = filedialog.asksaveasfilename(
            initialdir=DEFAULT_SCREENSHOT_DIR,
            initialfile="cops_and_robbers_gui.ps",
            defaultextension=".ps",
            filetypes=(("PostScript image", "*.ps"),),
        )
        if destination:
            self.canvas.postscript(file=destination, colormode="color")
            messagebox.showinfo("Export complete", f"Saved {Path(destination).name}")


def launch_gui(config_path: str | Path | None = None, *, demo: bool = False) -> None:
    """Launch the native GUI with heuristic baseline agents."""
    sdk = CopsAndRobbersSDK.from_config(config_path)
    session = sdk.create_interactive_session()
    if demo:
        session.run_full_match()
    root = Tk()
    GameWindow(root, session)
    root.mainloop()

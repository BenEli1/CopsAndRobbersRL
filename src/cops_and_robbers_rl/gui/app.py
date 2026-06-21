"""Thin Tkinter renderer over the interactive SDK session."""

from pathlib import Path
from tkinter import BOTH, Canvas, Frame, Label, StringVar, Tk, filedialog, messagebox, ttk

from cops_and_robbers_rl.sdk import (
    DEFAULT_SCREENSHOT_DIR,
    CopsAndRobbersSDK,
    InteractiveSession,
    InteractiveSnapshot,
)

CELL_SIZE = 84


class GameWindow:
    """Render SDK snapshots and forward user commands to the session."""

    def __init__(self, root: Tk, session: InteractiveSession) -> None:
        self.root = root
        self.session = session
        self.status = StringVar()
        root.title("Cops and Robbers RL")
        root.minsize(520, 620)

        self.canvas = Canvas(root, background="#f8fafc", highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=True, padx=18, pady=(18, 8))
        Label(root, textvariable=self.status, font=("Segoe UI", 11), justify="left").pack()

        controls = Frame(root)
        controls.pack(pady=14)
        for text, command in (
            ("Reset", self._reset),
            ("Step", self._step),
            ("Run sub-game", self._run_sub_game),
            ("Run full match", self._run_full_match),
            ("Export image", self._export),
        ):
            ttk.Button(controls, text=text, command=command).pack(side="left", padx=4)
        self.render(session.snapshot)

    def render(self, snapshot: InteractiveSnapshot) -> None:
        """Draw one immutable SDK snapshot without applying game rules."""
        self.canvas.delete("all")
        rows, columns = snapshot.grid_size
        width, height = columns * CELL_SIZE, rows * CELL_SIZE
        self.canvas.configure(width=width, height=height)
        for row in range(rows):
            for column in range(columns):
                x0, y0 = column * CELL_SIZE, row * CELL_SIZE
                self.canvas.create_rectangle(
                    x0, y0, x0 + CELL_SIZE, y0 + CELL_SIZE, outline="#64748b", width=2
                )
        for barrier in snapshot.barriers:
            self._cell_marker(barrier.row, barrier.column, "#334155", "B")
        self._cell_marker(snapshot.cop_position.row, snapshot.cop_position.column, "#2563eb", "C")
        self._cell_marker(
            snapshot.thief_position.row, snapshot.thief_position.column, "#dc2626", "T"
        )
        winner = snapshot.winner.value.title() if snapshot.winner else "In progress"
        completion = " | Full match complete" if snapshot.full_match_complete else ""
        self.status.set(
            f"Sub-game {snapshot.sub_game_id}/{snapshot.num_games} | Move "
            f"{snapshot.moves_completed}/{snapshot.max_moves}\n"
            f"Sub-game score — Cop {snapshot.sub_game_score.cop}, "
            f"Thief {snapshot.sub_game_score.thief}\n"
            f"Match score — Cop {snapshot.match_score.cop}, Thief {snapshot.match_score.thief}\n"
            f"Status: {winner}{completion}"
        )

    def _cell_marker(self, row: int, column: int, color: str, label: str) -> None:
        margin = 13
        x0, y0 = column * CELL_SIZE + margin, row * CELL_SIZE + margin
        x1, y1 = (column + 1) * CELL_SIZE - margin, (row + 1) * CELL_SIZE - margin
        self.canvas.create_oval(x0, y0, x1, y1, fill=color, outline="")
        self.canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=label, fill="white")

    def _reset(self) -> None:
        self.render(self.session.reset())

    def _step(self) -> None:
        self.render(self.session.step())

    def _run_sub_game(self) -> None:
        self.render(self.session.run_sub_game())

    def _run_full_match(self) -> None:
        self.render(self.session.run_full_match())

    def _export(self) -> None:
        output_dir = DEFAULT_SCREENSHOT_DIR
        output_dir.mkdir(parents=True, exist_ok=True)
        destination = filedialog.asksaveasfilename(
            initialdir=output_dir,
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

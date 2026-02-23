"""Progress widget for displaying download progress."""

import logging
import tkinter as tk
from tkinter import ttk
from typing import Any

from resource_fetcher_gui.gui.core.output_parser import SongProgress

logger = logging.getLogger(__name__)


class ProgressWidget(ttk.LabelFrame):
    """Widget for displaying download progress.

    Shows overall progress bar and song status list with icons.
    """

    def __init__(self, master: tk.Widget) -> None:
        """Initialize progress widget.

        Args:
            master: Parent widget.
        """
        super().__init__(master, text="Progress", padding=10)

        self.song_items: dict[str, dict[str, Any]] = {}
        self._create_widgets()
        logger.debug("ProgressWidget initialized")

    def _create_widgets(self) -> None:
        """Create progress display widgets."""
        # Overall progress frame
        progress_frame = ttk.Frame(self)
        progress_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(progress_frame, text="Overall Progress:").pack(side=tk.LEFT, padx=(0, 5))

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode="determinate",
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.progress_label = ttk.Label(progress_frame, text="0/0")
        self.progress_label.pack(side=tk.LEFT, padx=(5, 0))

        # Song list with Treeview
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview
        columns = ("status", "title")
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
        )

        self.tree.heading("status", text="Status")
        self.tree.heading("title", text="Song Title")

        self.tree.column("status", width=80, anchor=tk.CENTER)
        self.tree.column("title", width=400, anchor=tk.W)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        # Status icons (using text for simplicity)
        self.icons = {
            "pending": "\u231B",  # Hourglass
            "downloading": "\u2193",  # Down arrow
            "success": "\u2713",  # Checkmark
            "failed": "\u2717",  # Cross mark
            "skipped": "\u23ED",  # Skip symbol
        }

        # Configure tags for coloring
        self.tree.tag_configure("failed", foreground="red")
        self.tree.tag_configure("success", foreground="green")
        self.tree.tag_configure("downloading", foreground="blue")

    def update_progress(self, progress: SongProgress) -> None:
        """Update song progress.

        Args:
            progress: Song progress information.
        """
        song_id = f"{progress.index}:{progress.title}"

        if song_id not in self.song_items:
            # Add new song to list
            item_id = self.tree.insert("", tk.END, values=("", progress.title))
            self.song_items[song_id] = {"item_id": item_id, "status": progress.status}
        else:
            # Update existing song
            item_id = self.song_items[song_id]["item_id"]
            self.tree.item(item_id, values=(self._get_icon(progress.status), progress.title))

            # Update tag based on status
            tags = ()
            if progress.status == "failed":
                tags = ("failed",)
            elif progress.status == "success":
                tags = ("success",)
            elif progress.status == "downloading":
                tags = ("downloading",)

            self.tree.item(item_id, tags=tags)
            self.song_items[song_id]["status"] = progress.status

        # Update overall progress
        if progress.total > 0:
            percentage = (progress.index / progress.total) * 100
            self.progress_var.set(percentage)
            self.progress_label.config(text=f"{progress.index}/{progress.total}")

        logger.debug(f"Updated progress: [{progress.index}/{progress.total}] {progress.title}")

    def _get_icon(self, status: str) -> str:
        """Get icon for status.

        Args:
            status: Song status.

        Returns:
            Icon character.
        """
        return self.icons.get(status, "\u003F")  # Question mark as default

    def set_total_songs(self, total: int) -> None:
        """Set total number of songs.

        Args:
            total: Total song count.
        """
        self.progress_bar.config(maximum=total)
        self.progress_label.config(text=f"0/{total}")
        logger.debug(f"Set total songs: {total}")

    def clear(self) -> None:
        """Clear all progress data."""
        self.tree.delete(*self.tree.get_children())
        self.song_items.clear()
        self.progress_var.set(0)
        self.progress_label.config(text="0/0")
        logger.debug("Progress cleared")

    def get_failed_songs(self) -> list[str]:
        """Get list of failed song titles.

        Returns:
            List of failed song titles.
        """
        failed = []
        for song_id, data in self.song_items.items():
            if data["status"] == "failed":
                # Extract title from song_id (format: "index:title")
                title = song_id.split(":", 1)[1] if ":" in song_id else song_id
                failed.append(title)
        return failed

    def scroll_to_bottom(self) -> None:
        """Scroll treeview to show last item."""
        if self.tree.get_children():
            self.tree.see(self.tree.get_children()[-1])

from __future__ import annotations

import os
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import tkinter as tk
import webbrowser

from tkinterdnd2 import DND_FILES, TkinterDnD

from .grib_output import group_streams, write_current_gribs
from .report import write_reports
from .xml_input import load_dataset


VERSION = "0.2.1"

HELP_TEXT = f"""NLCurrent ↭ Grib2 Exporter V{VERSION}                       7/2026

Konvertiert XML Dateien zu Grib2 (grb2)
als Oberflächenströmung für QtVlm/OpenCPN

Christian Streicher, Facebook"""


class Application:
    def __init__(self) -> None:
        self.root = TkinterDnD.Tk()
        self.root.title(f"XML ↭ Grib2 Exporter – V{VERSION}")
        self.root.geometry("780x465")
        self.root.minsize(680, 440)
        self.source: Path | None = None
        self.dataset = None
        self.output_var = tk.StringVar()
        self._build()

    def _build(self) -> None:
        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill="both", expand=True)
        ttk.Label(
            frame,
            text=f"XML ↭ Grib2 Exporter – V{VERSION}",
            font=("", 17, "bold"),
        ).pack(
            pady=(0, 12)
        )
        self.drop = ttk.Label(
            frame,
            text="XML-Dateien oder Exportordner hier ablegen\n\n"
            "oder über „Ordner wählen“ öffnen",
            anchor="center",
            relief="groove",
            padding=38,
        )
        self.drop.pack(fill="x")
        self.drop.drop_target_register(DND_FILES)
        self.drop.dnd_bind("<<Drop>>", self._on_drop)
        ttk.Button(frame, text="Ordner wählen …", command=self._browse).pack(pady=9)

        output_frame = ttk.Frame(frame)
        output_frame.pack(fill="x", pady=(4, 6))
        ttk.Label(output_frame, text="Ausgabeordner:").pack(side="left")
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_var)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=8)
        ttk.Button(output_frame, text="Auswählen …", command=self._browse_output).pack(
            side="right"
        )

        self.summary = ttk.Label(frame, text="Noch keine Daten geladen.", justify="left")
        self.summary.pack(fill="x", pady=8)
        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.pack(fill="x", pady=(4, 6))
        self.convert_button = ttk.Button(
            frame, text="GRIB2 erzeugen", command=self._convert, state="disabled"
        )
        self.convert_button.pack(pady=(6, 4))

        bottom = ttk.Frame(frame)
        bottom.pack(fill="x", side="bottom")
        self.status = ttk.Label(bottom, text="Bereit.")
        self.status.pack(side="left", fill="x", expand=True)
        ttk.Button(bottom, text="Hilfe", command=self._show_help).pack(side="right")
        tk.Frame(frame, height=1, background="black").pack(
            fill="x", side="bottom", pady=(4, 5)
        )

    def _show_help(self) -> None:
        window = tk.Toplevel(self.root)
        window.title("Hilfe – XML ↭ Grib2 Exporter")
        window.resizable(False, False)
        body = ttk.Frame(window, padding=18)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=HELP_TEXT, justify="left").pack(anchor="w")
        link = tk.Label(
            body,
            text="https://github.com/SignalKuser",
            fg="#0563c1",
            cursor="hand2",
            font=("", 10, "underline"),
        )
        link.pack(anchor="w", pady=(8, 14))
        link.bind(
            "<Button-1>",
            lambda _event: webbrowser.open("https://github.com/SignalKuser"),
        )
        ttk.Button(body, text="Schließen", command=window.destroy).pack(anchor="e")

    def _on_drop(self, event) -> None:
        paths = list(self.root.tk.splitlist(event.data))
        if paths:
            first = Path(paths[0])
            self._load(first if first.is_dir() else first.parent)

    def _browse(self) -> None:
        path = filedialog.askdirectory(title="UTC-XML-Export auswählen")
        if path:
            self._load(Path(path))

    def _browse_output(self) -> None:
        path = filedialog.askdirectory(title="Ausgabeordner auswählen")
        if path:
            self.output_var.set(path)

    def _load(self, source: Path) -> None:
        try:
            self.status.config(text="Prüfe XML-Dateien …")
            self.root.update_idletasks()
            self.dataset = load_dataset(source)
            self.source = source
            if not self.output_var.get():
                self.output_var.set(str(source.parent / f"{source.name}_GRIB2"))
            groups = group_streams(self.dataset)
            group_text = ", ".join(f"{key}: {len(value)}" for key, value in groups.items())
            self.summary.config(
                text=(
                    f"Quelle: {source}\n"
                    f"Häfen: {len(self.dataset.ports)} | "
                    f"Strömungspunkte: {len(self.dataset.streams)}\n"
                    f"Regionen: {group_text or 'keine'}\n"
                    f"UTC: {self.dataset.start:%d.%m.%Y %H:%M} – "
                    f"{self.dataset.end:%d.%m.%Y %H:%M}\n"
                    f"Sample Period: {self.dataset.sample_minutes} Minuten"
                )
            )
            supported = bool(groups) and all(len(value) >= 3 for value in groups.values())
            self.convert_button.config(state="normal" if supported else "disabled")
            self.status.config(
                text=(
                    "Datenprüfung erfolgreich."
                    if supported
                    else "Mindestens drei Punkte je Region erforderlich."
                )
            )
        except Exception as exc:
            self.dataset = None
            self.convert_button.config(state="disabled")
            self.status.config(text="Datenprüfung fehlgeschlagen.")
            messagebox.showerror("Ungültiger Export", str(exc))

    def _convert(self) -> None:
        if self.dataset is None:
            return
        output_text = self.output_var.get().strip()
        if not output_text:
            messagebox.showwarning("Ausgabeordner fehlt", "Bitte Ausgabeordner auswählen.")
            return
        output_dir = Path(output_text)
        try:
            self.progress.start(12)
            self.status.config(text="Erzeuge regionale GRIB2-Dateien …")
            self.root.update_idletasks()
            results = write_current_gribs(self.dataset, output_dir)
            write_reports(self.dataset, output_dir)
            self.status.config(text=f"Fertig: {len(results)} GRIB2-Datei(en)")
            messagebox.showinfo(
                "Konvertierung abgeschlossen",
                f"{len(results)} GRIB2-Datei(en) erzeugt:\n{output_dir}",
            )
        except Exception as exc:
            self.status.config(text="Konvertierung fehlgeschlagen.")
            messagebox.showerror("Konvertierungsfehler", str(exc))
        finally:
            self.progress.stop()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    Application().run()


if __name__ == "__main__":
    main()

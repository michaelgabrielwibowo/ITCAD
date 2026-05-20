from __future__ import annotations

import json
import tkinter as tk
from tkinter import filedialog, messagebox

from open_image_to_cad.pipeline import run
from open_image_to_cad.schemas import RunRequest


def launch() -> None:
    root = tk.Tk()
    root.title("Open Image to CAD")
    root.geometry("700x500")

    image_var = tk.StringVar()

    def browse() -> None:
        path = filedialog.askopenfilename(title="Select image")
        if path:
            image_var.set(path)

    tk.Label(root, text="Image path").pack(anchor="w", padx=10, pady=(10, 2))
    tk.Entry(root, textvariable=image_var, width=90).pack(padx=10)
    tk.Button(root, text="Browse", command=browse).pack(anchor="w", padx=10, pady=6)

    tk.Label(root, text="Text prompt").pack(anchor="w", padx=10, pady=(8, 2))
    prompt = tk.Text(root, height=8)
    prompt.pack(fill="x", padx=10)

    output = tk.Text(root, height=14)
    output.pack(fill="both", expand=True, padx=10, pady=10)

    def process() -> None:
        try:
            req = RunRequest(text=prompt.get("1.0", "end").strip() or None, image_path=image_var.get() or None)
            if not req.text and not req.image_path:
                messagebox.showerror("Error", "Add text and/or image first.")
                return
            res = run(req)
            output.delete("1.0", "end")
            output.insert("1.0", json.dumps(res.model_dump(), indent=2))
        except Exception as exc:
            messagebox.showerror("Processing error", str(exc))

    tk.Button(root, text="Generate CAD", command=process).pack(pady=6)
    root.mainloop()

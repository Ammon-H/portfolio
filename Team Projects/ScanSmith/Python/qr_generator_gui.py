"""
Scan Smith
----------
A fully offline desktop GUI for generating QR codes.
"""

import io
import os
import shutil
import subprocess
import sys
import tempfile

from deps_check import ensure_dependencies
ensure_dependencies(
    fallback_script=os.path.join(os.path.dirname(os.path.abspath(__file__)), "qr_gui.py")
)

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk

from qr_generator import generate_custom_qr

try:
    import win32clipboard  # type: ignore
    HAS_WIN_CLIPBOARD = True
except ImportError:
    HAS_WIN_CLIPBOARD = False

if sys.platform.startswith("win"):
    FONT_FAMILY = "Segoe UI"
elif sys.platform == "darwin":
    FONT_FAMILY = "Helvetica Neue"
else:
    FONT_FAMILY = "DejaVu Sans"

# ---------------------------------------------------------------------------
# Color / style palette
# ---------------------------------------------------------------------------
COLOR_BG = "#f4f4f5"
COLOR_CARD = "#ffffff"
COLOR_BORDER = "#e2e2e6"
COLOR_TEXT_PRIMARY = "#1f1f23"
COLOR_TEXT_SECONDARY = "#7a7a82"
COLOR_INPUT_BG = "#fafafa"
COLOR_PRIMARY_BTN = "#3a3a42"
COLOR_PRIMARY_BTN_HOVER = "#27272c"
COLOR_SECONDARY_BTN = "#eeeeef"
COLOR_SECONDARY_BTN_HOVER = "#e2e2e6"
COLOR_QR_PLACEHOLDER_BG = "#fafafa"
COLOR_CUSTOMIZE_BG = "#fbfbfc"
COLOR_LINK = "#52525b"
COLOR_LINK_HOVER = "#1f1f23"

QR_DISPLAY_SIZE = 260

FONT_TITLE = (FONT_FAMILY, 16, "bold")
FONT_LABEL = (FONT_FAMILY, 10, "bold")
FONT_BUTTON = (FONT_FAMILY, 10, "bold")
FONT_SECONDARY_BUTTON = (FONT_FAMILY, 9, "bold")
FONT_PLACEHOLDER = (FONT_FAMILY, 10)


class HoverButton(tk.Label):
    """Custom button for precise styling control."""
    def __init__(self, master, text, command, bg, hover_bg, fg="#ffffff",
                 font=FONT_BUTTON, padx=18, pady=10, **kwargs):
        super().__init__(
            master, text=text, bg=bg, fg=fg, font=font,
            cursor="hand2", padx=padx, pady=pady, **kwargs
        )
        self.command = command
        self.bg_normal = bg
        self.bg_hover = hover_bg
        self.enabled = True
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_click(self, _event):
        if self.enabled and self.command:
            self.command()

    def _on_enter(self, _event):
        if self.enabled:
            self.config(bg=self.bg_hover)

    def _on_leave(self, _event):
        if self.enabled:
            self.config(bg=self.bg_normal)

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        if enabled:
            self.config(bg=self.bg_normal, cursor="hand2")
        else:
            self.config(bg="#d8d8da", cursor="arrow")


class ScanSmithApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Scan Smith")
        self.geometry("700x560")
        self.minsize(660, 400)
        self.configure(bg=COLOR_BG)

        self.current_qr_image = None  
        self.current_qr_photo = None  
        self.current_qr_data = ""

        # Customize panel state
        self.fg_color = "#000000"
        self.bg_color = "#ffffff"
        self.logo_path = None
        self.logo_border_color = "#ffffff"
        self.logo_border_width_var = tk.IntVar(value=0)
        self.logo_border_radius_var = tk.IntVar(value=0)
        self.dots_var = tk.BooleanVar(value=False)
        self.format_var = tk.StringVar(value="PNG")
        self.output_size_var = tk.StringVar(value="") 
        self.customize_visible = False

        self._build_ui()

    def _build_ui(self):
        outer = tk.Frame(self, bg=COLOR_BG)
        outer.pack(fill="both", expand=True, padx=20, pady=20)

        card = tk.Frame(outer, bg=COLOR_CARD, highlightbackground=COLOR_BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True)

        canvas = tk.Canvas(card, bg=COLOR_CARD, highlightthickness=0, bd=0)
        canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(card, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=self.scrollbar.set)

        scroll_frame = tk.Frame(canvas, bg=COLOR_CARD)
        scroll_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        def _sync_scrollregion(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            self._update_scrollbar_visibility(canvas)

        def _sync_content_width(event):
            canvas.itemconfig(scroll_window, width=event.width)

        scroll_frame.bind("<Configure>", _sync_scrollregion)
        canvas.bind("<Configure>", _sync_content_width)

        def _on_mousewheel(event):
            if not self.scrollbar.winfo_ismapped():
                return
            if sys.platform == "darwin":
                # macOS trackpad deltas vary wildly with scroll speed (single
                # digits to 100+) rather than the fixed step size Windows
                # reports, so use a fixed step per tick instead of the raw
                # magnitude to avoid huge, erratic jumps.
                delta = -1 if event.delta > 0 else 1
            else:
                delta = -1 * int(event.delta / 120)
            canvas.yview_scroll(delta, "units")

        def _on_mousewheel_linux(event):
            if not self.scrollbar.winfo_ismapped():
                return
            canvas.yview_scroll(-1 if event.num == 4 else 1, "units")

        # Bound globally (not just on the bare canvas) since the content
        # frame packed on top of it via create_window covers almost the
        # entire canvas area, so the canvas itself rarely gets pointer
        # enter/leave events to gate a conditional bind on.
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", _on_mousewheel_linux)
        canvas.bind_all("<Button-5>", _on_mousewheel_linux)

        self._sync_scrollregion = _sync_scrollregion

        content = tk.Frame(scroll_frame, bg=COLOR_CARD)
        content.pack(fill="both", expand=True, padx=24, pady=22)

        # --- Header ---
        tk.Label(
            content, text="Scan Smith", font=FONT_TITLE,
            bg=COLOR_CARD, fg=COLOR_TEXT_PRIMARY, anchor="center", justify="center"
        ).grid(row=0, column=0, columnspan=2, sticky="ew")

        tk.Frame(content, bg=COLOR_BORDER, height=1).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(16, 16))

        left_col = tk.Frame(content, bg=COLOR_CARD)
        left_col.grid(row=2, column=0, sticky="nsew", padx=(0, 20))

        right_col = tk.Frame(content, bg=COLOR_CARD)
        right_col.grid(row=2, column=1, sticky="n")

        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=0)
        content.grid_rowconfigure(2, weight=1)

        # --- Input section ---
        tk.Label(left_col, text="URL or text", font=FONT_LABEL, bg=COLOR_CARD, fg=COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(0, 6))

        input_frame = tk.Frame(left_col, bg=COLOR_INPUT_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
        input_frame.pack(fill="x")

        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(
            input_frame, textvariable=self.input_var, font=(FONT_FAMILY, 10),
            bg=COLOR_INPUT_BG, relief="flat", bd=0,
            fg=COLOR_TEXT_PRIMARY, insertbackground=COLOR_TEXT_PRIMARY
        )
        self.input_entry.pack(fill="x", padx=12, pady=10)
        self.input_entry.bind("<Return>", lambda _e: self.generate_preview())
        self.input_entry.focus_set()

        # --- Customize toggle + panel ---
        self.customize_toggle_btn = tk.Label(
            left_col, text="▸ Customize options & export format", font=(FONT_FAMILY, 9, "bold"),
            bg=COLOR_CARD, fg=COLOR_LINK, cursor="hand2"
        )
        self.customize_toggle_btn.pack(anchor="w", pady=(10, 0))
        self.customize_toggle_btn.bind("<Button-1>", lambda _e: self._toggle_customize())
        self.customize_toggle_btn.bind("<Enter>", lambda _e: self.customize_toggle_btn.config(fg=COLOR_LINK_HOVER))
        self.customize_toggle_btn.bind("<Leave>", lambda _e: self.customize_toggle_btn.config(fg=COLOR_LINK))

        self.customize_frame = tk.Frame(left_col, bg=COLOR_CUSTOMIZE_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
        self._build_customize_section(self.customize_frame)

        # --- Primary action ---
        generate_btn = HoverButton(right_col, text="Generate Preview", command=self.generate_preview, bg=COLOR_PRIMARY_BTN, hover_bg=COLOR_PRIMARY_BTN_HOVER)
        generate_btn.pack(fill="x", pady=(0, 14))

        # --- Output section ---
        tk.Label(right_col, text="Generated QR preview", font=FONT_LABEL, bg=COLOR_CARD, fg=COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(0, 8))

        output_outer = tk.Frame(right_col, bg=COLOR_CARD)
        output_outer.pack(pady=(0, 16))

        self.qr_canvas_frame = tk.Frame(
            output_outer, width=QR_DISPLAY_SIZE, height=QR_DISPLAY_SIZE,
            bg=COLOR_QR_PLACEHOLDER_BG, highlightbackground=COLOR_BORDER, highlightthickness=1
        )
        self.qr_canvas_frame.pack()
        self.qr_canvas_frame.pack_propagate(False)

        self.qr_label = tk.Label(self.qr_canvas_frame, text="[ QR Code ]", font=FONT_PLACEHOLDER, bg=COLOR_QR_PLACEHOLDER_BG, fg=COLOR_TEXT_SECONDARY)
        self.qr_label.pack(fill="both", expand=True)

        # --- Secondary actions ---
        actions_frame = tk.Frame(right_col, bg=COLOR_CARD)
        actions_frame.pack(fill="x")

        self.save_btn = HoverButton(
            actions_frame, text="Save", command=self.save_qr,
            bg=COLOR_SECONDARY_BTN, hover_bg=COLOR_SECONDARY_BTN_HOVER, fg=COLOR_TEXT_PRIMARY, font=FONT_SECONDARY_BUTTON
        )
        self.save_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.save_btn.set_enabled(False)

        self.copy_btn = HoverButton(
            actions_frame, text="Copy", command=self.copy_qr,
            bg=COLOR_SECONDARY_BTN, hover_bg=COLOR_SECONDARY_BTN_HOVER, fg=COLOR_TEXT_PRIMARY, font=FONT_SECONDARY_BUTTON
        )
        self.copy_btn.pack(side="left", fill="x", expand=True, padx=(6, 0))
        self.copy_btn.set_enabled(False)

    def _build_customize_section(self, parent):
        inner = tk.Frame(parent, bg=COLOR_CUSTOMIZE_BG)
        inner.pack(fill="x", padx=14, pady=12)

        # Swatches
        colors_row = tk.Frame(inner, bg=COLOR_CUSTOMIZE_BG)
        colors_row.pack(fill="x")

        fg_field, self.fg_swatch, self.fg_hex_label = self._make_color_field(colors_row, "Foreground", self.fg_color, "fg")
        fg_field.pack(side="left", padx=(0, 24))

        bg_field, self.bg_swatch, self.bg_hex_label = self._make_color_field(colors_row, "Background", self.bg_color, "bg")
        bg_field.pack(side="left")

        tk.Frame(inner, bg=COLOR_BORDER, height=1).pack(fill="x", pady=12)

        # Logo row
        tk.Label(inner, text="Logo (optional)", font=(FONT_FAMILY, 8, "bold"), bg=COLOR_CUSTOMIZE_BG, fg=COLOR_TEXT_SECONDARY).pack(anchor="w")
        logo_row = tk.Frame(inner, bg=COLOR_CUSTOMIZE_BG)
        logo_row.pack(fill="x", pady=(4, 0))

        self.logo_filename_var = tk.StringVar(value="No logo selected")
        tk.Label(logo_row, textvariable=self.logo_filename_var, font=(FONT_FAMILY, 9), bg=COLOR_CUSTOMIZE_BG, fg=COLOR_TEXT_PRIMARY, anchor="w").pack(side="left", fill="x", expand=True)

        HoverButton(logo_row, text="Browse", command=self._browse_logo, bg=COLOR_SECONDARY_BTN, hover_bg=COLOR_SECONDARY_BTN_HOVER, fg=COLOR_TEXT_PRIMARY, font=(FONT_FAMILY, 8, "bold"), padx=10, pady=5).pack(side="left", padx=(8, 0))
        
        self.logo_clear_btn = HoverButton(logo_row, text="Clear", command=self._clear_logo, bg=COLOR_SECONDARY_BTN, hover_bg=COLOR_SECONDARY_BTN_HOVER, fg=COLOR_TEXT_PRIMARY, font=(FONT_FAMILY, 8, "bold"), padx=10, pady=5)
        self.logo_clear_btn.pack(side="left", padx=(6, 0))
        self.logo_clear_btn.set_enabled(False)

        # Border control
        border_row = tk.Frame(inner, bg=COLOR_CUSTOMIZE_BG)
        border_row.pack(fill="x", pady=(12, 0))

        width_field = tk.Frame(border_row, bg=COLOR_CUSTOMIZE_BG)
        width_field.pack(side="left", padx=(0, 18))
        tk.Label(width_field, text="Border width", font=(FONT_FAMILY, 8, "bold"), bg=COLOR_CUSTOMIZE_BG, fg=COLOR_TEXT_SECONDARY).pack(anchor="w")
        tk.Spinbox(width_field, from_=0, to=20, textvariable=self.logo_border_width_var, width=4, font=(FONT_FAMILY, 9), relief="flat", highlightbackground=COLOR_BORDER, highlightthickness=1).pack(anchor="w", pady=(4, 0))

        border_color_field, self.logo_border_swatch, self.logo_border_hex_label = self._make_color_field(border_row, "Border color", self.logo_border_color, "logo_border")
        border_color_field.pack(side="left", padx=(0, 18))

        radius_field = tk.Frame(border_row, bg=COLOR_CUSTOMIZE_BG)
        radius_field.pack(side="left")
        tk.Label(radius_field, text="Border radius", font=(FONT_FAMILY, 8, "bold"), bg=COLOR_CUSTOMIZE_BG, fg=COLOR_TEXT_SECONDARY).pack(anchor="w")
        tk.Spinbox(radius_field, from_=0, to=50, textvariable=self.logo_border_radius_var, width=4, font=(FONT_FAMILY, 9), relief="flat", highlightbackground=COLOR_BORDER, highlightthickness=1).pack(anchor="w", pady=(4, 0))

        tk.Frame(inner, bg=COLOR_BORDER, height=1).pack(fill="x", pady=12)

        # Style & Export settings
        bottom_row = tk.Frame(inner, bg=COLOR_CUSTOMIZE_BG)
        bottom_row.pack(fill="x")

        tk.Checkbutton(bottom_row, text="Use dots instead of squares", variable=self.dots_var, font=(FONT_FAMILY, 9), bg=COLOR_CUSTOMIZE_BG, fg=COLOR_TEXT_PRIMARY, activebackground=COLOR_CUSTOMIZE_BG, highlightthickness=0).pack(anchor="w")
        
        export_row = tk.Frame(inner, bg=COLOR_CUSTOMIZE_BG)
        export_row.pack(fill="x", pady=(10, 0))

        format_frame = tk.Frame(export_row, bg=COLOR_CUSTOMIZE_BG)
        format_frame.pack(side="left", padx=(0, 18))
        tk.Label(format_frame, text="Format:", font=(FONT_FAMILY, 8, "bold"), bg=COLOR_CUSTOMIZE_BG, fg=COLOR_TEXT_SECONDARY).pack(side="left", padx=(0, 6))
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var, values=["PNG", "SVG", "JPEG"], state="readonly", width=5, font=(FONT_FAMILY, 9))
        format_combo.pack(side="left")

        size_frame = tk.Frame(export_row, bg=COLOR_CUSTOMIZE_BG)
        size_frame.pack(side="left")
        tk.Label(size_frame, text="Size (px, optional):", font=(FONT_FAMILY, 8, "bold"), bg=COLOR_CUSTOMIZE_BG, fg=COLOR_TEXT_SECONDARY).pack(side="left", padx=(0, 6))
        
        size_entry = tk.Entry(
            size_frame, textvariable=self.output_size_var, width=6, font=(FONT_FAMILY, 9),
            relief="flat", highlightbackground=COLOR_BORDER, highlightthickness=1
        )
        size_entry.pack(side="left")

        reset_label = tk.Label(inner, text="Reset to defaults", font=(FONT_FAMILY, 8, "underline"), bg=COLOR_CUSTOMIZE_BG, fg=COLOR_TEXT_SECONDARY, cursor="hand2")
        reset_label.pack(anchor="w", pady=(14, 0))
        reset_label.bind("<Button-1>", lambda _e: self._reset_customize())

    def _make_color_field(self, parent, label_text, initial_hex, target):
        field = tk.Frame(parent, bg=COLOR_CUSTOMIZE_BG)
        tk.Label(field, text=label_text, font=(FONT_FAMILY, 8, "bold"), bg=COLOR_CUSTOMIZE_BG, fg=COLOR_TEXT_SECONDARY).pack(anchor="w")

        row = tk.Frame(field, bg=COLOR_CUSTOMIZE_BG)
        row.pack(anchor="w", pady=(4, 0))

        swatch = tk.Label(row, bg=initial_hex, width=3, height=1, relief="flat", highlightbackground=COLOR_BORDER, highlightthickness=1, cursor="hand2")
        swatch.pack(side="left")

        hex_label = tk.Label(row, text=initial_hex.upper(), font=(FONT_FAMILY, 9), bg=COLOR_CUSTOMIZE_BG, fg=COLOR_TEXT_PRIMARY, cursor="hand2")
        hex_label.pack(side="left", padx=(8, 0))

        click_handler = lambda _e=None: self._pick_color(swatch, hex_label, target)
        swatch.bind("<Button-1>", click_handler)
        hex_label.bind("<Button-1>", click_handler)

        return field, swatch, hex_label

    def _pick_color(self, swatch_widget, label_widget, target):
        current = {"fg": self.fg_color, "bg": self.bg_color, "logo_border": self.logo_border_color}[target]
        result = colorchooser.askcolor(color=current, title="Choose a color")
        if not result or not result[1]: return

        hex_color = result[1]
        if target == "fg": self.fg_color = hex_color
        elif target == "bg": self.bg_color = hex_color
        else: self.logo_border_color = hex_color

        swatch_widget.config(bg=hex_color)
        label_widget.config(text=hex_color.upper())

    def _browse_logo(self):
        file_path = filedialog.askopenfilename(title="Choose a logo image", filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")])
        if file_path:
            self.logo_path = file_path
            self.logo_filename_var.set(os.path.basename(file_path))
            self.logo_clear_btn.set_enabled(True)

    def _clear_logo(self):
        self.logo_path = None
        self.logo_filename_var.set("No logo selected")
        self.logo_clear_btn.set_enabled(False)

    def _reset_customize(self):
        self.fg_color = "#000000"
        self.bg_color = "#ffffff"
        self.logo_border_color = "#ffffff"
        self.logo_border_width_var.set(0)
        self.logo_border_radius_var.set(0)
        self.dots_var.set(False)
        self.format_var.set("PNG")
        self.output_size_var.set("")
        self._clear_logo()

        self.fg_swatch.config(bg=self.fg_color)
        self.fg_hex_label.config(text=self.fg_color.upper())
        self.bg_swatch.config(bg=self.bg_color)
        self.bg_hex_label.config(text=self.bg_color.upper())
        self.logo_border_swatch.config(bg=self.logo_border_color)
        self.logo_border_hex_label.config(text=self.logo_border_color.upper())

    def _update_scrollbar_visibility(self, canvas):
        bbox = canvas.bbox("all")
        if not bbox:
            return
        content_height = bbox[3] - bbox[1]
        visible_height = canvas.winfo_height()
        if content_height > visible_height:
            if not self.scrollbar.winfo_ismapped():
                self.scrollbar.pack(side="right", fill="y")
        else:
            if self.scrollbar.winfo_ismapped():
                self.scrollbar.pack_forget()

    def _toggle_customize(self):
        if self.customize_visible:
            self.customize_frame.pack_forget()
            self.customize_toggle_btn.config(text="▸ Customize options & export format")
            self.customize_visible = False
        else:
            self.customize_frame.pack(fill="x", pady=(10, 0), after=self.customize_toggle_btn)
            self.customize_toggle_btn.config(text="▾ Hide customization options")
            self.customize_visible = True
        self.update_idletasks()
        self._sync_scrollregion()

    def _get_parsed_size(self):
        """Helper to safely parse and restrict the custom size input"""
        val = self.output_size_var.get().strip()
        if val.isdigit():
            size = int(val)
            if size > 0:
                if size < 256:
                    self.output_size_var.set("256")
                    messagebox.showinfo("Size Adjusted", "To ensure the QR code remains scannable, the minimum output size has been set to 256px.")
                    return 256
                return size
        return None

    def generate_preview(self):
        data = self.input_var.get().strip()
        if not data:
            messagebox.showwarning("Input required", "Please enter a URL or some text first.")
            self.current_qr_data = "" 
            return
        
        self.current_qr_data = data

        try:
            custom_size = self._get_parsed_size()
            
            img = generate_custom_qr(
                data=data, filename=None, scale=10, output_size=custom_size, border=2,
                fg_color=self.fg_color, bg_color=self.bg_color,
                logo_path=self.logo_path, logo_border_width=self.logo_border_width_var.get(),
                logo_border_color=self.logo_border_color, logo_border_radius=self.logo_border_radius_var.get(),
                dots=self.dots_var.get()
            ).convert("RGB")
        except Exception as exc:
            messagebox.showerror("Generation failed", f"Could not generate QR code:\n{exc}")
            return

        self.current_qr_image = img
        display_img = img.resize((QR_DISPLAY_SIZE, QR_DISPLAY_SIZE), Image.NEAREST)
        self.current_qr_photo = ImageTk.PhotoImage(display_img)

        self.qr_label.config(image=self.current_qr_photo, text="", bg=COLOR_CARD)
        self.qr_canvas_frame.config(bg=COLOR_CARD)

        self.save_btn.set_enabled(True)
        self.copy_btn.set_enabled(True)

    def save_qr(self):
        self.generate_preview() 
        if not self.current_qr_data: return

        fmt = self.format_var.get()
        ext_map = {"PNG": ".png", "SVG": ".svg", "JPEG": ".jpg"}
        ext = ext_map.get(fmt, ".png")

        file_path = filedialog.asksaveasfilename(
            title=f"Save QR Code as {fmt}", 
            defaultextension=ext,
            filetypes=[(f"{fmt} File", f"*{ext}")],
            initialfile=f"qr_code{ext}"
        )
        if not file_path: return

        if not file_path.lower().endswith(ext) and not (ext == ".jpg" and file_path.lower().endswith(".jpeg")):
            file_path += ext

        try:
            custom_size = self._get_parsed_size()
            
            generate_custom_qr(
                data=self.current_qr_data, filename=file_path, scale=10, output_size=custom_size, border=2,
                fg_color=self.fg_color, bg_color=self.bg_color,
                logo_path=self.logo_path, logo_border_width=self.logo_border_width_var.get(),
                logo_border_color=self.logo_border_color, logo_border_radius=self.logo_border_radius_var.get(),
                dots=self.dots_var.get()
            )
            messagebox.showinfo("Success", f"Saved to {os.path.basename(file_path)}")
        except Exception as exc:
            messagebox.showerror("Save failed", f"Could not save file:\n{exc}")

    def copy_qr(self):
        if self.current_qr_image is None: return

        try:
            if sys.platform.startswith("win") and HAS_WIN_CLIPBOARD:
                output = io.BytesIO()
                self.current_qr_image.convert("RGB").save(output, "BMP")
                data = output.getvalue()[14:]
                output.close()
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                win32clipboard.CloseClipboard()
            elif sys.platform == "darwin":
                with tempfile.NamedTemporaryFile(suffix=".tiff", delete=False) as tmp:
                    self.current_qr_image.convert("RGB").save(tmp.name, "TIFF")
                    tmp_path = tmp.name
                subprocess.run(["osascript", "-e", f'set the clipboard to (read (POSIX file "{tmp_path}") as TIFF picture)'], check=True, capture_output=True)
                os.remove(tmp_path)
            elif sys.platform.startswith("linux"):
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    self.current_qr_image.save(tmp.name, "PNG")
                    tmp_path = tmp.name
                if shutil.which("xclip"):
                    with open(tmp_path, "rb") as f:
                        subprocess.run(["xclip", "-selection", "clipboard", "-t", "image/png"], stdin=f, check=True)
                elif shutil.which("wl-copy"):
                    with open(tmp_path, "rb") as f:
                        subprocess.run(["wl-copy", "--type", "image/png"], stdin=f, check=True)
                else:
                    raise RuntimeError("Missing Linux clipboard dependencies.")
                os.remove(tmp_path)
            else:
                raise RuntimeError("no image clipboard support for this platform")
                
            messagebox.showinfo("Copied", "Image copied to clipboard.")
        except RuntimeError:
            messagebox.showerror("Copy Failed", "Please install 'xclip' (X11) or 'wl-clipboard' (Wayland) on Linux to copy images.")
        except Exception as e:
            messagebox.showerror("Copy Failed", f"An error occurred: {e}")

if __name__ == "__main__":
    app = ScanSmithApp()
    app.mainloop()
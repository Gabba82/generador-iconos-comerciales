import re
import tkinter as tk
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageTk


DEFAULTS = {
    "number": "408",
    "size": "512",
    "border": "40",
    "font": "200",
    "background": "#90EE90",
    "text_color": "#000000",
    "border_color": "#000000",
}

ICO_SIZES = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
FILENAME_SAFE_RE = re.compile(r"[^A-Za-z0-9_-]+")


def load_font(font_size):
    for font_name in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(font_name, font_size)
        except OSError:
            pass
    return ImageFont.load_default()


def text_bounds(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox, bbox[2] - bbox[0], bbox[3] - bbox[1]


def fit_font(draw, text, max_width, max_height, preferred_size):
    size = max(8, preferred_size)

    while size > 8:
        font = load_font(size)
        _, width, height = text_bounds(draw, text, font)
        if width <= max_width and height <= max_height:
            return font
        size -= 2

    return load_font(8)


def clean_filename(text):
    clean = FILENAME_SAFE_RE.sub("_", text.strip())
    return clean.strip("_") or "icono"


def parse_settings(text=None):
    number = (text if text is not None else number_input.get()).strip()
    if not number:
        raise ValueError("Introduce el número del comercial.")

    try:
        icon_size = int(size_input.get())
        border_width = int(border_input.get())
        preferred_font_size = int(font_input.get())
    except ValueError as exc:
        raise ValueError("Tamaño, borde y fuente deben ser números enteros.") from exc

    if icon_size < 64:
        raise ValueError("El tamaño del icono debe ser de al menos 64 px.")
    if border_width < 0:
        raise ValueError("El grosor del borde no puede ser negativo.")
    if border_width >= icon_size // 2:
        raise ValueError("El grosor del borde debe ser menor que la mitad del icono.")
    if preferred_font_size < 8:
        raise ValueError("El tamaño de fuente debe ser de al menos 8 px.")

    background_color = background_input.get().strip()
    text_color = text_color_input.get().strip()
    border_color = border_color_input.get().strip()

    for label, value in (
        ("color de fondo", background_color),
        ("color del número", text_color),
        ("color del borde", border_color),
    ):
        try:
            ImageColor.getrgb(value)
        except ValueError as exc:
            raise ValueError(f"El {label} no es válido: {value}") from exc

    return {
        "text": number,
        "icon_size": icon_size,
        "border_width": border_width,
        "preferred_font_size": preferred_font_size,
        "background_color": background_color,
        "text_color": text_color,
        "border_color": border_color,
    }


def create_icon(settings):
    icon_size = settings["icon_size"]
    border_width = settings["border_width"]

    icon = Image.new("RGBA", (icon_size, icon_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)

    half_border = max(1, border_width // 2)
    circle_box = (
        half_border,
        half_border,
        icon_size - half_border - 1,
        icon_size - half_border - 1,
    )

    draw.ellipse(
        circle_box,
        fill=settings["background_color"],
        outline=settings["border_color"],
        width=max(1, border_width),
    )

    padding = border_width + max(10, icon_size // 14)
    max_text_width = max(8, icon_size - padding * 2)
    max_text_height = max(8, icon_size - padding * 2)
    font = fit_font(
        draw,
        settings["text"],
        max_text_width,
        max_text_height,
        settings["preferred_font_size"],
    )

    bbox, text_width, text_height = text_bounds(draw, settings["text"], font)
    text_x = (icon_size - text_width) / 2 - bbox[0]
    text_y = (icon_size - text_height) / 2 - bbox[1]

    draw.text((text_x, text_y), settings["text"], font=font, fill=settings["text_color"])
    return icon


def save_icon(icon, save_path):
    suffix = Path(save_path).suffix.lower()
    if suffix == ".ico":
        icon.save(save_path, format="ICO", sizes=ICO_SIZES)
    else:
        icon.save(save_path, format="PNG")


def make_checkerboard(size, square=12):
    preview = Image.new("RGBA", (size, size), "#ffffff")
    draw = ImageDraw.Draw(preview)

    for y in range(0, size, square):
        for x in range(0, size, square):
            if (x // square + y // square) % 2 == 0:
                draw.rectangle((x, y, x + square - 1, y + square - 1), fill="#e9e9e9")

    return preview


def update_preview(*_):
    global preview_photo

    try:
        settings = parse_settings()
        icon = create_icon(settings)
        preview_size = 280
        preview_icon = icon.copy()
        preview_icon.thumbnail((preview_size, preview_size), Image.Resampling.LANCZOS)

        preview = make_checkerboard(preview_size)
        x = (preview_size - preview_icon.width) // 2
        y = (preview_size - preview_icon.height) // 2
        preview.alpha_composite(preview_icon, (x, y))

        preview_photo = ImageTk.PhotoImage(preview)
        preview_canvas.delete("all")
        preview_canvas.create_image(preview_size // 2, preview_size // 2, image=preview_photo)
        status_label.config(text="Vista previa actualizada", fg="#2f6f3e")
    except Exception as exc:
        preview_canvas.delete("all")
        preview_canvas.create_text(140, 140, text="Sin vista previa", fill="#555555")
        status_label.config(text=str(exc), fg="#b00020")


def generate_icon():
    try:
        settings = parse_settings()
        icon = create_icon(settings)
        default_name = f"{clean_filename(settings['text'])}_icono.png"
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=default_name,
            filetypes=[("PNG", "*.png"), ("Icono de Windows", "*.ico")],
        )
        if save_path:
            save_icon(icon, save_path)
            messagebox.showinfo("Éxito", f"Icono generado:\n{save_path}")
    except Exception as exc:
        messagebox.showerror("Error", str(exc))


def generate_batch():
    raw_numbers = batch_text.get("1.0", tk.END)
    numbers = [line.strip() for line in raw_numbers.replace(",", "\n").splitlines() if line.strip()]

    if not numbers:
        messagebox.showwarning("Lista vacía", "Pega uno o varios números de comercial.")
        return

    output_dir = filedialog.askdirectory(title="Seleccionar carpeta de salida")
    if not output_dir:
        return

    generated = 0
    errors = []

    for number in numbers:
        try:
            settings = parse_settings(number)
            icon = create_icon(settings)
            save_path = Path(output_dir) / f"{clean_filename(number)}_icono.png"
            save_icon(icon, save_path)
            generated += 1
        except Exception as exc:
            errors.append(f"{number}: {exc}")

    if errors:
        messagebox.showwarning(
            "Lote finalizado con avisos",
            f"Iconos generados: {generated}\n\nErrores:\n" + "\n".join(errors[:8]),
        )
    else:
        messagebox.showinfo("Éxito", f"Iconos generados: {generated}")


def choose_color(entry, title):
    color_code = colorchooser.askcolor(title=title, initialcolor=entry.get())[1]
    if color_code:
        entry.delete(0, tk.END)
        entry.insert(0, color_code)
        update_preview()


def reset_defaults():
    for entry, value in (
        (number_input, DEFAULTS["number"]),
        (size_input, DEFAULTS["size"]),
        (border_input, DEFAULTS["border"]),
        (font_input, DEFAULTS["font"]),
        (background_input, DEFAULTS["background"]),
        (text_color_input, DEFAULTS["text_color"]),
        (border_color_input, DEFAULTS["border_color"]),
    ):
        entry.delete(0, tk.END)
        entry.insert(0, value)
    update_preview()


def add_labeled_entry(parent, row, label, default, width=18):
    tk.Label(parent, text=label, anchor="w").grid(row=row, column=0, sticky="w", padx=10, pady=5)
    entry = tk.Entry(parent, width=width)
    entry.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
    entry.insert(0, default)
    entry.bind("<KeyRelease>", update_preview)
    entry.bind("<FocusOut>", update_preview)
    return entry


def main():
    global root
    global preview_photo
    global number_input, size_input, border_input, font_input
    global background_input, text_color_input, border_color_input
    global preview_canvas, status_label, batch_text

    root = tk.Tk()
    root.title("Generador de Iconos")
    root.resizable(False, False)

    preview_photo = None

    main_frame = tk.Frame(root, padx=12, pady=12)
    main_frame.grid(row=0, column=0, sticky="nsew")

    settings_frame = tk.LabelFrame(main_frame, text="Configuración", padx=6, pady=6)
    settings_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
    settings_frame.columnconfigure(1, weight=1)

    number_input = add_labeled_entry(settings_frame, 0, "Número:", DEFAULTS["number"])
    size_input = add_labeled_entry(settings_frame, 1, "Tamaño del icono:", DEFAULTS["size"])
    border_input = add_labeled_entry(settings_frame, 2, "Grosor del borde:", DEFAULTS["border"])
    font_input = add_labeled_entry(settings_frame, 3, "Tamaño máximo de fuente:", DEFAULTS["font"])

    background_input = add_labeled_entry(settings_frame, 4, "Color de fondo:", DEFAULTS["background"])
    tk.Button(
        settings_frame,
        text="Elegir",
        command=lambda: choose_color(background_input, "Seleccionar color de fondo"),
    ).grid(row=4, column=2, padx=10, pady=5)

    text_color_input = add_labeled_entry(settings_frame, 5, "Color del número:", DEFAULTS["text_color"])
    tk.Button(
        settings_frame,
        text="Elegir",
        command=lambda: choose_color(text_color_input, "Seleccionar color del número"),
    ).grid(row=5, column=2, padx=10, pady=5)

    border_color_input = add_labeled_entry(settings_frame, 6, "Color del borde:", DEFAULTS["border_color"])
    tk.Button(
        settings_frame,
        text="Elegir",
        command=lambda: choose_color(border_color_input, "Seleccionar color del borde"),
    ).grid(row=6, column=2, padx=10, pady=5)

    button_frame = tk.Frame(settings_frame)
    button_frame.grid(row=7, column=0, columnspan=3, sticky="ew", padx=10, pady=(10, 4))

    tk.Button(button_frame, text="Generar icono", command=generate_icon, bg="#237a3b", fg="white").grid(
        row=0, column=0, sticky="ew", padx=(0, 6)
    )
    tk.Button(button_frame, text="Restablecer", command=reset_defaults).grid(row=0, column=1, sticky="ew")
    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)

    preview_frame = tk.LabelFrame(main_frame, text="Vista previa", padx=10, pady=10)
    preview_frame.grid(row=0, column=1, sticky="nsew")

    preview_canvas = tk.Canvas(
        preview_frame,
        width=280,
        height=280,
        bg="#f3f3f3",
        highlightthickness=1,
        highlightbackground="#c9c9c9",
    )
    preview_canvas.grid(row=0, column=0, padx=4, pady=4)

    status_label = tk.Label(preview_frame, text="", anchor="center")
    status_label.grid(row=1, column=0, sticky="ew", pady=(8, 0))

    batch_frame = tk.LabelFrame(main_frame, text="Generación por lote", padx=10, pady=10)
    batch_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0))

    tk.Label(batch_frame, text="Números separados por líneas o comas:", anchor="w").grid(
        row=0, column=0, sticky="w"
    )
    batch_text = tk.Text(batch_frame, width=56, height=5)
    batch_text.grid(row=1, column=0, sticky="ew", pady=6)
    tk.Button(batch_frame, text="Generar lote en carpeta", command=generate_batch).grid(
        row=2, column=0, sticky="ew"
    )

    update_preview()
    root.mainloop()


if __name__ == "__main__":
    main()

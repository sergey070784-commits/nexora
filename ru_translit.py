import tkinter as tk
import pyperclip

M = {
    "shch": "\u0449", "sch": "\u0449","eh": "\u044d",
    "yo": "\u0451", "zh": "\u0436", "kh": "\u0445",
    "ts": "\u0446", "ch": "\u0447", "sh": "\u0448",
    "yu": "\u044e", "ya": "\u044f",

    "a": "\u0430", "b": "\u0431", "v": "\u0432", "g": "\u0433",
    "d": "\u0434", "e": "\u0435", "z": "\u0437", "i": "\u0438",
    "j": "\u0439", "k": "\u043a", "l": "\u043b", "m": "\u043c",
    "n": "\u043d", "o": "\u043e", "p": "\u043f", "r": "\u0440",
    "s": "\u0441", "t": "\u0442", "u": "\u0443", "f": "\u0444",
    "h": "\u0445", "c": "\u0446", "y": "\u044b", "w": "\u0432",
    "x": "\u043a\u0441", "q": "\u043a",
    "'": "\u044c", "`": "\u044a"
}


def transliterate(text):
    result = []
    i = 0
    keys = sorted(M.keys(), key=len, reverse=True)

    while i < len(text):
        tail = text[i:].lower()

        for key in keys:
            if tail.startswith(key):
                value = M[key]

                if text[i].isupper():
                    value = value.capitalize()

                result.append(value)
                i += len(key)
                break
        else:
            result.append(text[i])
            i += 1

    return "".join(result)


def update_result(event=None):
    output_box.delete("1.0", "end")

    text = input_box.get("1.0", "end-1c")
    output_box.insert("1.0", transliterate(text))


def copy_result(event=None):
    text = output_box.get("1.0", "end-1c")

    if text.strip():
        pyperclip.copy(text)

        input_box.delete("1.0", "end")
        output_box.delete("1.0", "end")

        input_box.focus_set()

    return "break"


def clear_all():
    input_box.delete("1.0", "end")
    output_box.delete("1.0", "end")
    input_box.focus_set()


# =========================
# WINDOW
# =========================

root = tk.Tk()

root.title("RU Translit")
root.geometry("650x560")
root.minsize(500, 480)
root.configure(bg="#f4f4f4")


# =========================
# TITLE
# =========================

title = tk.Label(
    root,
    text="RU Translit",
    font=("Segoe UI", 18, "bold"),
    bg="#f4f4f4"
)

title.pack(
    anchor="w",
    padx=22,
    pady=(18, 8)
)


# =========================
# INPUT
# =========================

tk.Label(
    root,
    text="Type in English letters:",
    font=("Segoe UI", 10),
    bg="#f4f4f4"
).pack(
    anchor="w",
    padx=22
)


input_box = tk.Text(
    root,
    height=7,
    font=("Segoe UI", 13),
    wrap="word",
    relief="solid",
    borderwidth=1
)

input_box.pack(
    fill="x",
    padx=22,
    pady=(5, 12)
)

input_box.bind(
    "<KeyRelease>",
    update_result
)

input_box.bind(
    "<Control-Return>",
    copy_result
)


# =========================
# OUTPUT
# =========================

tk.Label(
    root,
    text="Russian:",
    font=("Segoe UI", 10),
    bg="#f4f4f4"
).pack(
    anchor="w",
    padx=22
)


output_box = tk.Text(
    root,
    height=7,
    font=("Segoe UI", 13),
    wrap="word",
    relief="solid",
    borderwidth=1,
    bg="white"
)

output_box.pack(
    fill="x",
    padx=22,
    pady=(5, 12)
)


# =========================
# BUTTONS
# =========================

button_frame = tk.Frame(
    root,
    bg="#f4f4f4"
)

button_frame.pack(
    fill="x",
    padx=22,
    pady=(0, 18)
)


copy_button = tk.Button(
    button_frame,
    text="Copy",
    command=copy_result,
    font=("Segoe UI", 11, "bold"),
    width=10,
    height=2
)

copy_button.pack(
    side="left"
)


clear_button = tk.Button(
    button_frame,
    text="Clear",
    command=clear_all,
    font=("Segoe UI", 11),
    width=10,
    height=2
)

clear_button.pack(
    side="left",
    padx=(10, 0)
)


# Start in input field
input_box.focus_set()

root.mainloop()
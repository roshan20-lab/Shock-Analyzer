import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
import math


# ============================================================
# BACKEND SETTINGS
# ============================================================

FILE_NAME = "Shock_Report.csv"
ROOM_TEMPERATURE_K = 298.15
BAR_TO_PA = 1e5

# gamma, specific gas constant R [J/(kg K)]
GAS_PROPERTIES = {
    "N₂": (1.400, 296.80),
    "Ar": (1.667, 208.13)
}

last_calc = {}


# ============================================================
# BACKEND CALCULATIONS
# ============================================================

def get_sound_speed():

    gamma, R = GAS_PROPERTIES[driven_gas_var.get()]

    sound_speed = math.sqrt(
        gamma * R * ROOM_TEMPERATURE_K
    )

    return gamma, sound_speed


def calculate_reflected_shock(gamma, mach, pressure_bar):

    # Convert driven pressure P1 from bar to Pa
    pressure_p1_pa = pressure_bar * BAR_TO_PA

    M2 = mach ** 2

    # --------------------------------------------------------
    # P5 / P1
    # --------------------------------------------------------

    pressure_ratio = (
        (2 * gamma * M2 - (gamma - 1))
        / (gamma + 1)
    ) * (
        ((3 * gamma - 1) * M2
         - 2 * (gamma - 1))
        / ((gamma - 1) * M2 + 2)
    )

    pressure_p5_pa = (
        pressure_ratio * pressure_p1_pa
    )

    # --------------------------------------------------------
    # T5 / T1
    # --------------------------------------------------------

    temperature_ratio = (
        (
            2 * (gamma - 1) * M2
            + (3 - gamma)
        )
        *
        (
            (3 * gamma - 1) * M2
            - 2 * (gamma - 1)
        )
        /
        (
            (gamma + 1) ** 2 * M2
        )
    )

    temperature_p5_k = (
        ROOM_TEMPERATURE_K
        * temperature_ratio
    )

    return (
        pressure_p1_pa,
        pressure_ratio,
        pressure_p5_pa,
        temperature_ratio,
        temperature_p5_k
    )


# ============================================================
# MAIN CALCULATION
# ============================================================

def calculate(event=None):

    try:

        distance = float(length_var.get())
        time_text = entry_time.get().strip()

        ch1 = float(entry_ch1.get())
        ch2 = float(entry_ch2.get())
        trigger = int(entry_trigger.get())
        t0 = float(entry_t0.get())
        time_scale = float(entry_time_scale.get())

        driver_gas = entry_driver_gas.get().strip()
        driven_gas = driven_gas_var.get()

        diaphragm = entry_diaphragm.get().strip()

        burst_pressure = float(
            entry_bursting_pressure.get()
        )

        driven_pressure = float(
            entry_driven_pressure.get()
        )

        comments = comments_text.get(
            "1.0",
            tk.END
        ).strip()

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if ch1 < 0 or ch2 < 0:
            raise ValueError(
                "CH1 and CH2 cannot be negative."
            )

        if trigger < 0:
            raise ValueError(
                "Trigger cannot be negative."
            )

        if time_scale <= 0:
            raise ValueError(
                "Time Scale must be greater than zero."
            )

        if burst_pressure < 0:
            raise ValueError(
                "Bursting Pressure cannot be negative."
            )

        if driven_pressure < 0:
            raise ValueError(
                "Driven Section Pressure cannot be negative."
            )

        # ----------------------------------------------------
        # GAS PROPERTIES
        # ----------------------------------------------------

        gamma, sound_speed = get_sound_speed()

        # ----------------------------------------------------
        # SHOCK VELOCITY AND MACH NUMBER
        # ----------------------------------------------------

        if time_text:

            time_us = float(time_text)

            if time_us <= 0:
                raise ValueError(
                    "Time Difference must be greater than zero."
                )

            velocity = distance / (
                time_us * 1e-6
            )

            mach = velocity / sound_speed

            velocity = round(
                velocity,
                2
            )

            mach = round(
                mach,
                4
            )

            # ------------------------------------------------
            # REFLECTED SHOCK CALCULATION
            # ------------------------------------------------

            (
                pressure_p1_pa,
                pressure_ratio,
                pressure_p5_pa,
                temperature_ratio,
                temperature_p5_k
            ) = calculate_reflected_shock(
                gamma,
                mach,
                driven_pressure
            )

            # Display results

            label_velocity.config(
                text=f"{velocity:.2f} m/s",
                foreground="#155EEF"
            )

            label_mach.config(
                text=f"{mach:.4f}",
                foreground="#16A34A"
            )

            label_p5.config(
                text=f"{pressure_p5_pa:.2f} Pa",
                foreground="#7C3AED"
            )

            label_t5.config(
                text=f"{temperature_p5_k:.2f} K",
                foreground="#EA580C"
            )

            status_label.config(
                text="Calculation complete • Ready to save",
                foreground="#155EEF"
            )

        else:

            time_us = "N.A."
            velocity = "N.A."
            mach = "N.A."

            pressure_p1_pa = "N.A."
            pressure_ratio = "N.A."
            pressure_p5_pa = "N.A."
            temperature_ratio = "N.A."
            temperature_p5_k = "N.A."

            label_velocity.config(
                text="N.A.",
                foreground="#DC2626"
            )

            label_mach.config(
                text="N.A.",
                foreground="#DC2626"
            )

            label_p5.config(
                text="N.A.",
                foreground="#DC2626"
            )

            label_t5.config(
                text="N.A.",
                foreground="#DC2626"
            )

            status_label.config(
                text=(
                    "Parameters complete • "
                    "Time Difference not entered"
                ),
                foreground="#D97706"
            )

        # ----------------------------------------------------
        # STORE DATA
        # ----------------------------------------------------

        last_calc.clear()

        last_calc.update({

            "Sensor_Dist_m":
                distance,

            "Input_Time_us":
                time_us,

            "CH1_mV":
                ch1,

            "CH2_mV":
                ch2,

            "Trigger_mV":
                trigger,

            "T0_ms":
                t0,

            "Time_Scale_ns":
                time_scale,

            "Driver_Gas":
                driver_gas,

            "Driven_Gas":
                driven_gas,

            "Temperature_K":
                ROOM_TEMPERATURE_K,

            "Gamma":
                gamma,

            "Sound_Speed_mps":
                round(sound_speed, 2),

            "Diaphragm_Thickness_mm":
                diaphragm,

            "Bursting_Pressure_Bar":
                burst_pressure,

            "Driven_Section_Pressure_Bar":
                driven_pressure,

            # Converted driven pressure
            "Driven_Pressure_P1_Pa":
                pressure_p1_pa,

            "Velocity_mps":
                velocity,

            "Mach_Number":
                mach,

            # New calculations
            "P5_P1_Ratio":
                pressure_ratio,

            "P5_Pa":
                pressure_p5_pa,

            "T5_T1_Ratio":
                temperature_ratio,

            "T5_K":
                temperature_p5_k,

            "Comments":
                comments
        })

        btn_save.config(
            state="normal"
        )

    except ValueError as error:

        messagebox.showerror(
            "Invalid Input",
            str(error)
        )


# ============================================================
# SAVE
# ============================================================

def save_to_csv():

    if not last_calc:

        messagebox.showwarning(
            "No Data",
            "Calculate the experiment before saving."
        )

        return

    try:

        record = {
            "Timestamp":
                pd.Timestamp.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            **last_calc
        }

        df = pd.DataFrame([record])

        df.to_csv(
            FILE_NAME,
            mode="a",
            index=False,
            header=not os.path.isfile(FILE_NAME)
        )

        status_label.config(
            text=f"Saved successfully • {FILE_NAME}",
            foreground="#16A34A"
        )

        reset_fields()

    except PermissionError:

        messagebox.showwarning(
            "File Locked",
            "Close the CSV file before saving."
        )


# ============================================================
# RESET
# ============================================================

def reset_fields():

    for entry in (
        entry_time,
        entry_trigger,
        entry_t0,
        entry_time_scale,
        entry_diaphragm,
        entry_bursting_pressure,
        entry_driven_pressure
    ):
        entry.delete(0, tk.END)

    entry_ch1.delete(0, tk.END)
    entry_ch1.insert(0, "100")

    entry_ch2.delete(0, tk.END)
    entry_ch2.insert(0, "100")

    entry_driver_gas.delete(0, tk.END)
    entry_driver_gas.insert(0, "He")

    driven_gas_var.set("Ar")

    comments_text.delete(
        "1.0",
        tk.END
    )

    label_velocity.config(
        text="—",
        foreground="#64748B"
    )

    label_mach.config(
        text="—",
        foreground="#64748B"
    )

    label_p5.config(
        text="—",
        foreground="#64748B"
    )

    label_t5.config(
        text="—",
        foreground="#64748B"
    )

    btn_save.config(
        state="disabled"
    )

    last_calc.clear()

    entry_time.focus_set()


# ============================================================
# WINDOW
# ============================================================

root = tk.Tk()

root.title("Shock Analyzer")

root.geometry("760x720")
root.minsize(720, 680)

root.configure(
    bg="#F1F5F9"
)

root.bind(
    "<Return>",
    calculate
)


# ============================================================
# STYLE
# ============================================================

style = ttk.Style(root)

try:
    style.theme_use("clam")
except tk.TclError:
    pass

style.configure(
    "TEntry",
    padding=5,
    font=("Segoe UI", 9)
)

style.configure(
    "TRadiobutton",
    font=("Segoe UI", 9),
    background="#FFFFFF"
)

style.configure(
    "Section.TLabelframe",
    background="#FFFFFF",
    borderwidth=1,
    relief="solid"
)

style.configure(
    "Section.TLabelframe.Label",
    background="#FFFFFF",
    foreground="#1E293B",
    font=("Segoe UI", 9, "bold")
)

style.configure(
    "Primary.TButton",
    font=("Segoe UI", 9, "bold"),
    padding=(18, 7),
    foreground="white",
    background="#2563EB"
)

style.map(
    "Primary.TButton",
    background=[
        ("active", "#1D4ED8"),
        ("pressed", "#1E40AF")
    ]
)

style.configure(
    "Save.TButton",
    font=("Segoe UI", 9, "bold"),
    padding=(18, 7),
    foreground="white",
    background="#16A34A"
)

style.map(
    "Save.TButton",
    background=[
        ("active", "#15803D"),
        ("pressed", "#166534")
    ]
)


# ============================================================
# MAIN CONTAINER
# ============================================================

main = tk.Frame(
    root,
    bg="#F1F5F9"
)

main.pack(
    fill="both",
    expand=True,
    padx=16,
    pady=10
)


# ============================================================
# HEADER
# ============================================================

header = tk.Frame(
    main,
    bg="#17324D",
    height=60
)

header.pack(
    fill="x",
    pady=(0, 8)
)

header.pack_propagate(False)

tk.Label(
    header,
    text="SHOCK ANALYZER",
    font=("Segoe UI", 15, "bold"),
    foreground="white",
    background="#17324D"
).pack(
    anchor="w",
    padx=18,
    pady=(8, 0)
)

tk.Label(
    header,
    text="Experimental shock-wave measurement and analysis",
    font=("Segoe UI", 8),
    foreground="#CBD5E1",
    background="#17324D"
).pack(
    anchor="w",
    padx=19
)


# ============================================================
# MEASUREMENT
# ============================================================

measurement = ttk.LabelFrame(
    main,
    text="  Measurement  ",
    style="Section.TLabelframe",
    padding=7
)

measurement.pack(
    fill="x",
    pady=(0, 7)
)

measurement.columnconfigure(
    4,
    weight=1
)


tk.Label(
    measurement,
    text="Sensor Distance",
    font=("Segoe UI", 9, "bold"),
    bg="#FFFFFF",
    fg="#334155"
).grid(
    row=0,
    column=0,
    padx=(2, 8)
)

length_var = tk.StringVar(
    value="0.50"
)

ttk.Radiobutton(
    measurement,
    text="0.25 m",
    variable=length_var,
    value="0.25"
).grid(
    row=0,
    column=1,
    sticky="w"
)

ttk.Radiobutton(
    measurement,
    text="0.50 m",
    variable=length_var,
    value="0.50"
).grid(
    row=0,
    column=2,
    sticky="w",
    padx=(8, 20)
)


tk.Label(
    measurement,
    text="Time Difference",
    font=("Segoe UI", 9, "bold"),
    bg="#FFFFFF",
    fg="#334155"
).grid(
    row=0,
    column=3,
    padx=(8, 7)
)

entry_time = ttk.Entry(
    measurement,
    width=13
)

entry_time.grid(
    row=0,
    column=4,
    sticky="ew"
)

tk.Label(
    measurement,
    text="μs          ",
    font=("Segoe UI", 8),
    bg="#FFFFFF",
    fg="#64748B"
).grid(
    row=0,
    column=5,
    padx=(6, 2)
)


# ============================================================
# EXPERIMENTAL PARAMETERS
# ============================================================

params = ttk.LabelFrame(
    main,
    text="  Experimental Parameters  ",
    style="Section.TLabelframe",
    padding=7
)

params.pack(
    fill="x",
    pady=(0, 7)
)

for col in (1, 3, 5):
    params.columnconfigure(
        col,
        weight=1
    )


def add_label(text, row, col):

    tk.Label(
        params,
        text=text,
        font=("Segoe UI", 8),
        bg="#FFFFFF",
        fg="#475569"
    ).grid(
        row=row,
        column=col,
        sticky="e",
        padx=3,
        pady=3
    )


def add_entry(row, col, default=""):

    entry = ttk.Entry(
        params,
        width=10
    )

    if default:
        entry.insert(
            0,
            default
        )

    entry.grid(
        row=row,
        column=col,
        sticky="ew",
        padx=3,
        pady=3
    )

    return entry


# Row 0

add_label("CH1 (mV)", 0, 0)
entry_ch1 = add_entry(0, 1, "100")

add_label("CH2 (mV)", 0, 2)
entry_ch2 = add_entry(0, 3, "100")

add_label("Trigger (mV)", 0, 4)
entry_trigger = add_entry(0, 5)


# Row 1

add_label("T0 (ms)", 1, 0)
entry_t0 = add_entry(1, 1)

add_label("Time Scale (μs)", 1, 2)
entry_time_scale = add_entry(1, 3)

add_label("Driver Gas", 1, 4)
entry_driver_gas = add_entry(1, 5, "He")


# Row 2

add_label("Driven Gas", 2, 0)

driven_gas_var = tk.StringVar(
    value="Ar"
)

gas_frame = tk.Frame(
    params,
    bg="#FFFFFF"
)

gas_frame.grid(
    row=2,
    column=1,
    sticky="w"
)

ttk.Radiobutton(
    gas_frame,
    text="N₂",
    variable=driven_gas_var,
    value="N₂"
).pack(
    side="left"
)

ttk.Radiobutton(
    gas_frame,
    text="Ar",
    variable=driven_gas_var,
    value="Ar"
).pack(
    side="left",
    padx=(10, 0)
)


add_label("Diaphragm (mm)", 2, 2)
entry_diaphragm = add_entry(2, 3)

add_label("Burst Pressure (Bar)", 2, 4)
entry_bursting_pressure = add_entry(2, 5)


# Row 3

add_label("Driven Pressure (Bar)", 3, 0)

entry_driven_pressure = add_entry(
    3,
    1
)


# ============================================================
# COMMENTS
# ============================================================

comments_frame = ttk.LabelFrame(
    main,
    text="  Comments  ",
    style="Section.TLabelframe",
    padding=6
)

comments_frame.pack(
    fill="x",
    pady=(0, 7)
)

comments_text = tk.Text(
    comments_frame,
    height=2,
    font=("Segoe UI", 9),
    relief="solid",
    borderwidth=1,
    highlightthickness=0,
    wrap="word"
)

comments_text.pack(
    fill="x"
)


# ============================================================
# BUTTONS
# ============================================================

button_frame = tk.Frame(
    main,
    bg="#F1F5F9"
)

button_frame.pack(
    pady=(0, 7)
)

ttk.Button(
    button_frame,
    text="Calculate",
    style="Primary.TButton",
    command=calculate
).pack(
    side="left",
    padx=5
)

btn_save = ttk.Button(
    button_frame,
    text="Save Result",
    style="Save.TButton",
    command=save_to_csv,
    state="disabled"
)

btn_save.pack(
    side="left",
    padx=5
)


# ============================================================
# RESULTS
# ============================================================

results = tk.Frame(
    main,
    bg="#FFFFFF",
    highlightbackground="#CBD5E1",
    highlightthickness=1
)

results.pack(
    fill="x",
    pady=(0, 7)
)

for col in (1, 3):
    results.columnconfigure(
        col,
        weight=1
    )


tk.Label(
    results,
    text="RESULTS",
    font=("Segoe UI", 8, "bold"),
    bg="#FFFFFF",
    fg="#64748B"
).grid(
    row=0,
    column=0,
    columnspan=4,
    sticky="w",
    padx=12,
    pady=(6, 2)
)


# Velocity

tk.Label(
    results,
    text="Velocity",
    font=("Segoe UI", 8),
    bg="#FFFFFF",
    fg="#64748B"
).grid(
    row=1,
    column=0,
    padx=(12, 4),
    pady=(0, 7)
)

label_velocity = tk.Label(
    results,
    text="—",
    font=("Segoe UI", 11, "bold"),
    bg="#FFFFFF",
    fg="#64748B"
)

label_velocity.grid(
    row=1,
    column=1,
    sticky="w",
    padx=4,
    pady=(0, 7)
)


# Mach

tk.Label(
    results,
    text="Mach Number",
    font=("Segoe UI", 8),
    bg="#FFFFFF",
    fg="#64748B"
).grid(
    row=1,
    column=2,
    padx=(10, 4),
    pady=(0, 7)
)

label_mach = tk.Label(
    results,
    text="—",
    font=("Segoe UI", 12, "bold"),
    bg="#FFFFFF",
    fg="#64748B"
)

label_mach.grid(
    row=1,
    column=3,
    sticky="w",
    padx=4,
    pady=(0, 7)
)


# P5

tk.Label(
    results,
    text="P₅",
    font=("Segoe UI", 8),
    bg="#FFFFFF",
    fg="#64748B"
).grid(
    row=2,
    column=0,
    padx=(12, 4),
    pady=(0, 7)
)

label_p5 = tk.Label(
    results,
    text="—",
    font=("Segoe UI", 11, "bold"),
    bg="#FFFFFF",
    fg="#64748B"
)

label_p5.grid(
    row=2,
    column=1,
    sticky="w",
    padx=4,
    pady=(0, 7)
)


# T5

tk.Label(
    results,
    text="T₅",
    font=("Segoe UI", 8),
    bg="#FFFFFF",
    fg="#64748B"
).grid(
    row=2,
    column=2,
    padx=(10, 4),
    pady=(0, 7)
)

label_t5 = tk.Label(
    results,
    text="—",
    font=("Segoe UI", 11, "bold"),
    bg="#FFFFFF",
    fg="#64748B"
)

label_t5.grid(
    row=2,
    column=3,
    sticky="w",
    padx=4,
    pady=(0, 7)
)


# ============================================================
# STATUS
# ============================================================

status_frame = tk.Frame(
    main,
    bg="#E2E8F0",
    height=25
)

status_frame.pack(
    fill="x"
)

status_frame.pack_propagate(False)

status_label = tk.Label(
    status_frame,
    text="Ready for measurement",
    font=("Segoe UI", 8),
    bg="#E2E8F0",
    fg="#475569",
    anchor="w"
)

status_label.pack(
    fill="both",
    padx=10
)


# ============================================================
# START
# ============================================================

entry_time.focus_set()

root.mainloop()
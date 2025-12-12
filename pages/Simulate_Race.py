# simulate_race.py (Isaac Acuna)
import time
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
import math

st.set_page_config(page_title="Drag Race Simulation (power model)", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("cars.csv")

cars = load_data()

st.sidebar.header("Select Cars")
car1_name = st.sidebar.selectbox("Car 1", cars["name"])
car2_name = st.sidebar.selectbox("Car 2", cars["name"], index=1)

# prepare car data

car1_row = cars[cars["name"] == car1_name].iloc[0]
car2_row = cars[cars["name"] == car2_name].iloc[0]

img1 = mpimg.imread(car1_row["icon"])
img2 = mpimg.imread(car2_row["icon"])

TRACK_LEN = 402.336  # meters (quarter mile)
st.title("Drag Race – Power-based Physics (Quarter mile)")

# --- helpers to prepare car parameters ---
def parse_float(x):
    try:
        return float(str(x).strip())
    except:
        return 0.0

def prep_car(row): #function to prepare car parameters in variables
    hp = parse_float(row['horsepower'])
    weight_lbs = parse_float(row['weight_lbs'])
    top_speed_mph = parse_float(row['top_speed_mph'])
    zero_to_60 = parse_float(row['acceleration_0_60'])

    mass = weight_lbs * 0.45359237  # kg
    top_speed_mps = top_speed_mph * 0.44704


    drivetrain_eff = 0.85
    P_wheel = max(1.0, hp) * 745.699872 * drivetrain_eff
    Cd = 0.33
    # estimate frontal area A from weight heuristic
    A = 2.0 + (weight_lbs - 3000.0) / 2500.0
    A = max(1.6, min(2.6, A))

    # rolling resistance
    Crr = 0.015

    
    # compute average accel needed for 0-60, then scale a bit to approximate peak launch accel.
    if zero_to_60 > 0:
        a_avg = (60 * 0.44704) / zero_to_60
        mu_est = (a_avg * 1.15) / 9.81
        mu_est = max(0.6, min(1.4, mu_est))  # clamp
    else:
        mu_est = 1.0

    return {
        "name": row["name"],
        "hp": hp,
        "mass": mass,
        "top_speed_mps": top_speed_mps,
        "P_wheel": P_wheel,
        "Cd": Cd,
        "A": A,
        "Crr": Crr,
        "mu": mu_est,
        "icon": row["icon"],
        "zero_to_60": zero_to_60
    }

c1 = prep_car(car1_row)
c2 = prep_car(car2_row)

# Show prep info (helpful for debugging / tuning)
with st.expander("Car parameters (estimated)"):
    st.write(c1)
    st.write(c2)

# Physics constants and params
rho = 1.225  
g = 9.81 # m/s²

# Simulation params
dt = 0.075    # small dt for accuracy
max_time = 30.0  # safety cap

# state
pos1 = pos2 = 0.0
v1 = v2 = 0.0
t = 0.0

# UI placeholders
plot_ph = st.empty()
stats_ph = st.empty()

# countdown
count = st.empty()
for s in ["3", "2", "1", "GO!"]:
    count.markdown(f"## **{s}**")
    time.sleep(0.5)
count.empty()

plot_interval = 4  # plot every 4*dt = 0.04s
step = 0

winner = None
t_list = []
p1_list = []
p2_list = []
v1_list = []
v2_list = []

def step_car(c, v, pos): #function to step car physics across 
    """
    returns (v_new, pos_new, a, F_tractive, F_drag, F_roll)
    Model:
      F_drag = 0.5 * rho * Cd * A * v^2
      F_roll = Crr * mass * g
      F_power = P / v  (use v_floor to avoid division by zero)
      F_traction_limit = mu * mass * g
      F_tractive = min(F_power, F_traction_limit)
      F_net = F_tractive - F_drag - F_roll
      a = F_net / mass
    """
    mass = c["mass"]
    Cd = c["Cd"]
    A = c["A"]
    Crr = c["Crr"]
    mu = c["mu"]
    P = c["P_wheel"]

    # forces
    F_drag = 0.5 * rho * Cd * A * v * v
    F_roll = Crr * mass * g

    
    v_for_div = max(v, 0.5)  # treat very low speeds with v_floor => P/v very large but traction caps it
    F_power = P / v_for_div

    F_traction_limit = mu * mass * g

    F_tractive = min(F_power, F_traction_limit)

    F_net = F_tractive - F_drag - F_roll

    a = F_net / mass
    # allow small negative acceleration but avoid flipping sign too large at v ~0
    v_new = max(0.0, v + a * dt)
    pos_new = pos + v_new * dt
    return v_new, pos_new, a, F_tractive, F_drag, F_roll

# simulation loop
while t < max_time:
    v1, pos1, a1, F1, D1, R1 = step_car(c1, v1, pos1)
    v2, pos2, a2, F2, D2, R2 = step_car(c2, v2, pos2)

    # cap by top speed
    v1 = min(v1, c1["top_speed_mps"])
    v2 = min(v2, c2["top_speed_mps"])

    t += dt
    step += 1

    # sample for plotting/stats
    if step % plot_interval == 0:
        t_list.append(t)
        p1_list.append(pos1)
        p2_list.append(pos2)
        v1_list.append(v1)
        v2_list.append(v2)

        # draw
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.set_xlim(0, TRACK_LEN)
        ax.set_ylim(0, 3)
        ax.get_yaxis().set_visible(False)
        ax.plot([TRACK_LEN, TRACK_LEN], [0, 3], "k--")
        ax.add_artist(AnnotationBbox(OffsetImage(mpimg.imread(c1["icon"]), zoom=0.06), (pos1, 2), frameon=False))
        ax.add_artist(AnnotationBbox(OffsetImage(mpimg.imread(c2["icon"]), zoom=0.06), (pos2, 1), frameon=False))
        plot_ph.pyplot(fig)

        stats_ph.markdown(
            f"""
            ### Live
            **{c1['name']}** — {pos1:.1f} m — {(v1/0.44704):.1f} mph  
            **{c2['name']}** — {pos2:.1f} m — {(v2/0.44704):.1f} mph  
            **Time:** {t:.2f} s
            """
        )

    # finish check
    if pos1 >= TRACK_LEN or pos2 >= TRACK_LEN:
        if pos1 >= TRACK_LEN and pos2 >= TRACK_LEN:
            winner = c1["name"] if pos1 > pos2 else c2["name"]
        else:
            winner = c1["name"] if pos1 >= TRACK_LEN else c2["name"]
        break

# final
if winner is None:
    winner = c1["name"] if pos1 > pos2 else c2["name"]

st.success(f"🏁 Winner: {winner} — elapsed: {t:.2f} s")
st.write(f"Final distances — {c1['name']}: {pos1:.1f} m, {c2['name']}: {pos2:.1f} m")
st.write(f"Final speeds — {c1['name']}: {(v1/0.44704):.1f} mph, {c2['name']}: {(v2/0.44704):.1f} mph")
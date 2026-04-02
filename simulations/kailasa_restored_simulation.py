import sympy as sp

# Exact symbolic constants (no rounding)
five_thirds = sp.Rational(5, 3)
delta_0 = 0
Y = 360  # clean 360-day grid
speed_of_sound = 343  # m/s

# Kailasa dimensions (exact archaeological)
length = 60  # m
width = 30   # m
depth = 30   # m

# Torsional debt (exact)
delta = five_thirds * sp.Abs(Y - 360) / sp.Rational(21, 4)  # 5.25 = 21/4
print(f"Torsional debt δ (restored): {delta} ms")

# Efficiency
eta = 100 * sp.exp(-sp.Rational(1, 10) * delta)
print(f"Phase-lock efficiency η: {eta}%")

# Acoustic cavity modes (exact)
f_x = speed_of_sound / (2 * length)
f_y = speed_of_sound / (2 * width)
f_z = speed_of_sound / (2 * depth)

print(f"Fundamental mode along length (60 m): {float(f_x):.4f} Hz")
print(f"Fundamental mode along width/depth (30 m): {float(f_y):.4f} Hz")

# Check harmonic relationship to 5/3 Hz bridge
bridge = five_thirds
print(f"5/3 Hz bridge frequency: {float(bridge):.4f} Hz")
print(f"Ratio f_x / bridge: {float(f_x / bridge):.4f}")
print(f"Ratio f_y / bridge: {float(f_y / bridge):.4f}")

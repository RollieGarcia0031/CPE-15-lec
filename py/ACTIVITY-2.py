import numpy as np

def print_separator():
    print("\n- - - - - - - - - - - - - -\n")

raw_readings = np.array([
    [512, 208, 715, 1005],
    [518, 203, 728, 1012],
    [505, 210, 705,  998],
    [522, 199, 733, 1020],
    [509, 206, 718, 1003],
    [515, 990, 722, 1008],
    [520, 201, 710,  995],
    [507, 207, 726, 1015],
    [513, 204, 719, 1006],
    [519, 202, 731, 1018],
    [504, 209, 708,  999],
    [516, 205, 720,   15],
], dtype=float)

readings_scale_factor = np.array([0.0125, 0.005, 0.0075, 0.08])
readings_offset = np.array([0.02, 0.1, -0.1, 0.2])

calibrated_readings = (raw_readings * readings_scale_factor) + readings_offset

print_separator();
print("Calibrated readings: \n")
print(calibrated_readings)
print_separator();

lower_bounds = np.array([5.0, 1.0, 5.0, 70.0])
upper_bounds = np.array([7.0, 4.0, 6.0, 90.0])

valid_reading_mask = (calibrated_readings >= lower_bounds) & (calibrated_readings <= upper_bounds)

print_separator()
print("Valid Readings")
print(valid_reading_mask)
print_separator()

valid_rows = valid_reading_mask.sum(axis=0)
rejected_rows = (~valid_reading_mask).sum(axis=0)
mean_readings = calibrated_readings.mean(axis=0)
std_readings = calibrated_readings.std(axis=0)

report = {
    "Valid readings" : valid_rows.tolist(),
    "Rejected readings" : rejected_rows.tolist(),
    "Statistics": {
        "Mean" : mean_readings,
        "Standard Deviation": std_readings
    }
}

actual_total_readings = calibrated_readings.sum(axis=0)
rejected_total_readings = np.where(~valid_reading_mask, calibrated_readings, 0).sum(axis=0)
accepted_total_readings = np.where(valid_reading_mask, calibrated_readings, 0).sum(axis=0)

collected_total_readings = accepted_total_readings + rejected_total_readings

assert np.array_equal(actual_total_readings, collected_total_readings)

print_separator()
report
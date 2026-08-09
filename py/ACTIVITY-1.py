env_readings = [
    {"station": "ENV-01", "temperature_c": 27.3, "humidity_pct": 65, "pm25_ugm3": 12.4},
    {"station": "ENV-02", "temperature_c": 29.8, "humidity_pct": 70, "pm25_ugm3": 18.9},
    {"station": "ENV-03", "temperature_c": 31.1, "humidity_pct": 58, "pm25_ugm3": 9.7},
    {"station": "ENV-04", "temperature_c": None,  "humidity_pct": 62, "pm25_ugm3": 15.2},
    {"station": "ENV-05", "temperature_c": 28.6, "humidity_pct": 130, "pm25_ugm3": 11.0},
    {"station": "ENV-06", "temperature_c": 26.9, "humidity_pct": 74, "pm25_ugm3": 22.5},
    {"station": "ENV-07", "temperature_c": None, "humidity_pct": 110, "pm25_ugm3": 8.3},
    {"station": "ENV-08", "temperature_c": 27.7, "humidity_pct": 68, "pm25_ugm3": 14.1},
]

def validate_env_record(row: dict) -> list:
    error_messages = []

    if row["temperature_c"] is None:
        error_messages.append("Missing temperature")

    if row["humidity_pct"] is None:
        error_messages.append("Missing humidity")

    humidity_is_out_of_bounds = row["humidity_pct"] is not None and not (0 <= row["humidity_pct"] <= 100)
    if humidity_is_out_of_bounds:
        error_messages.append("Humidity out of bounds (0-100)")

    temperature_is_out_of_bounds = row["temperature_c"] is not None and not (-10 <= row["temperature_c"] <= 60)
    if temperature_is_out_of_bounds:
        error_messages.append("Temperature out of bounds (-10 to 60)")

    return error_messages

def get_mean(items, amount):
    try:
        return sum(items) / amount
    except ZeroDivisionError:
        return None

def rounded_value(value):
    return round(value, 2) if value is not None else None;

for row in env_readings:
    row["errors"] = validate_env_record(row)

for row in env_readings:
    status = "usable" if not row["errors"] else ", ".join(row["errors"])
    print(row["station"], "->", status)

usable_rows = list(filter(lambda row: len(row["errors"]) <= 0, env_readings))
usable_temperatures = list(map(lambda row: row["temperature_c"], usable_rows))
usable_pm25 = list(map(lambda row: row["pm25_ugm3"], usable_rows))

total_records = len(env_readings)
usable_count = len(usable_rows)
rejected_count = total_records - usable_count

mean_usable_temp = get_mean(usable_temperatures, usable_count)
mean_usable_pm25 = get_mean(usable_pm25, usable_count)

assert total_records == usable_count + rejected_count

report = {
    "total_records": total_records,
    "usable_records": usable_count,
    "rejected_records": rejected_count,
    "mean_usable_temperature_c": rounded_value(mean_usable_temp),
    "mean_usable_pm25_ugm3": rounded_value(mean_usable_pm25),
}

report
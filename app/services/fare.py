"""Fare calculation — mirrors the frontend model so quotes match the app."""

BASE_FARE = 50.0
PER_KM = 35.0
PER_MIN = 2.0
MIN_FARE = 80.0

VEHICLE_MULTIPLIER = {
    "Moto": 0.5, "Scooty": 0.5,
    "Rickshaw": 0.7, "Loader": 0.9, "Shahzore": 1.6, "Dumper": 2.0,
    "Mini": 1.0, "Ride A/C": 1.3, "Premium": 1.8, "City to City": 2.2,
}

SURGE = {"normal": 1.0, "rain": 1.4, "peakHours": 1.25}
ACTIVE_SURGE = "normal"

PLATFORM_COMMISSION = 0.15  # company keeps 15%


def estimate_fare(distance_m: float, duration_s: float, vehicle_type: str) -> float:
    km = distance_m / 1000
    minutes = duration_s / 60
    mult = VEHICLE_MULTIPLIER.get(vehicle_type, 1.0)
    surge = SURGE.get(ACTIVE_SURGE, 1.0)
    total = (BASE_FARE + km * PER_KM + minutes * PER_MIN) * mult * surge
    total = max(total, MIN_FARE * mult * surge)
    return round(total / 5) * 5  # nearest 5 PKR


def split_fare(total: float) -> dict:
    commission = round(total * PLATFORM_COMMISSION)
    return {"total": total, "driver_earnings": total - commission, "company_commission": commission}

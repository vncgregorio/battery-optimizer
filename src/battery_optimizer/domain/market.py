from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PricePoint:
    period_start: datetime
    period_duration_hours: float
    price_pounds_per_megawatt_hour: float

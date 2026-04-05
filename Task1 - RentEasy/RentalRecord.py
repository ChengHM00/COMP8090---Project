
from dataclasses import dataclass
from datetime import date

from typing import Optional

# RentalRecord is a unified class to represent both room and leisure rentals, with fields to capture all relevant information for both types of rentals in a single list
@dataclass
class RentalRecord:
    rental_id: int
    asset_type: str
    asset_index: int
    start_date: date
    end_date: date
    rate: float
    revenue: float
    rental_nights: int = 0
    rental_time: int = 0
    room_rental_index: Optional[int] = None

    def __str__(self) -> str:
        return f"{self.asset_type.capitalize()} rental {self.rental_id}"
    


if __name__ == "__main__":
    print("This is RentalRecord class for representing rental records. It should not be instantiated directly.")
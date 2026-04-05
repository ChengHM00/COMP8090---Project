from datetime import date
from dataclasses import dataclass
from typing import List

from Object.Room import Room
from Object.Leisure import Leisure
from RentalRecord import RentalRecord   

class AssetManager:
    def __init__(self):
        self.rooms_assets: List[Room] = []
        self.leisures_assets: List[Leisure] = []

    def add_room_asset(self, room_name: str, location: str, capacity: int, start_date: date, end_date: date, maintenance: bool = False) -> int:
        room = Room(
            location=location,
            startDate=start_date,
            endDate=end_date,
            maintenance=maintenance,
            revenue=0.0,
            room_name=room_name,
            capacity=capacity,
        )
        self.rooms_assets.append(room)
        return len(self.rooms_assets) - 1

    def add_leisure_asset(self, leisure_name: str, location: str, availability: int, start_date: date, end_date: date, maintenance: bool = False) -> int:
        leisure = Leisure(
            location=location,
            startDate=start_date,
            endDate=end_date,
            maintenance=maintenance,
            revenue=0.0,
            leisure_name=leisure_name,
            availablility=availability,
            rental_time=0,
        )
        self.leisures_assets.append(leisure)
        return len(self.leisures_assets) - 1

    def update_room_asset(self, index: int, room_name: str, location: str, capacity: int, start_date: date, end_date: date, maintenance: bool):
        room = self.rooms_assets[index]
        room.room_name = room_name
        room.location = location
        room.capacity = capacity
        room.startDate = start_date
        room.endDate = end_date
        room.set_maintenance(maintenance)

    def update_leisure_asset(self, index: int, leisure_name: str, location: str, availability: int, start_date: date, end_date: date, maintenance: bool):
        leisure = self.leisures_assets[index]
        leisure.leisure_name = leisure_name
        leisure.location = location
        leisure.startDate = start_date
        leisure.endDate = end_date
        leisure.update_availability(availability)
        leisure.set_maintenance(maintenance)

    def delete_room_asset(self, index: int):
        self.rooms_assets.pop(index)

    def delete_leisure_asset(self, index: int):
        self.leisures_assets.pop(index)

    def clear(self):
        self.rooms_assets = []
        self.leisures_assets = []


class RentalManager:
    def __init__(self, asset_manager: AssetManager):
        self.asset_manager = asset_manager
        self.rentals: List[RentalRecord] = []
        self.next_rental_id = 1

    def add_room_rental(self, asset_index: int, start_date: date, end_date: date, rate: float) -> RentalRecord:
        if start_date >= end_date:
            raise ValueError("End date must be after start date.")
        if asset_index < 0 or asset_index >= len(self.asset_manager.rooms_assets):
            raise IndexError("Room asset not found.")

        room_asset = self.asset_manager.rooms_assets[asset_index]
        if room_asset.maintenance:
            raise ValueError("Cannot rent a room that is under maintenance.")

        if start_date < room_asset.startDate or end_date > room_asset.endDate:
            raise ValueError("Room rental dates must fall within the asset's available start and end dates.")

        if self.has_overlap('room', asset_index, start_date, end_date):
            raise ValueError("This room is already rented during the selected period.")
        rental_room = Room(
            location=room_asset.location,
            startDate=start_date,
            endDate=end_date,
            maintenance=room_asset.maintenance,
            revenue=0.0,
            room_name=room_asset.room_name,
            capacity=room_asset.capacity,
        )
        revenue = rental_room.calculate_revenue(rate)
        record = RentalRecord(
            rental_id=self.next_rental_id,
            asset_type='room',
            asset_index=asset_index,
            start_date=start_date,
            end_date=end_date,
            rate=rate,
            revenue=revenue,
            rental_nights=(end_date - start_date).days,
        )
        self.rentals.append(record)
        self.next_rental_id += 1
        return record

    def add_leisure_rental(self, asset_index: int, start_date: date, end_date: date, rate: float, rental_hours: int, room_rental_index: int) -> RentalRecord:
        if start_date > end_date:
            raise ValueError("End date must be on or after start date.")
        if rental_hours <= 0:
            raise ValueError("Rental time must be at least 1 hour.")
        if asset_index < 0 or asset_index >= len(self.asset_manager.leisures_assets):
            raise IndexError("Leisure asset not found.")
        if room_rental_index is None or room_rental_index < 0 or room_rental_index >= len(self.rentals):
            raise ValueError("A valid room rental must be selected for leisure linking.")

        leisure_asset = self.asset_manager.leisures_assets[asset_index]
        if leisure_asset.maintenance:
            raise ValueError("Cannot rent a leisure facility that is under maintenance.")

        # Check availability: count overlapping leisure rentals for this asset
        overlapping_count = 0
        for rental in self.rentals:
            if (rental.asset_type == 'leisure' and 
                rental.asset_index == asset_index and 
                start_date <= rental.end_date and 
                end_date >= rental.start_date):
                overlapping_count += 1
        if overlapping_count >= leisure_asset.availability:
            raise ValueError(f"This leisure facility has reached its maximum capacity ({leisure_asset.availability}) for the selected dates.")

        room_rental = self.rentals[room_rental_index]
        if not (start_date >= room_rental.start_date and end_date <= room_rental.end_date):
            raise ValueError("Leisure rental dates must fall within the linked room rental period.")

        leisure_rental = Leisure(
            location=leisure_asset.location,
            startDate=start_date,
            endDate=end_date,
            maintenance=leisure_asset.maintenance,
            revenue=0.0,
            leisure_name=leisure_asset.leisure_name,
            availablility=leisure_asset.availability,
            rental_time=rental_hours,
        )
        revenue = leisure_rental.calculate_revenue(rate)
        record = RentalRecord(
            rental_id=self.next_rental_id,
            asset_type='leisure',
            asset_index=asset_index,
            start_date=start_date,
            end_date=end_date,
            rate=rate,
            revenue=revenue,
            rental_time=rental_hours,
            room_rental_index=room_rental_index,
        )
        self.rentals.append(record)
        self.next_rental_id += 1
        return record

    def has_overlap(self, asset_type: str, asset_index: int, start_date: date, end_date: date) -> bool:
        for rental in self.rentals:
            if rental.asset_type != asset_type or rental.asset_index != asset_index:
                continue
            if start_date < rental.end_date and end_date > rental.start_date:
                return True
        return False

    def get_total_revenue(self) -> float:
        return sum(r.revenue for r in self.rentals)

    def get_statistics(self) -> dict:
        return {
            'total_rentals': len(self.rentals),
            'room_rentals': len([r for r in self.rentals if r.asset_type == 'room']),
            'leisure_rentals': len([r for r in self.rentals if r.asset_type == 'leisure']),
            'total_revenue': self.get_total_revenue(),
        }

    def clear(self):
        self.rentals = []
        self.next_rental_id = 1


if __name__ == "__main__":
    print("This is AssetManager and RentalManager classes for managing assets and rentals. They should not be instantiated directly.")
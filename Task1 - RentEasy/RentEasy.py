import streamlit as st
from datetime import date
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import pandas as pd
import io

from Room import Room
from Leisure import Leisure
from Facility import Facility

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


class CSVManager:
    def __init__(self, asset_manager, rental_manager):
        self.asset_manager = asset_manager
        self.rental_manager = rental_manager

    def export_rooms_to_csv(self):
        if not self.asset_manager.rooms_assets:
            return None

        data = []
        for i, room in enumerate(self.asset_manager.rooms_assets):
            data.append({
                'index': i,
                'name': room.room_name,
                'location': room.location,
                'capacity': room.capacity,
                'start_date': room.startDate.isoformat(),
                'end_date': room.endDate.isoformat(),
                'maintenance': room.maintenance,
            })
        df = pd.DataFrame(data)
        return df.to_csv(index=False).encode('utf-8')

    def export_leisures_to_csv(self):
        if not self.asset_manager.leisures_assets:
            return None

        data = []
        for i, leisure in enumerate(self.asset_manager.leisures_assets):
            data.append({
                'index': i,
                'name': leisure.leisure_name,
                'location': leisure.location,
                'availability': leisure.availability,
                'start_date': leisure.startDate.isoformat(),
                'end_date': leisure.endDate.isoformat(),
                'maintenance': leisure.maintenance,
            })
        df = pd.DataFrame(data)
        return df.to_csv(index=False).encode('utf-8')

    def export_rentals_to_csv(self):
        if not self.rental_manager.rentals:
            return None

        data = []
        for i, rental in enumerate(self.rental_manager.rentals):
            data.append({
                'index': i,
                'type': rental.asset_type,
                'asset_index': rental.asset_index,
                'start_date': rental.start_date.isoformat(),
                'end_date': rental.end_date.isoformat(),
                'rate': rental.rate,
                'revenue': rental.revenue,
                'rental_nights': rental.rental_nights,
                'rental_time': rental.rental_time,
                'room_rental_index': rental.room_rental_index if rental.room_rental_index is not None else '',
            })
        df = pd.DataFrame(data)
        return df.to_csv(index=False).encode('utf-8')

    def import_rooms_from_csv(self, csv_data):
        try:
            df = pd.read_csv(io.StringIO(csv_data.decode('utf-8')))
            rooms = []
            for _, row in df.iterrows():
                rooms.append(_room_from_dict({
                    'name': row['name'],
                    'location': row['location'],
                    'capacity': int(row['capacity']),
                    'start_date': date.fromisoformat(row['start_date']) if 'start_date' in row else date.today(),
                    'end_date': date.fromisoformat(row['end_date']) if 'end_date' in row else date(2999, 12, 31),
                    'maintenance': bool(row['maintenance']),
                }))
            return rooms
        except Exception as e:
            st.error(f"Error importing rooms: {e}")
            return None

    def import_leisures_from_csv(self, csv_data):
        try:
            df = pd.read_csv(io.StringIO(csv_data.decode('utf-8')))
            leisures = []
            for _, row in df.iterrows():
                leisures.append(_leisure_from_dict({
                    'name': row['name'],
                    'location': row['location'],
                    'availability': int(row['availability']),
                    'start_date': date.fromisoformat(row['start_date']) if 'start_date' in row else date.today(),
                    'end_date': date.fromisoformat(row['end_date']) if 'end_date' in row else date(2999, 12, 31),
                    'maintenance': bool(row['maintenance']),
                }))
            return leisures
        except Exception as e:
            st.error(f"Error importing leisures: {e}")
            return None

    def _parse_int(self, value, default=0):
        if pd.isna(value):
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            try:
                return int(float(value))
            except (ValueError, TypeError):
                return default

    def import_rentals_from_csv(self, csv_data):
        try:
            df = pd.read_csv(io.StringIO(csv_data.decode('utf-8')))
            rentals = []
            for index, row in df.iterrows():
                rental_nights = self._parse_int(row.get('rental_nights', 0), 0)
                rental_time = self._parse_int(row.get('rental_time', 0), 0)

                room_rental_index = None
                if 'room_rental_index' in row and pd.notna(row['room_rental_index']):
                    room_rental_index_value = str(row['room_rental_index']).strip()
                    if room_rental_index_value != '':
                        room_rental_index = self._parse_int(room_rental_index_value, None)

                converted = {
                    'type': row['type'],
                    'asset_index': self._parse_int(row['asset_index'], None),
                    'start_date': date.fromisoformat(row['start_date']),
                    'end_date': date.fromisoformat(row['end_date']),
                    'rate': float(row['rate']),
                    'revenue': float(row['revenue']),
                    'rental_nights': rental_nights,
                    'rental_time': rental_time,
                    'room_rental_index': room_rental_index,
                }
                rentals.append(_rental_record_from_dict(converted, index + 1))

            # Validate imported rental references against loaded assets and rental links
            for rental in rentals:
                if rental.asset_type == 'room':
                    if rental.asset_index is None or rental.asset_index < 0 or rental.asset_index >= len(self.asset_manager.rooms_assets):
                        raise ValueError(f"Imported room rental references missing room asset index {rental.asset_index}.Please ensure the referenced room asset exists in the system before importing rentals.")
                elif rental.asset_type == 'leisure':
                    if rental.asset_index is None or rental.asset_index < 0 or rental.asset_index >= len(self.asset_manager.leisures_assets):
                        raise ValueError(f"Imported leisure rental references missing leisure asset index {rental.asset_index}.Please ensure the referenced leisure asset exists in the system before importing rentals.")
                else:
                    raise ValueError(f"Unknown rental type '{rental.asset_type}' in imported data.")

                if rental.room_rental_index is not None:
                    if rental.room_rental_index < 0 or rental.room_rental_index >= len(rentals):
                        raise ValueError(f"Imported rental references invalid room rental index {rental.room_rental_index}.")

            return rentals
        except Exception as e:
            st.error(f"Error importing rentals: {e}")
            return None


def _room_from_dict(record: dict) -> Room:
    return Room(
        location=record['location'],
        startDate=record.get('start_date', date.today()),
        endDate=record.get('end_date', date(2999, 12, 31)),
        maintenance=record.get('maintenance', False),
        revenue=0.0,
        room_name=record['name'],
        capacity=int(record['capacity']),
    )


def _leisure_from_dict(record: dict) -> Leisure:
    return Leisure(
        location=record['location'],
        startDate=record.get('start_date', date.today()),
        endDate=record.get('end_date', date(2999, 12, 31)),
        maintenance=record.get('maintenance', False),
        revenue=0.0,
        leisure_name=record['name'],
        availablility=int(record['availability']),
        rental_time=0,
    )


def _rental_record_from_dict(record: dict, rental_id: int) -> RentalRecord:
    room_rental_index = None
    if 'room_rental_index' in record and record.get('room_rental_index') != '' and record.get('room_rental_index') is not None:
        room_rental_index = int(record['room_rental_index'])

    rental_nights = record.get('rental_nights')
    if rental_nights is None and record['type'] == 'room':
        rental_nights = (record['end_date'] - record['start_date']).days

    return RentalRecord(
        rental_id=rental_id,
        asset_type=record['type'],
        asset_index=int(record['asset_index']),
        start_date=record['start_date'],
        end_date=record['end_date'],
        rate=float(record['rate']),
        revenue=float(record['revenue']),
        rental_nights=int(rental_nights) if rental_nights is not None else 0,
        rental_time=int(record.get('rental_time', 0)),
        room_rental_index=room_rental_index,
    )


def get_manager() -> AssetManager:
    if 'asset_manager' not in st.session_state:
        manager = AssetManager()
        if 'rooms_assets' in st.session_state:
            for old_room in st.session_state.rooms_assets:
                manager.add_room_asset(
                    old_room['name'],
                    old_room['location'],
                    int(old_room['capacity']),
                    bool(old_room.get('maintenance', False)),
                )
        if 'leisures_assets' in st.session_state:
            for old_leisure in st.session_state.leisures_assets:
                manager.add_leisure_asset(
                    old_leisure['name'],
                    old_leisure['location'],
                    int(old_leisure['availability']),
                    bool(old_leisure.get('maintenance', False)),
                )
        st.session_state.asset_manager = manager
    return st.session_state.asset_manager


def get_rental_manager(asset_manager: AssetManager) -> RentalManager:
    if 'rental_manager' not in st.session_state:
        rental_manager = RentalManager(asset_manager)
        if 'rentals' in st.session_state:
            existing_rentals = []
            for index, old_rental in enumerate(st.session_state.rentals):
                converted = old_rental
                if isinstance(old_rental, dict):
                    converted = {
                        'type': old_rental['type'],
                        'asset_index': int(old_rental['asset_index']),
                        'start_date': old_rental['start_date'] if isinstance(old_rental['start_date'], date) else date.fromisoformat(old_rental['start_date']),
                        'end_date': old_rental['end_date'] if isinstance(old_rental['end_date'], date) else date.fromisoformat(old_rental['end_date']),
                        'rate': float(old_rental['rate']),
                        'revenue': float(old_rental['revenue']),
                        'rental_nights': int(old_rental.get('rental_nights', 0)),
                        'rental_time': int(old_rental.get('rental_time', 0)),
                        'room_rental_index': old_rental.get('room_rental_index'),
                    }
                existing_rentals.append(_rental_record_from_dict(converted, index + 1))
            rental_manager.rentals = existing_rentals
            rental_manager.next_rental_id = len(existing_rentals) + 1
        st.session_state.rental_manager = rental_manager
    return st.session_state.rental_manager


def show_home():
    st.header("Welcome to RentEasy")
    st.write("Manage your homestay rooms and leisure facilities with object-oriented assets and rentals.")
    logo_path = Path(__file__).parent / "Assets" / "building_hotel.png"
    if logo_path.exists():
        st.image(logo_path.read_bytes(), caption="RentEasy Logo")
    else:
        st.warning(f"Logo asset missing: {logo_path}")
    asset_manager = get_manager()
    rental_manager = get_rental_manager(asset_manager)
    stats = rental_manager.get_statistics()
    col1, col2, col3 = st.columns(3)
    col1.metric("Rooms", len(asset_manager.rooms_assets))
    col2.metric("Leisure", len(asset_manager.leisures_assets))
    col3.metric("Total Rentals", stats['total_rentals'])


def show_manage_assets():
    asset_manager = get_manager()
    st.header("Manage Assets")
    tab1, tab2 = st.tabs(["Rooms", "Leisure Facilities"])

    with tab1:
        st.subheader("Add New Room Asset")
        with st.form("add_room_asset"):
            room_name = st.text_input("Room Name")
            location = st.text_input("Location")
            capacity = st.number_input("Capacity", min_value=1, value=1)
            start_date = st.date_input("Start Date", value=date.today(), key="room_start")
            end_date = st.date_input("End Date", value=date(2999, 12, 31), key="room_end")
            maintenance = st.checkbox("Under Maintenance", value=False)
            submitted = st.form_submit_button("Add Room Asset")
            if submitted:
                asset_manager.add_room_asset(room_name, location, capacity, start_date, end_date, maintenance)
                st.success("Room asset added successfully!")
                st.rerun()

        st.subheader("Existing Room Assets")
        for index, room in enumerate(asset_manager.rooms_assets):
            with st.expander(room.room_name or f"Room {index+1}"):
                if st.button("Edit", key=f"edit_btn_room_{index}"):
                    st.session_state[f"edit_mode_room_{index}"] = not st.session_state.get(f"edit_mode_room_{index}", False)
                    st.rerun()
                if st.session_state.get(f"edit_mode_room_{index}", False):
                    with st.form(f"edit_form_room_{index}"):
                        new_name = st.text_input("Room Name", value=room.room_name)
                        new_location = st.text_input("Location", value=room.location)
                        new_capacity = st.number_input("Capacity", min_value=1, value=room.capacity)
                        new_start_date = st.date_input("Start Date", value=room.startDate, key=f"edit_room_start_{index}")
                        new_end_date = st.date_input("End Date", value=room.endDate, key=f"edit_room_end_{index}")
                        new_maintenance = st.checkbox("Under Maintenance", value=room.maintenance)
                        if st.form_submit_button("Save Changes"):
                            asset_manager.update_room_asset(index, new_name, new_location, new_capacity, new_start_date, new_end_date, new_maintenance)
                            st.success("Room asset updated successfully!")
                            st.session_state[f"edit_mode_room_{index}"] = False
                            st.rerun()
                else:
                    st.write(str(room))
                if st.button("Delete Room", key=f"delete_room_{index}"):
                    asset_manager.delete_room_asset(index)
                    st.rerun()

    with tab2:
        st.subheader("Add New Leisure Asset")
        with st.form("add_leisure_asset"):
            leisure_name = st.text_input("Leisure Name")
            location = st.text_input("Location")
            availability = st.number_input("Availability", min_value=1, value=1)
            start_date = st.date_input("Start Date", value=date.today(), key="leisure_start")
            end_date = st.date_input("End Date", value=date(2999, 12, 31), key="leisure_end")
            maintenance = st.checkbox("Under Maintenance", value=False)
            submitted = st.form_submit_button("Add Leisure Asset")
            if submitted:
                asset_manager.add_leisure_asset(leisure_name, location, availability, start_date, end_date, maintenance)
                st.success("Leisure asset added successfully!")
                st.rerun()

        st.subheader("Existing Leisure Assets")
        for index, leisure in enumerate(asset_manager.leisures_assets):
            with st.expander(leisure.leisure_name or f"Leisure {index+1}"):
                if st.button("Edit", key=f"edit_btn_leisure_{index}"):
                    st.session_state[f"edit_mode_leisure_{index}"] = not st.session_state.get(f"edit_mode_leisure_{index}", False)
                    st.rerun()
                if st.session_state.get(f"edit_mode_leisure_{index}", False):
                    with st.form(f"edit_form_leisure_{index}"):
                        new_name = st.text_input("Leisure Name", value=leisure.leisure_name)
                        new_location = st.text_input("Location", value=leisure.location)
                        new_availability = st.number_input("Availability", min_value=1, value=leisure.availability)
                        new_start_date = st.date_input("Start Date", value=leisure.startDate, key=f"edit_leisure_start_{index}")
                        new_end_date = st.date_input("End Date", value=leisure.endDate, key=f"edit_leisure_end_{index}")
                        new_maintenance = st.checkbox("Under Maintenance", value=leisure.maintenance)
                        if st.form_submit_button("Save Changes"):
                            asset_manager.update_leisure_asset(index, new_name, new_location, new_availability, new_start_date, new_end_date, new_maintenance)
                            st.success("Leisure asset updated successfully!")
                            st.session_state[f"edit_mode_leisure_{index}"] = False
                            st.rerun()
                else:
                    st.write(str(leisure))
                if st.button("Delete Leisure", key=f"delete_leisure_{index}"):
                    asset_manager.delete_leisure_asset(index)
                    st.rerun()


def show_manage_rentals():
    asset_manager = get_manager()
    rental_manager = get_rental_manager(asset_manager)
    st.header("Manage Rentals")
    tab1, tab2 = st.tabs(["Room Rentals", "Leisure Rentals"])

    with tab1:
        st.subheader("Add New Room Rental")
        if not asset_manager.rooms_assets:
            st.warning("Please create room assets first.")
        else:
            available_rooms = [(i, room) for i, room in enumerate(asset_manager.rooms_assets) if not room.maintenance]
            if not available_rooms:
                st.warning("No available rooms (all under maintenance).")
            else:
                with st.form("add_room_rental"):
                    room_labels = [f"{i+1}. {room.room_name}" for i, room in available_rooms]
                    selected_room = st.selectbox("Select Room Asset", room_labels, key="select_room_asset")
                    room_index = available_rooms[room_labels.index(selected_room)][0]
                    start_date = st.date_input("Start Date", value=date.today(), key="room_rental_start")
                    end_date = st.date_input("End Date", value=date.today(), key="room_rental_end")
                    rate = st.number_input("Daily Rate ($/night)", min_value=0.0, value=50.0)
                    submitted = st.form_submit_button("Create Room Rental")
                    if submitted:
                        try:
                            rental_manager.add_room_rental(room_index, start_date, end_date, rate)
                            room_name = asset_manager.rooms_assets[room_index].room_name
                            st.success(f"Room '{room_name}' rental created successfully!")
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))

    with tab2:
        st.subheader("Add New Leisure Rental")
        if not asset_manager.leisures_assets:
            st.warning("Please create leisure assets first.")
        elif not [r for r in rental_manager.rentals if r.asset_type == 'room']:
            st.warning("Create at least one room rental before adding leisure rentals.")
        else:
            available_leisures = [(i, leisure) for i, leisure in enumerate(asset_manager.leisures_assets) if not leisure.maintenance]
            if not available_leisures:
                st.warning("No available leisure assets (all under maintenance).")
            else:
                with st.form("add_leisure_rental"):
                    leisure_labels = [f"{i+1}. {leisure.leisure_name}" for i, leisure in available_leisures]
                    selected_leisure = st.selectbox("Select Leisure Asset", leisure_labels, key="select_leisure_asset")
                    leisure_index = available_leisures[leisure_labels.index(selected_leisure)][0]
                    start_date = st.date_input("Start Date", value=date.today(), key="leisure_rental_start")
                    end_date = st.date_input("End Date", value=date.today(), key="leisure_rental_end")
                    rate = st.number_input("Hourly Rate ($/hour)", min_value=0.0, value=10.0)
                    rental_hours = st.number_input("Rental Time (hours)", min_value=1, value=1)

                    room_rental_options = []
                    room_rental_indices = []
                    for index, rental in enumerate(rental_manager.rentals):
                        if rental.asset_type == 'room' and start_date >= rental.start_date and end_date <= rental.end_date:
                            room_name = asset_manager.rooms_assets[rental.asset_index].room_name
                            room_rental_options.append(f"Rental {rental.rental_id}: {room_name} ({rental.start_date} to {rental.end_date})")
                            room_rental_indices.append(index)

                    selected_room_rental_index = None
                    if room_rental_options:
                        options = ["Select a room rental"] + room_rental_options
                        selected_room_rental = st.selectbox("Select linked room rental", options, key="select_linked_room_rental")
                        if selected_room_rental != "Select a room rental":
                            selected_room_rental_index = room_rental_indices[room_rental_options.index(selected_room_rental)]
                    else:
                        st.warning("No room rentals found that cover the selected leisure dates. Leisure rentals must be within an existing room rental period.")

                    submitted = st.form_submit_button("Create Leisure Rental")
                    if submitted:
                        try:
                            if selected_room_rental_index is None:
                                raise ValueError("Please select a room rental to link.")
                            rental_manager.add_leisure_rental(leisure_index, start_date, end_date, rate, int(rental_hours), selected_room_rental_index)
                            leisure_name = asset_manager.leisures_assets[leisure_index].leisure_name
                            st.success(f"Leisure '{leisure_name}' rental created successfully!")
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))

    st.subheader("Rental History")
    for rental in rental_manager.rentals:
        asset_name = (asset_manager.rooms_assets[rental.asset_index].room_name
                      if rental.asset_type == 'room'
                      else asset_manager.leisures_assets[rental.asset_index].leisure_name)
        with st.expander(f"Rental {rental.rental_id}: {asset_name} ({rental.asset_type.capitalize()})"):
            st.write(f"Asset: {asset_name}")
            st.write(f"Period: {rental.start_date} to {rental.end_date}")
            st.write(f"Revenue: ${rental.revenue:.2f}")
            if rental.asset_type == 'room':
                st.write(f"Duration: {rental.rental_nights} night(s)")
            else:
                st.write(f"Duration: {rental.rental_time} hour(s)")
            if rental.room_rental_index is not None:
                linked = rental_manager.rentals[rental.room_rental_index]
                linked_name = asset_manager.rooms_assets[linked.asset_index].room_name
                st.write(f"Linked room rental: {linked_name}")
            if st.button("Delete", key=f"delete_rental_{rental.rental_id}"):
                rental_manager.rentals.remove(rental)
                st.rerun()


def show_revenue():
    asset_manager = get_manager()
    rental_manager = get_rental_manager(asset_manager)
    st.header("Revenue Overview")
    stats = rental_manager.get_statistics()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Rentals", stats['total_rentals'])
    col2.metric("Room Rentals", stats['room_rentals'])
    col3.metric("Leisure Rentals", stats['leisure_rentals'])
    st.metric("Total Revenue", f"${stats['total_revenue']:.2f}")

    if rental_manager.rentals:
        for rental in rental_manager.rentals:
            asset_name = (asset_manager.rooms_assets[rental.asset_index].room_name
                          if rental.asset_type == 'room'
                          else asset_manager.leisures_assets[rental.asset_index].leisure_name)
            st.write(f"Rental {rental.rental_id}: {asset_name} - ${rental.revenue:.2f}")
    else:
        st.info("No rentals recorded yet.")


def show_data_management():
    asset_manager = get_manager()
    rental_manager = get_rental_manager(asset_manager)
    csv_manager = st.session_state.csv_manager
    st.header("Data Management")
    st.write("Export your data to CSV files or import data from CSV files.")

    tab1, tab2 = st.tabs(["Export Data", "Import Data"])

    with tab1:
        st.subheader("Export Data to CSV")

        col1, col2, col3 = st.columns(3)

        with col1:
            csv_data = csv_manager.export_rooms_to_csv()
            if csv_data:
                st.download_button(
                    label="Download Rooms CSV",
                    data=csv_data,
                    file_name="rooms_assets.csv",
                    mime="text/csv",
                    key="download_rooms"
                )
            else:
                st.warning("No room data to export.")

        with col2:
            csv_data = csv_manager.export_leisures_to_csv()
            if csv_data:
                st.download_button(
                    label="Download Leisure CSV",
                    data=csv_data,
                    file_name="leisure_assets.csv",
                    mime="text/csv",
                    key="download_leisure"
                )
            else:
                st.warning("No leisure data to export.")

        with col3:
            csv_data = csv_manager.export_rentals_to_csv()
            if csv_data:
                st.download_button(
                    label="Download Rentals CSV",
                    data=csv_data,
                    file_name="rentals.csv",
                    mime="text/csv",
                    key="download_rentals"
                )
            else:
                st.warning("No rental data to export.")

        st.divider()
        if st.button("Export All Data (ZIP)", use_container_width=True):
            st.info("ZIP export feature coming soon! Please export each data type separately for now.")

    with tab2:
        st.subheader("Import Data from CSV")
        st.warning("**Important:** Importing will replace existing data. Make sure to export your current data first!")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Import Rooms")
            rooms_file = st.file_uploader("Choose rooms CSV file", type="csv", key="upload_rooms")
            if rooms_file is not None and st.button("Import Rooms Data", key="import_rooms_btn"):
                rooms_data = csv_manager.import_rooms_from_csv(rooms_file.getvalue())
                if rooms_data is not None:
                    asset_manager.rooms_assets = rooms_data
                    st.success(f"Successfully imported {len(rooms_data)} room assets!")
                    st.rerun()

        with col2:
            st.subheader("Import Leisure")
            leisure_file = st.file_uploader("Choose leisure CSV file", type="csv", key="upload_leisure")
            if leisure_file is not None and st.button("Import Leisure Data", key="import_leisure_btn"):
                leisure_data = csv_manager.import_leisures_from_csv(leisure_file.getvalue())
                if leisure_data is not None:
                    asset_manager.leisures_assets = leisure_data
                    st.success(f"Successfully imported {len(leisure_data)} leisure assets!")
                    st.rerun()

        with col3:
            st.subheader("Import Rentals")
            rentals_file = st.file_uploader("Choose rentals CSV file", type="csv", key="upload_rentals")
            if rentals_file is not None and st.button("Import Rentals Data", key="import_rentals_btn"):
                rentals_data = csv_manager.import_rentals_from_csv(rentals_file.getvalue())
                if rentals_data is not None:
                    rental_manager.rentals = rentals_data
                    rental_manager.next_rental_id = len(rentals_data) + 1
                    st.success(f"Successfully imported {len(rentals_data)} rentals!")
                    st.rerun()

        st.divider()
        st.subheader("Quick Actions")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Clear All Data", use_container_width=True, type="secondary"):
                asset_manager.clear()
                rental_manager.clear()
                st.success("All data cleared!")
                st.rerun()

        with col2:
            total_items = len(asset_manager.rooms_assets) + len(asset_manager.leisures_assets) + len(rental_manager.rentals)
            st.metric("Total Data Items", total_items)


def main():
    st.set_page_config(page_title="RentEasy", layout="wide")
    st.title("RentEasy - Homestay Management System")
    
    # Initialize managers
    asset_manager = get_manager()
    rental_manager = get_rental_manager(asset_manager)
    if 'csv_manager' not in st.session_state:
        st.session_state.csv_manager = CSVManager(asset_manager, rental_manager)
    
    page = st.sidebar.selectbox("Choose a page", ["Home", "Manage Assets", "Manage Rentals", "View Revenue", "Data Management"])
    if page == "Home":
        show_home()
    elif page == "Manage Assets":
        show_manage_assets()
    elif page == "Manage Rentals":
        show_manage_rentals()
    elif page == "View Revenue":
        show_revenue()
    elif page == "Data Management":
        show_data_management()


if __name__ == "__main__":
    main()



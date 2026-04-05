
# CSV Management Module for handling import and export of room, leisure, and rental data in CSV format, with validation and error handling.

import streamlit as st
from datetime import date
import pandas as pd
import io


class CSVManager:
    def __init__(self, asset_manager, rental_manager):
        self.asset_manager = asset_manager
        self.rental_manager = rental_manager
    
    #Export rooms, leisures, and rentals to CSV format
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

    # Import rooms, leisures, and rentals from CSV format with validation and error handling
    def import_rooms_from_csv(self, csv_data):
        try:
            df = pd.read_csv(io.StringIO(csv_data.decode('utf-8')))
            rooms = []
            for _, row in df.iterrows():
                rooms.append(self._room_from_dict({
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
                leisures.append(self._leisure_from_dict({
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

                # Convert the CSV row to a RentalRecord dictionary
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
                rentals.append(self._rental_record_from_dict(converted, index + 1))

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
        



    if __name__ == "__main__":
        print("This is CSVManager class for handling CSV import/export. It should not be instantiated directly.")
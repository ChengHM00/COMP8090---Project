
# Main module to run the RentEasy application

import streamlit as st
from datetime import date


from Object.Room import Room
from Object.Leisure import Leisure
from RentalRecord import RentalRecord
from Manager.Manager import AssetManager, RentalManager
from Manager.CSVManager import CSVManager
from StreamlitApp import StreamlitApp   

#Read the dict list and convert them to Room, Leisure objects and RentalRecord objects
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

#   Get the Asset and Rental Managers, and initialize them with the data from session state if available, otherwise create new instances
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
                existing_rentals.append(CSVManager._rental_record_from_dict(converted, index + 1))
            rental_manager.rentals = existing_rentals
            rental_manager.next_rental_id = len(existing_rentals) + 1
        st.session_state.rental_manager = rental_manager
    return st.session_state.rental_manager

# Main function to run the Streamlit app, which initializes the managers and displays the appropriate page based on user selection
def main():
    st.set_page_config(page_title="RentEasy", layout="wide")
    st.title("RentEasy - Homestay Management System")
    
    # Initialize managers
    asset_manager = CSVManager.get_manager()
    rental_manager = CSVManager.get_rental_manager(asset_manager)
    if 'csv_manager' not in st.session_state:
        st.session_state.csv_manager = CSVManager(asset_manager, rental_manager)
    
    page = st.sidebar.selectbox("Choose a page", ["Home", "Manage Assets", "Manage Rentals", "View Revenue", "Data Management"])
    if page == "Home":
        StreamlitApp.show_home()
    elif page == "Manage Assets":
        StreamlitApp.show_manage_assets()
    elif page == "Manage Rentals":
        StreamlitApp.show_manage_rentals()
    elif page == "View Revenue":
        StreamlitApp.show_revenue()
    elif page == "Data Management":
        StreamlitApp.show_data_management()


if __name__ == "__main__":
    main()



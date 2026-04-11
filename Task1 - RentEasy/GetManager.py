
import streamlit as st
from datetime import date


from Manager.Manager import AssetManager, RentalManager
from Manager.CSVManager import CSVManager


class GetManager:


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
    


# This is the GetManager class for accesaing asset and rental managers. It should not be instantiated directly.
if __name__ == "__main__":
   print("This is GetManager class for accesaing asset and rental managers. It should not be instantiated directly.")
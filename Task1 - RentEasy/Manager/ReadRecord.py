
from datetime import date


from Object.Room import Room
from Object.Leisure import Leisure
from RentalRecord import RentalRecord
  

class ReadRecord:

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
    

# This is the ReadRecord class for converting dictionaries to object instances. It should not be instantiated directly.
if __name__ == "__main__":
   print("This is ReadRecord class for converting dictionaries to object instances. It should not be instantiated directly.")
from Object.Facility import Facility   
from datetime import date

# Room class to represent a rental room that inherits from the Facility class, with additional attributes for room type and capacity.
class Room(Facility):

    def __init__(self, location, startDate, endDate=date(2999,12,31), maintenance=False, revenue=0.0, room_name="", capacity=1):
        super().__init__(location, startDate, endDate, maintenance, revenue)
        self.room_name = room_name
        self.capacity = capacity

    def print_details(self):
        # Print the details of the room, including location, availability, maintenance status, revenue, room name, and capacity
        super().print_details()
        print(f"Room name: {self.room_name}")
        print(f"Capacity: {self.capacity} person(s)")

    def calculate_revenue(self, daily_rate):
        # Calculate the revenue for the room based on the daily rate and the number of days it is rented
        if self.maintenance:
            return 0.0
        else:
            rental_days = (self.endDate - self.startDate).days
            return rental_days * daily_rate


    def update_revenue(self, daily_rate):
        # Update the revenue for the room by calculating it based on the daily rate and the rental period, and adding it to the existing revenue
        self.revenue += self.calculate_revenue(daily_rate)

    def update_rental_period(self, new_start_date, new_end_date):
        # Update the rental period for the room by setting new start and end dates, which can affect its availability and revenue
        self.startDate = new_start_date
        self.endDate = new_end_date
    
    def update_capacity(self, new_capacity):
        # Update the capacity of the room, which can affect its suitability for different types of renters
        self.capacity = new_capacity

    def update_room_name(self, new_room_name):
        # Update the name of the room, which can help with identification and marketing
        self.room_name = new_room_name

    def __str__(self):
        # Return a string representation of the room, including its location, rental period, maintenance status, revenue, room name, and capacity
        return (f"Room: {self.room_name}, Location: {self.location}, Rental Period: {self.startDate} to {self.endDate}, "
                f"Maintenance: {'Yes' if self.maintenance else 'No'}, Revenue: ${self.revenue:.2f}, Capacity: {self.capacity} person(s)")
    

    if __name__ == "__main__":
        print("This is the Room class, which represents a rentable room facility. It inherits from the Facility class and includes additional attributes for room name and capacity.")  
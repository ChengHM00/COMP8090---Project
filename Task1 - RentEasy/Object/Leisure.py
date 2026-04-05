from Facility import Facility
from datetime import date

class Leisure(Facility):
# Leisure class to represent a leisure facility that inherits from the Facility class, with additional attributes for leisure name, availability, and rental time.

    def __init__(self, location, startDate, endDate=date(2999,12,31), maintenance=False, revenue=0.0, leisure_name="", availablility=1, rental_time=0):
        super().__init__(location, startDate, endDate, maintenance, revenue)
        self.leisure_name = leisure_name
        self.availability = availablility
        self.rental_time = rental_time

    def print_details(self):
        # Print the details of the leisure facility, including location, availability, maintenance status, revenue, leisure name, and capacity
        super().print_details()
        print(f"Leisure name: {self.leisure_name}")
        print(f"Availability: {self.availability} qty")
        print(f"Rental time: {self.rental_time} hours")

    def calculate_revenue(self, hourly_rate):
        # Calculate the revenue for the leisure facility based on the hourly rate and the rental time
        if self.maintenance:
            return 0.0
        else:
            return self.rental_time * hourly_rate 


    def update_revenue(self, daily_rate):
        # Update the revenue for the leisure facility by calculating it based on the daily rate and the rental period, and adding it to the existing revenue
        self.revenue += self.calculate_revenue(daily_rate)

    def update_rental_period(self, new_start_date, new_end_date):
        # Update the rental period for the leisure facility by setting new start and end dates, which can affect its availability and revenue
        self.startDate = new_start_date
        self.endDate = new_end_date
    
    def update_availability(self, new_availability):
        # Update the availability of the leisure facility, which can affect its suitability for different types of renters
        self.availability = new_availability

    def update_leisure_name(self, new_leisure_name):
        # Update the name of the leisure facility, which can help with identification and marketing
        self.leisure_name = new_leisure_name
    
    def update_rental_time(self, new_rental_time):
        # Update the rental time for the leisure facility, which can affect its revenue and scheduling
        self.rental_time = new_rental_time  

    def __str__(self):
        # Return a string representation of the leisure facility, including its location, rental period, maintenance status, revenue, leisure name, and capacity
        return (f"Leisure Facility: {self.leisure_name}, Location: {self.location}, Rental Period: {self.startDate} to {self.endDate}, "
                f"Maintenance: {'Yes' if self.maintenance else 'No'}, Revenue: ${self.revenue:.2f}, Availability: {self.availability} qty, Rental Time: {self.rental_time} hours")
    

    if __name__ == "__main__":
        print("This is the Leisure class, which represents a rentable leisure facility. It inherits from the Facility class and includes additional attributes for leisure name, availability, and rental time.")
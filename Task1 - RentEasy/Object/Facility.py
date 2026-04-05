from datetime import date
from abc import ABC, abstractmethod

# Facility class to represent a rental facility with attributes for location, availability dates, maintenance status, and revenue.
class Facility(ABC):

    def __init__(self,location,startDate:date,endDate:date = date(2999,12,31),maintenance:bool=False,revenue:float=0.0):
        self.location = location
        self.startDate = startDate
        self.endDate = endDate
        self.maintenance = maintenance
        self.revenue = revenue

    def print_details(self):
        # Print the details of the facility, including location, availability, maintenance status, and revenue
        print(f"Facility located at {self.location}")
        print(f"Availability: {self.get_availability()}")
        print(f"Maintenance status: {self.get_maintenance_status()}")
        print(f"Revenue: ${self.revenue:.2f}")

# Check if the facility is available for rent on a given date by comparing the date with the availability dates and maintenance status.    
    def is_available(self, check_date:date) -> bool:
        # Check if the facility is available for rent on a given date
        return self.startDate <= check_date <= self.endDate and not self.maintenance
    
    def set_maintenance(self, status:bool):
        # Set the maintenance status of the facility
        self.maintenance = status

    def set_availability(self, startDate:date, endDate:date):
        # Set the availability dates for the facility
        self.startDate = startDate
        self.endDate = endDate
    
    def get_availability(self) -> str:
        # Return a string representation of the availability dates for the facility
        return f"Available from {self.startDate} to {self.endDate}"
    
    def get_maintenance_status(self) -> str:
        # Return a string representation of the maintenance status for the facility
        return "Under maintenance" if self.maintenance else "Available for rent"   
    

# Calculate the total cost for the facility based on fixed and monthly costs, and the duration of the rental period.
    def get_totalCost(self, fixed_cost:float, monthly_cost:float) -> float: 
        # Return the total cost for the facility
        self.totalCost = fixed_cost + monthly_cost*((self.endDate.year - self.startDate.year) * 12 + (self.endDate.month - self.startDate.month))
        return self.totalCost
    
    def get_revenue(self,cost,rent) -> float:
        # Return the current revenue for the facility
        self.revenue = rent - cost
        return self.revenue
  
    def update_revenue(self, amount:float):
        # Update the revenue for the facility by adding the specified amount
        self.revenue += amount

    def print_revenue(self):
        # Print the current revenue for the facility
        print(f"Current revenue for the facility: ${self.revenue:.2f}")

    @abstractmethod
    def calculate_revenue(self, daily_rate:float) -> float:
        # Abstract method to calculate the revenue for the rentable facility based on a daily rate
        pass   
        
    @abstractmethod
    def update_rental_period(self, new_start_date:date, new_end_date:date):
        # Update the rental period for the rentable facility by setting new start and end dates
        self.startDate = new_start_date
        self.endDate = new_end_date

    @abstractmethod
    def update_revenue(self, daily_rate:float):
        # Update the revenue for the rentable facility by calculating it based on the daily rate and the rental period, and adding it to the existing revenue
        self.revenue += self.calculate_revenue(daily_rate)

    def __str__(self):
        # Return a string representation of the rentable facility, including its location, rental period, maintenance status, and revenue
        return (f"Facility located at {self.location}, Rental Period: {self.startDate} to {self.endDate}, "
                f"Maintenance: {'Yes' if self.maintenance else 'No'}, Revenue: ${self.revenue:.2f}")
    

if __name__ == "__main__":
   print("This is the Facility class, which serves as a base class for Room and Leisure classes. It should not be instantiated directly.")
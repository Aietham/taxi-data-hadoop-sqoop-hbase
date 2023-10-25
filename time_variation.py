from mrjob.job import MRJob
from mrjob.step import MRStep
from datetime import datetime
import csv

class RevenueOverTime(MRJob):

    def steps(self):
        return [
            MRStep(mapper=self.mapper, reducer=self.reducer),
            MRStep(reducer=self.reducer_sort)
        ]

    def parse_datetime(self, datetime_str):
        formats = ['%d-%m-%Y %H:%M:%S', '%d-%m-%Y %H:%M', '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S']
        for fmt in formats:
            return datetime.strptime(datetime_str, fmt)    
    
    def mapper(self, _, line):

        if line.startswith('VendorID'):
            return
        
        row = next(csv.reader([line]))
        
        # Extracting columns
        start_datetime = self.parse_datetime(row[1])
        total_amount = float(row[16])

        # Extracting month
        month_name = datetime.strptime(str(start_datetime.month), '%m').strftime('%B') 

        # Checking whether the trip time is day or night
        # 6AM to 6PM - day, rest as night    
        if start_datetime.hour >= 6 and start_datetime.hour < 18:
            day_or_night = 'day'
        else:
            day_or_night = 'night'
        
        # Checking whether the trip day is weekday or weekend 
        if start_datetime.weekday() >= 5:
            weekday_or_weekend = 'weekend'
        else:
            weekday_or_weekend = 'weekday'

        key = (month_name, weekday_or_weekend, day_or_night)        
        yield key, total_amount

    def reducer(self, key, values):
        total_revenue = 0
        total_trips = 0
        for amount in values:
            total_revenue += amount
            total_trips += 1
        yield None, (key, (total_revenue / total_trips, total_trips))

    # Second reducer to sort the values based on revenue
    def reducer_sort(self, _, values):
        sorted_values = sorted(values)

        for item in sorted_values:
            avg_revenue = round(item[1][0], 3)
            total_trips = item[1][1]
            yield item[0], f"Average Trip Revenue = {avg_revenue}, No. of Trips = {total_trips}"

if __name__ == '__main__':
    RevenueOverTime.run()
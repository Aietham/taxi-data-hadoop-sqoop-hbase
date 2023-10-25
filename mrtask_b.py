# Importing necessary libraries
from mrjob.job import MRJob
from mrjob.step import MRStep
import csv

class LocationRevenue(MRJob):

    def steps(self):
        return [
            MRStep(mapper=self.mapper, reducer=self.reducer),
            MRStep(reducer=self.reducer_max)
        ]

    def mapper(self, _, line):
        if line.startswith('VendorID'):
            return
        
        row = list(csv.reader([line]))[0]
        pickup_location = int(row[7])
        total_amount = float(row[16])
        yield pickup_location, total_amount

    def reducer(self, PUlocation, amounts):
        total_revenue = round(sum(amounts), 2)
        yield None, (total_revenue, PUlocation)

    # Second reducer function to find the maximum values of revenue
    def reducer_max(self, _, total_revenues):
        maximum_revenue = max(total_revenues)
        highest_revenue = maximum_revenue[0]
        highest_revenue_PULocation = maximum_revenue[1]
        yield highest_revenue_PULocation, highest_revenue

if __name__ == '__main__':
    LocationRevenue.run()

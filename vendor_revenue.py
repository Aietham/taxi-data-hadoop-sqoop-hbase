# Importing necessary libraries
from mrjob.job import MRJob
from mrjob.step import MRStep
import csv

class VendorRevenue(MRJob):

	# MapReduce job steps
	def steps(self):
		return [
            MRStep(mapper=self.mapper, reducer=self.reducer),
            MRStep(reducer=self.reducer_max)
        ]
	
	# Mapper function to read each line of the csv file and extract VendorID and total amount per trip.
	def mapper(self, _, line):

		# Skipping header row
		if line.startswith('VendorID'):
			return
		# Reading csv
		row = list(csv.reader([line]))[0]
		
		# Exctracting VendorID and total_amount from the dataset
		vendor_id = int(row[0])
		total_amount = float(row[16])
		# Emit vendor_id as key and total_amount as value
		yield vendor_id, total_amount
		
	# Reducer function to calculate the total revenue generated per vendor by adding total amounts for all their trips.
	def reducer(self, vendor_id, revenues):
		trip_count = 0
		total_revenue = 0

		for value in revenues:
			trip_count = trip_count + 1
			total_revenue = total_revenue + value
		yield None, (trip_count, total_revenue, vendor_id)

	
	# Second reducer function to find out the vendor with the maximum number of trips
	def reducer_max(self, _ , vendor_details):
		max_vendor = max(vendor_details)
		max_total_revenue = max_vendor[1]
		max_vendor_id = max_vendor[2]
		yield max_vendor_id, max_total_revenue

if __name__ == '__main__':
	VendorRevenue.run()
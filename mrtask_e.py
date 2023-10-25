# Importing libraries
from mrjob.job import MRJob
import csv
from mrjob.step import MRStep

class TripRevenueRatio(MRJob):

	def steps(self):
		return [
			MRStep(mapper=self.mapper,reducer=self.reducer),
			MRStep(mapper=None,reducer=self.reducer_sort)
		]
	
	def mapper(self, _, line):

		if line.startswith('VendorID'): 
			return
		
		row = next(csv.reader([line]))
		
		# Extracting columns
		pickup_location = int(row[7])
		tip_amount = float(row[13])
		total_amount = float(row[16])

		yield pickup_location, (tip_amount, total_amount)
	
	# Combiner Function
	def combiner(self, pickup_location, trip_amounts):
		total_tip = 0
		total_revenue = 0
		for amount in trip_amounts:
			total_tip = total_tip + amount[0]
			total_revenue = total_revenue + amount[1]
		yield pickup_location, (total_tip, total_revenue)
			
	# Reducer Function
	def reducer(self, pickup_location, total_trip_amounts):
		total_tip = 0
		total_revenue = 0
		for amount in total_trip_amounts:
			total_tip = total_tip + amount[0]
			total_revenue = total_revenue + amount[1]

		average_tip_revenue_ratio = round(total_tip / total_revenue, 4)	
		yield None, (average_tip_revenue_ratio, pickup_location)
		
	
# Defining another reducer function to sort the values
	def reducer_sort(self, _, ratios):
		sorted_values = sorted(ratios, reverse=True)

		# Sorting the values in descending order of the ratio
		for value in sorted_values:
			yield value[1], value[0]

if __name__ == '__main__':
	TripRevenueRatio.run()
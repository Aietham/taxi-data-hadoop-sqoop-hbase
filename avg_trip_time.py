# Importing necessary libraries
from mrjob.job import MRJob
from mrjob.step import MRStep
from datetime import datetime
from itertools import groupby
import csv

class AvgTripTime(MRJob):

	def steps(self):
		return [
			MRStep(mapper=self.mapper,  reducer=self.reducer)
		]

	def mapper(self, _, line):

		if line.startswith('VendorID'):
			return

		data = next(csv.reader([line]))
		pickup_location = int(data[7])

		# Extracting time from pick-up and drop off
		pickup_time = datetime.strptime(data[1], '%Y-%m-%d %H:%M:%S')
		dropoff_time = datetime.strptime(data[2], '%Y-%m-%d %H:%M:%S')

		# Calculating time in minutes
		trip_duration = (dropoff_time - pickup_time).seconds / 60
		yield pickup_location, trip_duration
		
			
	def reducer(self, pickup_location, trip_times):
		total_trip_time = 0		# Calculating the sum of trip durations for each pickup location id
		trip_count = 0				# Calculating the sum of total trips from each pick location id

		for trip_time in trip_times:
			total_trip_time = total_trip_time + trip_time
			trip_count = trip_count + 1

		average_trip_time = round(total_trip_time / trip_count, 2)
		yield pickup_location, average_trip_time		

if __name__ == '__main__':
	AvgTripTime.run()
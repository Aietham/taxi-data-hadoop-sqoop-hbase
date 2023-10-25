from mrjob.job import MRJob
from mrjob.step import MRStep
import csv

class PaymentCount(MRJob):

    def steps(self):
        return [
            # Step 1: Count the occurrences of each payment type
            MRStep(
                mapper=self.mapper, combiner=self.combiner, reducer=self.reducer_count
            ),
            # Step 2: Sort the payment types by count in descending order
            MRStep(
                reducer=self.reducer_sort
            )
        ]


    def mapper(self, _, line):

        if line.startswith('VendorID'):
            return

        row = list(csv.reader([line]))[0]
        payment_type = row[9]
        yield payment_type, 1

    def combiner(self, payment_type, counts):

        # Combine intermediate counts to reduce data transfer
        total_count = sum(counts)
        yield payment_type, total_count

    def reducer_count(self, payment_type, counts):

        # Calculate the total count for each payment type
        total_count = sum(counts)
        yield None, (total_count, payment_type)

    def reducer_sort(self, _, payment_counts):

        # Sort payment types by count in descending order and yield the results
        sorted_counts = sorted(payment_counts, reverse=True)
        for count, payment_type in sorted_counts:
            yield payment_type, count

if __name__ == '__main__':
    PaymentCount.run()

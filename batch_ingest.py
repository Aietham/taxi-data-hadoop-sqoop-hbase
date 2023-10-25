import glob
import happybase
import csv

# HBase connection settings
hbase_host = 'ec2-18-234-245-255.compute-1.amazonaws.com'


# HBase table details
table_name = 'hbase_taxi'
column_family = 'trip_details'  # Modify to your column family name

# Function to create an HBase table if it doesn't exist
def create_hbase_table(connection, table_name, column_family):
    print ("Creating HBase table...")
    connection.create_table(
        table_name,
        {
            column_family: dict(),  # Column family options
        }
    )

# Function to load data from a CSV file into HBase
def load_data_into_hbase(csv_file, connection, table_name, column_family):
    table = connection.table(table_name)
    
    # Printing after 100000 rows are inserted from csv
    inserted_row_counter = 0
    print_threshold = 100000

    for file in csv_file:
        with open(file, 'r') as file1:
            csv_reader = csv.reader(file1)
            print("Reading a csv file...")
            for row in csv_reader:
                # Assuming the first column in the CSV is the row key
                row_key = row[0]
                
                # Create a row with column family and column qualifiers
                data = {f"{column_family}:{str(i)}": value for i, value in enumerate(row[1:], start=1)}
                
                # Insert data into HBase
                table.put(row_key.encode('utf-8'), data)

                inserted_row_counter = inserted_row_counter + 1  # Increment the row counter

                # checking and printing everytime when 100000 rows have been entered
                if inserted_row_counter % print_threshold == 0:
                    print(f'Inserted {inserted_row_counter} rows...') 

if __name__ == "__main__":
    # Connect to HBase
    print("Connecting to HBase...")
    connection = happybase.Connection(host=hbase_host)
    
    # Check if the table exists, create it if not
    if table_name.encode() not in connection.tables():
        create_hbase_table(connection, table_name, column_family)
    
    # Specify the path to your CSV file
    csv_file_path = glob.glob('/home/hadoop/' + '*.csv')
    
    # Load data from CSV into HBase
    load_data_into_hbase(csv_file_path, connection, table_name, column_family)
    
    # Close the HBase connection
    connection.close()

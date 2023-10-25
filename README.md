# MapReduce Optional Assignment: NYC Yellow Taxi Data Analysis

## Assignment Segments
1. **Introduction**
2. **Dataset Description**
3. **Tasks**
   - Data Ingestion
   - MapReduce Programming
4. **Evaluation Rubric**
5. **Final Submission**
6. **Optional Sessions**

---

## Introduction
Build an end-to-end big data pipeline on AWS EMR using:
- **Hadoop Framework**
- **Amazon RDS** (MySQL/PostgreSQL)
- **Apache Sqoop**
- **Apache HBase**
- **MRJob** for MapReduce

Ingest and analyze NYC TLC Yellow Taxi trip data for 2017 (Jan–Jun) and answer key analytical questions.

---

## Dataset Description
CSV files (each several GB) for Jan–Jun 2017:
- `yellow_tripdata_2017-01.csv`
- `yellow_tripdata_2017-02.csv`
- `yellow_tripdata_2017-03.csv`
- `yellow_tripdata_2017-04.csv`
- `yellow_tripdata_2017-05.csv`
- `yellow_tripdata_2017-06.csv`

**Data Dictionary**  
Refer to the [NYC TLC Yellow Taxi data dictionary](https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf) for detailed field definitions.

---

## Tasks

### 1. Data Ingestion

#### Task 1: RDS Setup & CSV Load
1. **Launch EMR Cluster** (single-node `m4.xlarge` with Hadoop & HBase).
2. **Create RDS MySQL instance**, open port 3306 for EMR master.
3. **SSH into EMR master**, download CSVs:
   ```bash
   wget https://nyc-tlc-upgrad.s3.amazonaws.com/yellow_tripdata_2017-01.csv
   wget https://nyc-tlc-upgrad.s3.amazonaws.com/yellow_tripdata_2017-02.csv
   ```
4. **Connect to RDS**:
   ```bash
   mysql -h <RDS_ENDPOINT> -u admin -p
   ```
5. **Create `taxi` table** with schema matching the data dictionary:
   ```sql
   CREATE TABLE taxi (
     VendorID INT,
     tpep_pickup_datetime DATETIME,
     tpep_dropoff_datetime DATETIME,
     passenger_count INT,
     trip_distance DOUBLE,
     RatecodeID INT,
     store_and_fwd_flag CHAR(1),
     PULocationID INT,
     DOLocationID INT,
     payment_type INT,
     fare_amount DOUBLE,
     extra DOUBLE,
     mta_tax DOUBLE,
     tip_amount DOUBLE,
     tolls_amount DOUBLE,
     improvement_surcharge DOUBLE,
     total_amount DOUBLE,
     congestion_surcharge DOUBLE,
     airport_fee DOUBLE,
     cbd_congestion_fee DOUBLE
   );
   ```
6. **Load data**:
   ```sql
   LOAD DATA LOCAL INFILE '/home/hadoop/yellow_tripdata_2017-01.csv'
     INTO TABLE taxi
     FIELDS TERMINATED BY ','
     IGNORE 1 LINES;
   LOAD DATA LOCAL INFILE '/home/hadoop/yellow_tripdata_2017-02.csv'
     INTO TABLE taxi
     FIELDS TERMINATED BY ','
     IGNORE 1 LINES;
   ```

#### Task 2: RDS → HBase via Sqoop
1. **Create HBase table**:
   ```shell
   hbase shell
   create 'hbtaxi','td'
   quit
   ```
2. **Install MySQL connector** on EMR master:
   ```bash
   wget https://de-mysql-connector.s3.amazonaws.com/mysql-connector-java-8.0.25.tar.gz
   tar -xzf mysql-connector-java-8.0.25.tar.gz
   sudo cp mysql-connector-java-8.0.25/mysql-connector-java-8.0.25.jar /usr/lib/sqoop/lib/
   ```
3. **Import from RDS**:
   ```bash
   sqoop import      --connect jdbc:mysql://<RDS_ENDPOINT>:3306/yellow      --table taxi      --hbase-table hbtaxi      --column-family td      --hbase-row-key VendorID,tpep_pickup_datetime,tpep_dropoff_datetime      --split-by VendorID      --username admin --password <password>      --num-mappers 5      --hbase-bulkload
   ```
4. **Verify**:
   ```shell
   hbase shell
   count 'hbtaxi'
   ```

#### Task 3: Bulk Import Additional Months
```bash
python3 batch_ingest.py   --csv-dir /home/hadoop/yellow   --table hbtaxi --column-family td --hbase-host localhost
```

---

### 2. MapReduce Programming
Before running jobs:
```bash
sudo pip3 install mrjob
hadoop fs -mkdir /user/hadoop/yellow
hadoop fs -put yellow_tripdata_2017-01.csv /user/hadoop/yellow
# Repeat for other CSVs
```

| Script                 | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| `vendor_revenue.py`    | Vendor with most trips & total revenue                                      |
| `pickup_revenue.py`    | Pickup location with highest total revenue                                  |
| `payment_types.py`     | Payment type counts, sorted descending                                      |
| `avg_trip_time.py`     | Average trip duration per pickup location                                   |
| `tip_ratio.py`         | Average tip/revenue ratio per pickup location (sorted)                      |
| `time_variation.py`    | Avg trip revenue by month, hour (day vs night), and day of week (wknd vs wd)|

**Example:**
```bash
python3 vendor_revenue.py   --input hdfs:///user/hadoop/yellow/*.csv   --output-dir results/vendor_revenue
```


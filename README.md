# Crypto ETL Pipeline

## Overview

This project is an automated ETL (Extract, Transform, Load) pipeline that collects cryptocurrency market data from the CoinGecko API, transforms the data using Python and Pandas, and stores historical market snapshots in a PostgreSQL database.

The pipeline is automated using Windows Task Scheduler and includes logging, error handling, duplicate prevention, and log rotation for monitoring pipeline executions.

## ETL Architecture

```text
CoinGecko API
      |
      v
Python Extraction
      |
      v
Pandas Transformation
      |
      v
PostgreSQL
      |
      v
Historical Market Data
```

Windows Task Scheduler runs the pipeline automatically every 6 hours.

## ETL Process

### 1. Extract

Cryptocurrency market data is retrieved from the CoinGecko `/coins/markets` API endpoint.

The pipeline currently extracts market data for the top 10 cryptocurrencies by market capitalization.

### 2. Transform

The API response is converted from JSON into a Pandas DataFrame.

The transformation process includes:

- Selecting relevant market fields
- Renaming columns for database readability
- Converting date fields to UTC timestamps
- Adding an extraction timestamp
- Preparing the dataset for PostgreSQL

### 3. Load

The transformed data is loaded into a PostgreSQL table called:

`crypto_market_history`

Each pipeline execution creates a new historical snapshot of cryptocurrency market data.

A database constraint and PostgreSQL conflict handling are used to prevent duplicate records for the same cryptocurrency and extraction timestamp.

## Technologies Used

- Python
- Pandas
- Requests
- PostgreSQL
- SQLAlchemy
- Psycopg
- CoinGecko API
- Windows Task Scheduler
- Jupyter Notebook

## Project Structure

```text
crypto-etl-pipeline/
|
|-- notebooks/
|   `-- api_exploration.ipynb
|
|-- sql/
|   `-- create_table.sql
|
|-- src/
|   `-- pipeline.py
|
|-- .gitignore
|-- requirements.txt
`-- README.md
```

Local environment files, database credentials, virtual environment files, and runtime logs are excluded from version control.

## Logging and Error Handling

The pipeline uses Python's logging module to record pipeline execution information.

Logs include:

- Pipeline start and completion
- Number of records extracted
- Number of records transformed
- Successful database loads
- Pipeline failures and exception tracebacks

Rotating file logging is used to prevent log files from growing indefinitely.

## Automation

The ETL pipeline is scheduled using Windows Task Scheduler.

The pipeline runs every 6 hours, allowing PostgreSQL to accumulate historical cryptocurrency market snapshots automatically.

## Database

The PostgreSQL database stores historical cryptocurrency market information including:

- Cryptocurrency ID and symbol
- Current price
- Market capitalization
- Market cap rank
- Trading volume
- 24-hour high and low
- 24-hour price change
- Circulating, total, and maximum supply
- All-time-high information
- Source update timestamp
- Pipeline extraction timestamp

The database schema is available in:

`sql/create_table.sql`

## Running the Project

### 1. Clone the repository

```bash
git clone <repository-url>
cd crypto-etl-pipeline
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root containing your PostgreSQL configuration:

```text
DB_HOST=your_host
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
```

The `.env` file is excluded from Git using `.gitignore`.

### 5. Create the database table

Run the SQL script:

`sql/create_table.sql`

### 6. Run the pipeline

```bash
python src/pipeline.py
```

## Key Learnings

This project provided hands-on experience with:

- Building an end-to-end ETL pipeline
- Extracting data from a REST API
- Transforming semi-structured JSON data with Pandas
- Loading historical data into PostgreSQL
- Managing database connections with SQLAlchemy
- Preventing duplicate database records
- Using environment variables for database credentials
- Implementing logging and error handling
- Automating recurring ETL jobs
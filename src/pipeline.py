import os
from pathlib import Path

import pandas as pd
import requests
import logging

from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, MetaData, Table
from sqlalchemy.dialects.postgresql import insert
from logging.handlers import RotatingFileHandler


project_root = Path(__file__).resolve().parent.parent

logs_dir = project_root / "logs"
logs_dir.mkdir(exist_ok=True)

log_file = logs_dir / "pipeline.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        RotatingFileHandler(
            log_file,
            maxBytes=1_000_000,
            backupCount=3
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

#extract function to get data from the API
def extract_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": False
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


#transform function to clean and transform the data
def transform_data(data):
    df = pd.DataFrame(data)

    selected_columns = [
        "id",
        "symbol",
        "name",
        "current_price",
        "market_cap",
        "market_cap_rank",
        "total_volume",
        "high_24h",
        "low_24h",
        "price_change_24h",
        "price_change_percentage_24h",
        "circulating_supply",
        "total_supply",
        "max_supply",
        "ath",
        "ath_change_percentage",
        "ath_date",
        "last_updated"
    ]

    df = df[selected_columns]

    df["ath_date"] = pd.to_datetime(
        df["ath_date"],
        utc=True
    )

    df["last_updated"] = pd.to_datetime(
        df["last_updated"],
        utc=True
    )

    df["extracted_at"] = pd.Timestamp.now(tz="UTC")

    df = df.rename(columns={
        "id": "coin_id",
        "name": "coin_name",
        "current_price": "current_price_usd",
        "market_cap": "market_cap_usd",
        "total_volume": "total_volume_usd",
        "high_24h": "high_24h_usd",
        "low_24h": "low_24h_usd",
        "price_change_24h": "price_change_24h_usd",
        "ath": "ath_usd",
        "last_updated": "source_updated_utc",
        "extracted_at": "extracted_at_utc"
    })

    return df


#database connection function to create a database engine
def create_database_engine():
    project_root = Path(__file__).resolve().parent.parent
    env_path = project_root / ".env"

    load_dotenv(env_path)

    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")

    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=db_user,
        password=db_password,
        host=db_host,
        port=int(db_port),
        database=db_name
    )

    return create_engine(database_url)


#load_data function to load the transformed data into the database
def load_data(df, engine):
    metadata = MetaData()

    crypto_market_history = Table(
        "crypto_market_history",
        metadata,
        autoload_with=engine
    )

    records = df.to_dict(orient="records")

    with engine.begin() as connection:
        stmt = insert(crypto_market_history).values(records)

        stmt = stmt.on_conflict_do_nothing(
            index_elements=[
                "coin_id",
                "extracted_at_utc"
            ]
        )

        connection.execute(stmt)


#main function to run the ETL pipeline
def main():
    logger.info("Starting crypto ETL pipeline...")

    try:
        data = extract_data()
        logger.info(f"Extracted {len(data)} records.")

        df = transform_data(data)
        logger.info(f"Transformed {len(df)} records.")

        engine = create_database_engine()

        load_data(df, engine)
        logger.info("Data loaded successfully.")

        logger.info("Pipeline completed.")

    except Exception:
        logger.exception("Pipeline failed.")
        raise

if __name__ == "__main__":
    main()
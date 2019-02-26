
import pandas as pd
import s3fs

# Connect to S3 using default credentials
fs = s3fs.S3FileSystem(anon=False)

# Specify bucket/database file
DB = "xdev-bot/database.csv"

def read_database():

    try:
        # If the databse file exists, open it in
        # a pandas dataframe
        if fs.exists(DB):
            with fs.open(DB, "r") as f:
                print(f"Reading Existing Database from {DB} S3 bucket")
                df = pd.read_csv(f, index_col=0)
                print(df.head())
        else:
            #create empty dataframe
            columns = [
                "column_name",
                "column_id",
                "column_url",
                "note",
                "card_id",
                "card_url",
                "created_at",
                "updated_at",
                "assignees",
            ]
            df = pd.DataFrame(columns=columns)
        return df

    except Exception as exc:
        raise exc


def write_database(df):

    with fs.open(DB, "w") as f:
        print(f"Saving Database in {DB} S3 bucket")
        print(df.head())
        df.to_csv(f, index=True)
""" Project Board related events """
import gidgethub.routing
import pandas as pd
import s3fs

router = gidgethub.routing.Router()

# Connect to S3 using default credentials
fs = s3fs.S3FileSystem(anon=False)

# Specify bucket/database file
DB = "xdev-bot/database.csv"

PROJECT_BOARD = {
    "name": "Backlog Queue",
    "columns": {
        "backlog": {"id": 4_507_386},
        "in_progress": {"id": 4_507_392},
        "done": {"id": 4_507_393},
    },
    "columns_reverse": {4_507_386: "backlog", 4_507_392: "in_progress", 4_507_393: "done"},
}


@router.register("project_card", action="created")
async def project_card_created_event(event, gh, *args, **kwargs):
    card_url = event.data["project_card"]["url"]
    card_id = event.data["project_card"]["id"]
    note = event.data["project_card"]["note"]
    column_url = event.data["project_card"]["column_url"]
    column_id = event.data["project_card"]["column_id"]
    column_name = PROJECT_BOARD["columns_reverse"][column_id]
    created_at = event.data["project_card"]["created_at"]
    updated_at = event.data["project_card"]["updated_at"]
    entry = {
        "card_url": card_url,
        "card_id": card_id,
        "note": note,
        "column_url": column_url,
        "column_id": column_id,
        "column_name": column_name,
        "created_at": created_at,
        "updated_at": updated_at,
    }
    temp_df = pd.DataFrame([entry])
    try:
        # If the databse file exists, open it in
        # a pandas dataframe
        if fs.exists(DB):
            with fs.open(DB, "r") as f:
                print(f"Reading Existing Database from {DB} S3 bucket")
                df = pd.read_csv(f, index_col=0)
                print(df.head())

        else:
            # Create empty dataframe
            columns = [
                "column_name",
                "column_id",
                "column_url",
                "note",
                "card_id",
                "card_url",
                "created_at",
                "updated_at",
            ]
            df = pd.DataFrame(columns=columns)

        df = pd.concat([temp_df, df], ignore_index=True, sort=False)

        with fs.open(DB, "w") as f:
            print(f"Saving Database in {DB} S3 bucket")
            print(df.head())
            df.to_csv(f, index=True)

    except Exception as exc:
        raise exc


@router.register("project_card", action="moved")
async def project_card_moved_event(event, gh, *args, **kwargs):
    card_id = event.data["project_card"]["id"]
    column_url = event.data["project_card"]["column_url"]
    column_id = event.data["project_card"]["column_id"]
    column_name = PROJECT_BOARD["columns_reverse"][column_id]
    updated_at = event.data["project_card"]["updated_at"]

    try:
        # If the databse file exists, open it in
        # a pandas dataframe
        if fs.exists(DB):
            with fs.open(DB, "r") as f:
                print(f"Reading Existing Database from {DB} S3 bucket")
                df = pd.read_csv(f, index_col=0)
                print(df.head())

                df.loc[df["card_id"] == card_id, "column_name"] = column_name
                df.loc[df["card_id"] == card_id, "column_url"] = column_url
                df.loc[df["card_id"] == card_id, "column_id"] = column_id
                df.loc[df["card_id"] == card_id, "updated_at"] = updated_at

            with fs.open(DB, "w") as f:
                print(f"Saving Database in {DB} S3 bucket")
                print(df.head())
                df.to_csv(f, index=True)

        else:
            raise ValueError(f"Specified Database : {DB} does not exist")

    except Exception as exc:
        raise exc

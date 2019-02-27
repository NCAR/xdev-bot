""" Issue related events"""
import gidgethub.routing
import pandas as pd
import s3fs
from .helpers import read_database, write_database

from .project_board import PROJECT_BOARD

fs = s3fs.S3FileSystem(anon=False)

DB = "xdev-bot/database.csv"

router = gidgethub.routing.Router()


@router.register("issues", action="opened")
async def issue_opened_event(event, gh, *args, **kwargs):
    """ Whenever an issue is opened, create a card in

    - project_board = "Backlog Queue"
    - column = "Backlog"
    """
    backlog_column_id = PROJECT_BOARD["columns"]["backlog"]["id"]
    project_board_name = PROJECT_BOARD["name"]
    issue_url = event.data["issue"]["html_url"]
    url = f"/projects/columns/{backlog_column_id}/cards"

    print(f"Creating Card in {project_board_name} project board for issue : {issue_url}")

    # POST /projects/columns/:column_id/cards
    await gh.post(
        url, data={"note": issue_url}, accept="application/vnd.github.inertia-preview+json"
    )


@router.register("issues", action="closed")
async def issue_closed_event(event, gh, *args, **kwargs):
    """ Whenever an issue is closed:

    - find card associated with issue (get card ID)
    - construct URL for card
    - get column ID of "done" column
    - retrieve updated_at from payload and update database
    - update card information (new column ID)

    """
    done_column_id = PROJECT_BOARD["columns"]["done"]["id"]
    project_board_name = PROJECT_BOARD["name"]

    issue_url = event.data["issue"]["html_url"]
    #updated_at = event.data["issue"]["updated_at"]
    
    df = read_database()

    row = df["note"] == issue_url
    card_id = df.loc[row]["card_id"].values[0]
    #df.loc[row]["updated_at"] = updated_at

    print(f"Updating database: move card {card_id} to done column")
    #write_database(df)

    print(f"Closing Card in {project_board_name} project board for issue : {issue_url}")
    # POST /projects/columns/cards/:card_id/moves
    url = f"/projects/columns/cards/{card_id}/moves"
    await gh.post(
        url,
        data={"position": "top", "column_id": done_column_id},
        accept="application/vnd.github.inertia-preview+json",
        )
    
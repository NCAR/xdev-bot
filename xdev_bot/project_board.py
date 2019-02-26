""" Project Board related events """
import gidgethub.routing
from .helpers import read_database, write_database
import pandas as pd
import ast

router = gidgethub.routing.Router()



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
    assignees = "octocat"
    entry = {
        "card_url": card_url,
        "card_id": card_id,
        "note": note,
        "column_url": column_url,
        "column_id": column_id,
        "column_name": column_name,
        "created_at": created_at,
        "updated_at": updated_at,
        "assignees": assignees,
    }
    temp_df = pd.DataFrame([entry])
    df = read_database()
 
    df = pd.concat([temp_df, df], ignore_index=True, sort=False)

    write_database(df)


@router.register("project_card", action="moved")
async def project_card_moved_event(event, gh, *args, **kwargs):
    """ Whenever a card is moved, assign card mover to the issue or pull request."""

    card_mover = event.data["sender"]["login"]
    card_id = event.data["project_card"]["id"]
    card_note = event.data["project_card"]["note"]
    column_url = event.data["project_card"]["column_url"]
    column_id = event.data["project_card"]["column_id"]
    column_name = PROJECT_BOARD["columns_reverse"][column_id]
    updated_at = event.data["project_card"]["updated_at"]
    
    
    df = read_database()
    assignees = df.loc[df["card_id"]==card_id]["assignees"]
    assignees = ast.literal_eval(assignees)
    assignees = set(assignees)
    assignees.add(card_mover)
    assignees=list(assignees)

    # Determine if card's note is an issue
    # or pull request html_url in the form
    # 'https://github.com/org_or_user/repo_name/issues_or_pull/number'
    note_items = card_note.split("/")

    # This returns ['https:', '', 'github.com', 'org_or_user', 'repo_name', 'issues_or_pull', 'number']
    # if note is a html_url to an issue or pull request, len(note_items) == 7
    if len(note_items) == 7:
        _event_type = note_items[-2]

        # Construct Issue or PR API url
        # * Issue url looks like https://api.github.com/repos/NCAR/xdev-bot-testing/issues/2
        # * PR url looks like 'https://api.github.com/repos/NCAR/xdev-bot-testing/pulls/3'
        if _event_type == "issues":
            prefix = "/".join(note_items[-4:])

        elif _event_type == "pull":
            # https://developer.github.com/v3/pulls/#labels-assignees-and-milestones
            # Every pull request is an issue, but not every issue is a pull request.
            p = note_items[-4:]
            p[-2] = "issues"
            prefix = "/".join(p)

        _event_api_url = "https://api.github.com/repos/" + prefix
        # Assign card mover to issue or pull request
        print(f"Assigning user={card_mover} to {card_note}")
        if _event_type == "issues":
            if column_name == "done":
                await gh.patch(_event_api_url,data={"state":"closed","assignees": assignees})
            elif column_name == "backlog":
                await gh.patch(_event_api_url,data={"state":"open"})
            elif column_name == "in_progress":
                await gh.patch(_event_api_url, data={"state":"open","assignees": assignees})

    else:
        print(f"Couldn't determine event type for {card_note}")

    df.loc[df["card_id"] == card_id, "column_name"] = column_name
    df.loc[df["card_id"] == card_id, "column_url"] = column_url
    df.loc[df["card_id"] == card_id, "column_id"] = column_id
    df.loc[df["card_id"] == card_id, "updated_at"] = updated_at
    df.loc[df["card_id"] == card_id, "assignees"] = str(assignees)
    write_database(df)

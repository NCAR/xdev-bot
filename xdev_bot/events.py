import gidgethub.routing

from .actions import create_card, get_card, move_card, card_is_issue, update_issue
from .database2 import PROJECT_CARDS

router = gidgethub.routing.Router()


@router.register('issues', action='opened')
async def issue_opened_event(event, gh, *args, **kwargs):
    ghargs = create_card(event, column='to_do')
    await gh.post(ghargs.url, **ghargs.kwargs)


@router.register('pull_request', action='opened')
async def pr_opened_event(event, gh, *args, **kwargs):
    ghargs = create_card(event, column='in_progress')
    await gh.post(ghargs.url, **ghargs.kwargs)


@router.register('issues', action='closed')
@router.register('pull_request', action='closed')
async def issue_or_pr_closed_event(event, gh, *args, **kwargs):
    ghargs = move_card(event, column='done')
    await gh.post(ghargs.url, **ghargs.kwargs)


@router.register('issues', action='reopened')
@router.register('pull_request', action='reopened')
async def issue_or_pr_reopened_event(event, gh, *args, **kwargs):
    ghargs = move_card(event, column='in_progress')
    await gh.post(ghargs.url, **ghargs.kwargs)


@router.register('project_card', action='created')
async def project_card_created(event, gh, *args, **kwargs):
    card = get_card(event)
    PROJECT_CARDS.add(card)


@router.register('project_card', action='moved')
async def project_card_moved(event, gh, *args, **kwargs):
    card = get_card(event)
    PROJECT_CARDS.add(card)
    if card_is_issue(card):
        state = 'closed' if card['column_name'] == 'done' else 'open'
        ghargs = update_issue(card, state=state)
        await gh.patch(ghargs.url, **ghargs.kwargs)


@router.register('project_card', action='deleted')
async def project_card_deleted(event, gh, *args, **kwargs):
    card = get_card(event)
    PROJECT_CARDS.remove(card)

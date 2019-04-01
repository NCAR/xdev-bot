import gidgethub.routing

from .actions import (get_create_card_ghargs, get_move_card_ghargs, get_update_issue_status_ghargs,
                      save_card, remove_card, save_merged_status, get_card_from_card_event,
                      get_card_type, get_update_pull_status_ghargs)

router = gidgethub.routing.Router()


@router.register('issues', action='opened')
async def issue_opened_event(event, gh, *args, **kwargs):
    ghargs = get_create_card_ghargs(event, column='to_do')
    await gh.post(ghargs.url, **ghargs.kwargs)


@router.register('pull_request', action='opened')
async def pr_opened_event(event, gh, *args, **kwargs):
    ghargs = get_create_card_ghargs(event, column='in_progress')
    await gh.post(ghargs.url, **ghargs.kwargs)


@router.register('issues', action='closed')
async def issue_closed_event(event, gh, *args, **kwargs):
    ghargs = get_move_card_ghargs(event, column='done')
    await gh.post(ghargs.url, **ghargs.kwargs)


@router.register('pull_request', action='closed')
async def pull_request_closed_event(event, gh, *args, **kwargs):
    save_merged_status(event)
    ghargs = get_move_card_ghargs(event, column='done')
    await gh.post(ghargs.url, **ghargs.kwargs)


@router.register('issues', action='reopened')
@router.register('pull_request', action='reopened')
async def issue_or_pr_reopened_event(event, gh, *args, **kwargs):
    ghargs = get_move_card_ghargs(event, column='in_progress')
    await gh.post(ghargs.url, **ghargs.kwargs)


@router.register('project_card', action='created')
async def project_card_created_event(event, gh, *args, **kwargs):
    save_card(event)


@router.register('project_card', action='moved')
async def project_card_moved_event(event, gh, *args, **kwargs):
    save_card(event)
    card = get_card_from_card_event(event)
    card_t = get_card_type(card)
    if card_t == 'issue':
        ghargs = get_update_issue_status_ghargs(card)
        await gh.patch(ghargs.url, **ghargs.kwargs)
    elif card_t == 'pull_request':
        ghargs = get_update_pull_status_ghargs(card)
        gh_func = getattr(gh, ghargs.func)
        await gh_func(ghargs.url, **ghargs.kwargs)


@router.register('project_card', action='deleted')
async def project_card_deleted_event(event, gh, *args, **kwargs):
    remove_card(event)

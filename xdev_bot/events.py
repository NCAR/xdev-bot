import gidgethub.routing

from .gidgethub import GHArgs
from .actions import (get_create_card_ghargs, get_move_card_ghargs, get_update_status_ghargs,
                      save_card, remove_card, save_merged_status)

router = gidgethub.routing.Router()


async def post_or_patch(gh, args):
    if isinstance(args, GHArgs):
        gh_func = getattr(gh, args.func)
        await gh_func(args.url, **args.kwargs)


@router.register('issues', action='opened')
async def issue_opened_event(event, gh, *args, **kwargs):
    ghargs = get_create_card_ghargs(event, column='to_do')
    await post_or_patch(gh, ghargs)


@router.register('pull_request', action='opened')
async def pr_opened_event(event, gh, *args, **kwargs):
    ghargs = get_create_card_ghargs(event, column='in_progress')
    await post_or_patch(gh, ghargs)


@router.register('issues', action='closed')
async def issue_closed_event(event, gh, *args, **kwargs):
    ghargs = get_move_card_ghargs(event, column='done')
    await post_or_patch(gh, ghargs)


@router.register('pull_request', action='closed')
async def pull_request_closed_event(event, gh, *args, **kwargs):
    ghargs = get_move_card_ghargs(event, column='done')
    save_merged_status(event)
    await post_or_patch(gh, ghargs)


@router.register('issues', action='reopened')
@router.register('pull_request', action='reopened')
async def issue_or_pr_reopened_event(event, gh, *args, **kwargs):
    ghargs = get_move_card_ghargs(event, column='in_progress')
    await post_or_patch(gh, ghargs)


@router.register('project_card', action='created')
async def project_card_created_event(event, gh, *args, **kwargs):
    save_card(event)


@router.register('project_card', action='moved')
async def project_card_moved_event(event, gh, *args, **kwargs):
    ghargs = get_update_status_ghargs(event)
    save_card(event)
    await post_or_patch(gh, ghargs)


@router.register('project_card', action='deleted')
async def project_card_deleted_event(event, gh, *args, **kwargs):
    remove_card(event)

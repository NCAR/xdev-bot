import gidgethub.routing

from .gidgethub import GHArgs
from .actions import (issue_opened_call_args, issue_closed_call_args,
                      card_created_call_args, card_moved_call_args, card_deleted_call_args,
                      save_card, remove_card, save_merged_status)

router = gidgethub.routing.Router()


async def post_or_patch(gh, args):
    if isinstance(args, GHArgs):
        gh_func = getattr(gh, args.func)
        await gh_func(args.url, **args.kwargs)


@router.register('issues', action='opened')
async def issue_opened_event(event, gh, *args, **kwargs):
    for ghargs in issue_opened_call_args(event, column='to_do'):
        await post_or_patch(gh, ghargs)


@router.register('pull_request', action='opened')
async def pull_request_opened_event(event, gh, *args, **kwargs):
    for ghargs in issue_opened_call_args(event, column='in_progress'):
        await post_or_patch(gh, ghargs)


@router.register('issues', action='closed')
async def issue_closed_event(event, gh, *args, **kwargs):
    for ghargs in issue_closed_call_args(event, column='done'):
        await post_or_patch(gh, ghargs)


@router.register('pull_request', action='closed')
async def pull_request_closed_event(event, gh, *args, **kwargs):
    save_merged_status(event)
    for ghargs in issue_closed_call_args(event, column='done'):
        await post_or_patch(gh, ghargs)


@router.register('issues', action='reopened')
async def issue_reopened_event(event, gh, *args, **kwargs):
    for ghargs in issue_closed_call_args(event, column='in_progress'):
        await post_or_patch(gh, ghargs)


@router.register('pull_request', action='reopened')
async def pull_request_reopened_event(event, gh, *args, **kwargs):
    for ghargs in issue_closed_call_args(event, column='in_progress'):
        await post_or_patch(gh, ghargs)


@router.register('project_card', action='created')
async def project_card_created_event(event, gh, *args, **kwargs):
    for ghargs in card_created_call_args(event):
        await post_or_patch(gh, ghargs)
    save_card(event)


@router.register('project_card', action='moved')
async def project_card_moved_event(event, gh, *args, **kwargs):
    for ghargs in card_moved_call_args(event):
        await post_or_patch(gh, ghargs)
    save_card(event)


@router.register('project_card', action='deleted')
async def project_card_deleted_event(event, gh, *args, **kwargs):
    for ghargs in card_deleted_call_args(event):
        await post_or_patch(gh, ghargs)
    remove_card(event)

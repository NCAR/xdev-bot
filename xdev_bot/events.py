import gidgethub.routing

from .cards import create_new_card, get_card, move_card
from .database import PROJECT_CARDS

router = gidgethub.routing.Router()


@router.register('issues', action='opened')
async def issue_opened_event(event, gh, *args, **kwargs):
    url, data = create_new_card(event)
    await gh.post(url,
                  data=data,
                  accept='application/vnd.github.inertia-preview+json')


@router.register('project_card', action='created')
async def project_card_created(event, gh, *args, **kwargs):
    card = get_card(event)
    await PROJECT_CARDS.update(card, key='id')


@router.register('issues', action='closed')
async def issue_closed_event(event, gh, *args, **kwargs):
    url, data = move_card(event, column='done')
    await gh.post(url,
                  data=data,
                  accept='application/vnd.github.inertia-preview+json')


@router.register('project_card', action='moved')
async def project_card_moved(event, gh, *args, **kwargs):
    card = get_card(event)
    await PROJECT_CARDS.update(card, key='id')

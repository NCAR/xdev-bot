import gidgethub.routing

from .cards import create_new_card, get_card_properties
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
    card_properties = get_card_properties(event)
    await PROJECT_CARDS.append(**card_properties)

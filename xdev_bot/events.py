import gidgethub.routing

from .cards import create_new_card

router = gidgethub.routing.Router()


@router.register('issues', action='opened')
async def issue_opened_event(event, gh, *args, **kwargs):
    url, data = create_new_card(event)
    await gh.post(url,
                  data=data,
                  accept='application/vnd.github.inertia-preview+json')

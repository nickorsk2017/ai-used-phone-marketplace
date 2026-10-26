"""`/api/my-listings`: docs/backend/API.md, docs/features/MY_LISTING.md."""

from fastapi import APIRouter, Depends

from modules.main.dependencies import CurrentUser, DbSession
from modules.main.rate_limit import my_listings_rate_limit
from modules.phones import services as phones_service
from modules.phones.schemas import MyListings

router = APIRouter(prefix="/my-listings", tags=["my-listings"], dependencies=[Depends(my_listings_rate_limit)])


@router.get("")
async def list_my_listings(user: CurrentUser, session: DbSession) -> MyListings:
    return MyListings(listings=await phones_service.list_user_phones(session, user.id))

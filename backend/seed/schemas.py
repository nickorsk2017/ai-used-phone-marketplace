"""Shape of one seed listing: the seller index in `USERS` and the body of `POST /api/phones`."""

from typing import NamedTuple

from modules.phones.schemas import PhoneCreate


class SeedListing(NamedTuple):
    user: int
    phone: PhoneCreate

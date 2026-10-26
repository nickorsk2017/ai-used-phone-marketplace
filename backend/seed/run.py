"""Loads the seed users and listings into the database: docs/backend/STRUCTURE.md#seed.

Run from `backend/`: `make seed`, or `make seed-reset` to delete the seed data first.
A repeated run adds only the missing users and listings.
"""

import argparse
import asyncio
import uuid
from collections import Counter

from sqlalchemy import bindparam, text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_engine, run_in_transaction
from modules.phones import services as phones_service
from modules.rag import services as rag_service
from modules.rag.schemas import IndexedPhone
from modules.users import services as users_service
from seed.listing import seed_1, seed_2, seed_3, seed_4, seed_5
from seed.schemas import SeedListing
from seed.users.seed_1 import USERS

LISTINGS: list[SeedListing] = [
    *seed_1.LISTINGS,
    *seed_2.LISTINGS,
    *seed_3.LISTINGS,
    *seed_4.LISTINGS,
    *seed_5.LISTINGS,
]
EMBEDDING_CONCURRENCY = 5

# The domain modules have no lookup by WhatsApp and no delete: the seed tool reads and deletes its own rows directly.
SEED_USER_IDS = text("SELECT id, whatsapp FROM users WHERE whatsapp IN :numbers").bindparams(
    bindparam("numbers", expanding=True)
)
DELETE_SEED_DATA = [
    "DELETE FROM search_index WHERE phone_id IN "
    "(SELECT id FROM phones WHERE user_id IN (SELECT id FROM users WHERE whatsapp IN :numbers))",
    "DELETE FROM phones WHERE user_id IN (SELECT id FROM users WHERE whatsapp IN :numbers)",
    "DELETE FROM users WHERE whatsapp IN :numbers",
]


def check_listings() -> None:
    """One listing per model, every listing has a seed seller."""
    errors = [f"{item.phone.model_name}: unknown user {item.user}" for item in LISTINGS if item.user >= len(USERS)]
    for field in ("model_code", "model_name"):
        counts = Counter(getattr(item.phone, field) for item in LISTINGS)
        errors += [f"duplicate {field}: {value}" for value, count in counts.items() if count > 1]
    if errors:
        raise SystemExit("Invalid seed data:\n" + "\n".join(f"  - {error}" for error in errors))


def _numbers() -> list[str]:
    return [user.whatsapp for user in USERS]


async def delete_seed_data(session: AsyncSession) -> None:
    for statement in DELETE_SEED_DATA:
        await session.execute(text(statement).bindparams(bindparam("numbers", expanding=True)), {"numbers": _numbers()})


async def ensure_users(session: AsyncSession) -> list[uuid.UUID]:
    """IDs of the seed users in the order of `USERS`, missing users are created."""
    rows = await session.execute(SEED_USER_IDS, {"numbers": _numbers()})
    existing = {whatsapp: user_id for user_id, whatsapp in rows}
    ids = []
    for user in USERS:
        if user.whatsapp not in existing:
            existing[user.whatsapp] = (await users_service.create_user(session, user)).id
        ids.append(existing[user.whatsapp])
    return ids


async def existing_listings(session: AsyncSession, user_ids: list[uuid.UUID]) -> set[tuple[uuid.UUID, str]]:
    pairs = set()
    for user_id in set(user_ids):
        pairs |= {(user_id, phone.model_code) for phone in await phones_service.list_user_phones(session, user_id)}
    return pairs


async def embed(listings: list[SeedListing]) -> list[list[float]]:
    """Embeddings before the transaction, as in `POST /api/phones`: docs/backend/DESIGN.md#transaction-retry."""
    semaphore = asyncio.Semaphore(EMBEDDING_CONCURRENCY)

    async def one(item: SeedListing) -> list[float]:
        async with semaphore:
            return await rag_service.embed_listing(
                item.phone.model_name, item.phone.description, item.phone.condition_note
            )

    return await asyncio.gather(*(one(item) for item in listings))


async def main(reset: bool) -> None:
    check_listings()
    try:
        if reset:
            await run_in_transaction(delete_seed_data)
            print("Deleted the seed users and their listings.")

        user_ids = await run_in_transaction(ensure_users)
        existing = await run_in_transaction(lambda session: existing_listings(session, user_ids))
        pending = [item for item in LISTINGS if (user_ids[item.user], item.phone.model_code) not in existing]
        if not pending:
            print(f"Seed is up to date: {len(USERS)} users, {len(LISTINGS)} listings.")
            return

        print(f"Creating embeddings for {len(pending)} listings...")
        embeddings = await embed(pending)

        async def save(session: AsyncSession) -> None:
            for item, embedding in zip(pending, embeddings, strict=True):
                phone = await phones_service.create_phone(session, user_ids[item.user], item.phone)
                indexed = IndexedPhone.model_validate({**phone.model_dump(), "phone_id": phone.id})
                await rag_service.index(session, indexed, embedding)

        await run_in_transaction(save)
        print(f"Added {len(pending)} listings, {len(LISTINGS) - len(pending)} already existed. Users: {len(USERS)}.")
    finally:
        await get_engine().dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load the seed users and listings into the database.")
    parser.add_argument("--reset", action="store_true", help="delete the seed users and their listings first")
    asyncio.run(main(parser.parse_args().reset))

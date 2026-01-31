import asyncio
from config.database import connect_db

async def test():
    try:
        db = await connect_db()
        print('✓ Connected to friend\'s MongoDB Atlas!')
        collections = await db.list_collection_names()
        print(f'Collections: {collections}')
    except Exception as e:
        print(f'✗ Connection failed: {e}')

asyncio.run(test())
import asyncio
from config.database import get_users_collection
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def reset_password():
    users_collection = await get_users_collection()
    
    # Find the user
    user = await users_collection.find_one({"email": "adit123@gmail.com"})
    
    if user:
        print(f"User found: {user['email']}")
        print(f"User ID: {user['_id']}")
        print(f"Has password_hash: {'password_hash' in user}")
        
        # Reset password to "password123"
        new_password = "password123"
        new_hash = pwd_context.hash(new_password)
        
        result = await users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"password_hash": new_hash}}
        )
        
        print(f"\nPassword reset to: {new_password}")
        print(f"Updated {result.modified_count} document(s)")
    else:
        print("User not found!")

if __name__ == "__main__":
    asyncio.run(reset_password())

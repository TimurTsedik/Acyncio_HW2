import aiohttp
import asyncio

BASE_URL = 'http://127.0.0.1:5001'

async def register(email, password):
    async with aiohttp.ClientSession() as session:
        async with session.post(f'{BASE_URL}/register', json={'email': email, 'password': password}) as response:
            return await response.json()

async def login(email, password):
    session = aiohttp.ClientSession()
    async with session.post(f'{BASE_URL}/login', json={'email': email, 'password': password}) as response:
        if response.status == 200:
            return session, await response.json()
        else:
            await session.close()
            return None, await response.json()

async def create_ad(session, title, description, user_id):
    async with session.post(f'{BASE_URL}/ads', json={'title': title, 'description': description, 'user_id': user_id}) as response:
        return await response.json()

async def get_ad(session, ad_id):
    async with session.get(f'{BASE_URL}/ads/{ad_id}') as response:
        return await response.json()

async def update_ad(session, ad_id, title=None, description=None):
    data = {}
    if title:
        data['title'] = title
    if description:
        data['description'] = description
    async with session.put(f'{BASE_URL}/ads/{ad_id}', json=data) as response:
        return await response.json()

async def delete_ad(session, ad_id):
    async with session.delete(f'{BASE_URL}/ads/{ad_id}') as response:
        return await response.json()

async def logout(session):
    async with session.post(f'{BASE_URL}/logout') as response:
        return await response.json()

async def main():
    # Register a new user
    print("Registering a new user...")
    print(await register('user@example.com', 'password'))

    # Login the user
    print("Logging in the user...")
    session, login_response = await login('user@example.com', 'password')
    print(login_response)

    if session:
        user_id = login_response.get('id')  # Assuming the login response contains user ID

        # Create a new ad
        print("Creating a new ad...")
        create_response = await create_ad(session, 'My First Ad', 'This is a description of my first ad', user_id)
        print(create_response)

        ad_id = create_response.get('ad_id')

        # Get the ad
        print("Getting the ad...")
        print(await get_ad(session, ad_id))

        # Update the ad
        print("Updating the ad...")
        print(await update_ad(session, ad_id, title='Updated Ad', description='Updated description'))

        # Delete the ad
        print("Deleting the ad...")
        print(await delete_ad(session, ad_id))

        # Logout the user
        print("Logging out the user...")
        print(await logout(session))

        await session.close()

if __name__ == '__main__':
    asyncio.run(main())

import os
import aiohttp
import asyncio
import aiopg
from aiohttp import web

BASE_URL = 'http://127.0.0.1:5000'
DSN = os.getenv('DATABASE_URL', 'dbname=test user=postgres password=secret host=db port=5432')

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);
"""

CREATE_ADS_TABLE = """
CREATE TABLE IF NOT EXISTS ads (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id)
);
"""

async def init_pg(app):
    app['db'] = await aiopg.create_pool(DSN)
    async with app['db'].acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(CREATE_USERS_TABLE)
            await cur.execute(CREATE_ADS_TABLE)

async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()

async def register_user(request):
    try:
        data = await request.json()
        email = data['email']
        password = data['password']
        async with request.app['db'].acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
                return web.json_response({'status': 'success'})
    except Exception as e:
        return web.json_response({'status': 'error', 'message': str(e)})

async def login_user(request):
    try:
        data = await request.json()
        email = data['email']
        password = data['password']
        async with request.app['db'].acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
                user = await cur.fetchone()
                if user:
                    return web.json_response({'status': 'success', 'id': user[0]})
                else:
                    return web.json_response({'status': 'fail'}, status=401)
    except Exception as e:
        return web.json_response({'status': 'error', 'message': str(e)})

async def create_ad_db(request):
    try:
        data = await request.json()
        title = data['title']
        description = data['description']
        user_id = data['user_id']
        async with request.app['db'].acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("INSERT INTO ads (title, description, user_id) VALUES (%s, %s, %s)", (title, description, user_id))
                await cur.execute("SELECT id FROM ads WHERE title = %s AND description = %s AND user_id = %s", (title, description, user_id))
                ad_id = await cur.fetchone()
                return web.json_response({'status': 'success', 'ad_id': ad_id[0]})
    except Exception as e:
        return web.json_response({'status': 'error', 'message': str(e)})

async def get_ad_db(request):
    try:
        ad_id = request.match_info['ad_id']
        async with request.app['db'].acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM ads WHERE id = %s", (ad_id,))
                ad = await cur.fetchone()
                if ad:
                    return web.json_response({'ad': ad})
                else:
                    return web.json_response({'status': 'not found'}, status=404)
    except Exception as e:
        return web.json_response({'status': 'error', 'message': str(e)})

async def update_ad_db(request):
    try:
        ad_id = request.match_info['ad_id']
        data = await request.json()
        async with request.app['db'].acquire() as conn:
            async with conn.cursor() as cur:
                if 'title' in data:
                    await cur.execute("UPDATE ads SET title = %s WHERE id = %s", (data['title'], ad_id))
                if 'description' in data:
                    await cur.execute("UPDATE ads SET description = %s WHERE id = %s", (data['description'], ad_id))
                return web.json_response({'status': 'success'})
    except Exception as e:
        return web.json_response({'status': 'error', 'message': str(e)})

async def delete_ad_db(request):
    try:
        ad_id = request.match_info['ad_id']
        async with request.app['db'].acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("DELETE FROM ads WHERE id = %s", (ad_id,))
                return web.json_response({'status': 'success'})
    except Exception as e:
        return web.json_response({'status': 'error', 'message': str(e)})

async def logout_user(request):
    try:
        return web.json_response({'status': 'success'})
    except Exception as e:
        return web.json_response({'status': 'error', 'message': str(e)})

app = web.Application()
app.on_startup.append(init_pg)
app.on_cleanup.append(close_pg)
app.router.add_post('/register', register_user)
app.router.add_post('/login', login_user)
app.router.add_post('/ads', create_ad_db)
app.router.add_get('/ads/{ad_id}', get_ad_db)
app.router.add_put('/ads/{ad_id}', update_ad_db)
app.router.add_delete('/ads/{ad_id}', delete_ad_db)
app.router.add_post('/logout', logout_user)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5001)

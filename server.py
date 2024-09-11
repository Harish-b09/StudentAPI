from aiohttp import web
import aiopg
import aioredis
import json


async def init_pg(app):
    app['postgres_conn'] = await aiopg.create_pool(dsn='dbname=student_db user=postgres_st password=postgres_st host=localhost')
    yield
    app['postgres_conn'].close()
    await app['postgres_conn'].wait_closed()


async def init_redis(app):
   app['redis'] = await aioredis.from_url('redis://localhost',decode_responses=True)
   yield
   await app['redis'].close()


async def handle_get(request):
    studentid = request.match_info.get('studentid')
    async with request.app['postgres_conn'].acquire() as conn:
        async with conn.cursor() as cur:
            if studentid:
                await cur.execute('SELECT studentid, studentname, studentage FROM students WHERE studentid=%s', (studentid,))
                student = await cur.fetchone()
                if student:
                    return web.json_response({'studentid': student[0], 'studentname': student[1], 'studentage': student[2]})
                return web.json_response({'error': 'Student not found'}, status=404)
            else:
                await cur.execute('SELECT studentid, studentname, studentage FROM students ORDER BY studentid')
                students = await cur.fetchall()
                return web.json_response([{'studentid': row[0], 'studentname': row[1], 'studentage': row[2]} for row in students])


async def handle_post(request):
    data = await request.json()
    async with request.app['postgres_conn'].acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute('INSERT INTO students (studentname, studentage) VALUES (%s, %s) RETURNING studentid',
                              (data['studentname'], data['studentage']))
            studentid = await cur.fetchone()
            data['studentid'] = studentid[0]
            await request.app['redis'].set(f'student:{studentid[0]}', json.dumps(data))
            return web.json_response({'studentid': studentid[0],'studentname':data['studentname'],'studentage':data['studentage']}, status=201)


async def handle_put(request):
    studentid = int(request.match_info['studentid'])
    data = await request.json()
    async with request.app['postgres_conn'].acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute('UPDATE students SET studentname=%s, studentage=%s WHERE studentid=%s RETURNING studentid',
                              (data['studentname'], data['studentage'], studentid))
            if cur.rowcount:
                data['studentid'] = studentid
                await request.app['redis'].set(f'student:{studentid}', json.dumps(data))
                return web.json_response({'studentid': studentid})
            return web.json_response({'error': 'Student not found'}, status=404)


async def handle_patch(request):
    studentid = int(request.match_info['studentid'])
    data = await request.json()
    async with request.app['postgres_conn'].acquire() as conn:
        async with conn.cursor() as cur:
            query_parts = [f'{key}=%s' for key in data.keys()]
            query = f'UPDATE students SET {", ".join(query_parts)} WHERE studentid=%s RETURNING studentid'
            values = list(data.values()) + [studentid]
            await cur.execute(query, values)
            if cur.rowcount:
                data['studentid'] = studentid
                await request.app['redis'].set(f'student:{studentid}', json.dumps(data))
                return web.json_response({'studentid': studentid})
            return web.json_response({'error': 'Student not found'}, status=404)


async def handle_delete(request):
    studentid = int(request.match_info['studentid'])
    async with request.app['postgres_conn'].acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute('DELETE FROM students WHERE studentid=%s RETURNING studentid', (studentid,))
            if cur.rowcount:
                await request.app['redis'].delete(f'student:{studentid}')
                return web.json_response({'studentid': studentid})
            return web.json_response({'error': 'Student not found'}, status=404)


app = web.Application()
app.cleanup_ctx.append(init_pg)
app.cleanup_ctx.append(init_redis)
app.add_routes([
    web.get('/students', handle_get),
    web.get('/students/{studentid}', handle_get),
    web.post('/students', handle_post),
    web.put('/students/{studentid}', handle_put),
    web.patch('/students/{studentid}', handle_patch),
    web.delete('/students/{studentid}', handle_delete)
])


if __name__ == '__main__':
    web.run_app(app, host='192.168.1.35', port=8080)
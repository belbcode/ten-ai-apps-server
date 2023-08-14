import asyncio
async def batch(function, jobs, callback):
    for job in jobs:
        worker = await asyncio.create_task(function(job))
        worker.add_done_callback(callback)
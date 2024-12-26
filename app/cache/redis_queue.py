from rq import Queue
from rq.job import Job
from redis import Redis

class EncoderQueue:
    def __init__(self, app):
        self.redis_conn = Redis.from_url(app.config['REDIS_URL'])
        self.queue = Queue('encoder_tasks', connection=self.redis_conn)
    
    def enqueue_status_update(self, encoder_id):
        """Queue a status update job"""
        job = self.queue.enqueue(
            'app.tasks.update_encoder_status',
            encoder_id,
            job_timeout='5m'
        )
        return job.id
        
    def get_job_status(self, job_id):
        """Check status of a queued job"""
        job = Job.fetch(job_id, connection=self.redis_conn)
        return {
            'status': job.get_status(),
            'result': job.result,
            'error': job.exc_info
        }

# Example background task
def update_encoder_status_background(encoder_id):
    # Long-running task code here
    pass 
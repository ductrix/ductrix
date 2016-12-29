
from rq.compat import as_text, decode_redis_hash
try:
    import cPickle as pickle
except ImportError:  # noqa
    import pickle

def get_all_jobs(queue = None, redis_conn = None):
    '''
    This is pretty much a ripoff of what RQ does for queued jobs, recreated so
    that we can grab ALL jobs.
    '''
    def to_date(date_str):
        if date_str is None:
            return
        else:
            return as_text(date_str)
            return utcparse(as_text(date_str))


    def unpickle(pickled_string):
        try:
            obj = pickle.loads(pickled_string)
        except Exception as e:
            print str(e)
            obj = None
            #raise 'Could not unpickle. {0}'.format(str(e))
            #raise UnpickleError('Could not unpickle.', pickled_string, e)
        return obj


    job_ids = redis_conn.keys('rq:job:*')
    #jobs = {}
    jobs = []

    for job_id in job_ids:
        obj = decode_redis_hash(redis_conn.hgetall(job_id))
        if len(obj) == 0:
            pass
        if queue is not None:
            if queue != as_text(obj.get('origin')):
                # If a specific queue was requested and this job isn't it, don't
                # process the details of this job and don't return the job.
                pass
        #jobs[job_id] = {
        jobs.append({
            'job_id': job_id.replace('rq:job:', ''),
            'created_at': obj.get('created_at'),
            'origin': as_text(obj.get('origin')),
            'description': as_text(obj.get('description')),
            'enqueued_at': to_date(as_text(obj.get('enqueued_at'))),
            'ended_at': to_date(as_text(obj.get('ended_at'))),
            'result': unpickle(obj.get('result')) if obj.get('result') else None,  # noqa
            'exc_info': obj.get('exc_info'),
            'timeout': int(obj.get('timeout')) if obj.get('timeout') else None,
            'result_ttl': int(obj.get('result_ttl')) if obj.get('result_ttl') else None,  # noqa
            'status': as_text(obj.get('status') if obj.get('status') else None),
            'dependency_id': as_text(obj.get('dependency_id', None)),
            'meta': unpickle(obj.get('meta')) if obj.get('meta') else {}})

    return sorted(jobs, key=lambda k: k['status']) 
    #return jobs


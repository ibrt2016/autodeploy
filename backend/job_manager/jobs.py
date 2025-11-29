class JobManager:
    def __init__(self):
        self.jobs = {}

    def create_job(self, job_id):
        self.jobs[job_id] = {"logs": [], "status": "running"}

    def log(self, job_id, message):
        self.jobs[job_id]["logs"].append(message)

    def get_job(self, job_id):
        return self.jobs.get(job_id, {"error": "not found"})

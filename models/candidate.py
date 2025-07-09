class Candidate:
    def __init__(self, name, job_id, cv_link):
        self.name = name
        self.job_id = job_id
        self.cv_link = cv_link
        self.score = 0

    def set_score(self, score):
        self.score = score

    def get_info(self):
        return {
            "name": self.name,
            "job_id": self.job_id,
            "cv_link": self.cv_link,
            "score": self.score
        }
class Job:
    def __init__(self, job_id, required_skills):
        self.job_id = job_id
        self.required_skills = required_skills

    def get_job_id(self):
        return self.job_id

    def get_required_skills(self):
        return self.required_skills

    def score_candidate(self, candidate_skills):
        score = 0
        for skill in self.required_skills:
            if skill in candidate_skills:
                score += 1
        return score
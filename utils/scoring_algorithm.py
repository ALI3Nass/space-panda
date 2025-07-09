def score_candidates(candidates, job_skills):  # Renamed from score_candidate
    scored_candidates = []

    for candidate in candidates:
        score = 0
        cv_content = candidate['cv_content']

        for skill in job_skills:
            if skill.lower() in cv_content.lower():
                score += 1

        scored_candidates.append({
            'name': candidate['name'],
            'job_id': candidate['job_id'],
            'score': score
        })

    return scored_candidates


def select_top_candidates(scored_candidates, top_n=5):
    job_candidates = {}

    for candidate in scored_candidates:
        job_id = candidate['job_id']
        if job_id not in job_candidates:
            job_candidates[job_id] = []
        job_candidates[job_id].append(candidate)

    top_candidates = {}

    for job_id, candidates in job_candidates.items():
        sorted_candidates = sorted(
            candidates, key=lambda x: x['score'], reverse=True)
        top_candidates[job_id] = sorted_candidates[:top_n]

    return top_candidates


def rename_cv_files(top_candidates, cv_folder='shortlisted_cvs/'):
    renamed_files = []

    for job_id, candidates in top_candidates.items():
        for index, candidate in enumerate(candidates, start=1):
            # Assuming the original name is stored
            original_cv_name = f"{candidate['name']}.pdf"
            new_cv_name = f"{cv_folder}{job_id}_{index}.pdf"
            # Here you would add the logic to rename/move the file
            renamed_files.append({
                'original_name': original_cv_name,
                'new_name': new_cv_name,
                'candidate_name': candidate['name'],
                'score': candidate['score']
            })

    return renamed_files

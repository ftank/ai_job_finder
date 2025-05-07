def match_jobs(profile, jobs, threshold=0.2):
    # Simple keyword overlap matching for demonstration
    resume_text = profile.get('raw_text', '').lower()
    matched = []
    for job in jobs:
        job_text = (job['title'] + ' ' + job['description']).lower()
        overlap = sum(1 for word in job_text.split() if word in resume_text)
        score = overlap / max(1, len(job_text.split()))
        if score >= threshold:
            job['match_score'] = score
            matched.append(job)
    # TODO: Use AI embeddings or LLM for better matching
    return matched 
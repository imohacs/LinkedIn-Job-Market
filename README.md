# LinkedIn Job Market — V8

Seven interactive sections: Market Story, Jobs & Skills, City Explorer, Salary Lab, Career Comparison, Skill Gap Analyzer, and Best City for Your Career.

## Run

1. Run the original EDA notebook and export the final `df_cleaned` as `linkedin_job_postings_cleaned.csv`, including `title`, `extracted_skills`, `location`, `normalized_salary`, `currency`, and `formatted_experience_level`.
2. Place the CSV next to `app.py` (not in the `assets/` folder). No file uploads are required by site visitors.
3. Run `pip install -r requirements.txt` and `streamlit run app.py`.

All career-specific analyses use the exported dataset. The 30 available job titles in the skills and salary explorers are ordered by eligible advertisement count. Match scores are descriptive keyword coverage, not employment probabilities.

import openai
import json
from django.conf import settings

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)  # Corrected API client

def rank_candidates(job_description, candidates):
    """
    Uses OpenAI API to rank candidates based on job description.
    """
    prompt = f"""
    You are an AI assistant helping a company shortlist job applicants.
    Given the job description and candidate profiles, rank the candidates from best to worst.

    Job Description:
    {job_description}

    Candidates:
    {candidates}

    Output the ranking in **valid JSON format only** (without markdown or extra text):

    [
        {{
            "name": "Candidate Name",
            "email": "candidate@example.com",
            "score": 95
        }}
    ]
    """

    try:
        response = client.chat.completions.create(  
            model="gpt-4o-mini",  # Change to an available model
            messages=[{"role": "user", "content": prompt}],  # Use "user" role
            temperature=0.2
        )

        ai_content = response.choices[0].message.content.strip()
        print("AI Response Content:", ai_content)  # Debugging

        # Remove Markdown formatting if present
        if ai_content.startswith("```json"):
            ai_content = ai_content[7:-3].strip()  # Remove ```json ... ```

        ranked_candidates = json.loads(ai_content)  # Parse JSON safely
        return ranked_candidates
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
        return []
    except Exception as e:
        print("OpenAI API Error:", e)
        return []

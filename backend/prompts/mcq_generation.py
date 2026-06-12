import json

from models.assessment import AssessmentConfig


def build_mcq_generation_prompt(
    config: AssessmentConfig,
    count: int,
    previously_asked: list[str] | None = None,
) -> str:
    previously_asked = previously_asked or []
    avoid_section = ""
    if previously_asked:
        avoid_section = (
            "\n\nDo NOT repeat or closely rephrase these previously asked questions:\n"
            + "\n".join(f"- {q}" for q in previously_asked)
        )

    objectives = config.learning_objectives.strip() or "General proficiency in the topic"

    return f"""You are an expert technical interviewer creating industry-grade multiple choice assessments.

Generate exactly {count} unique MCQ questions as a JSON array.

Assessment parameters:
- Skill Category: {config.skill_category}
- Topic: {config.topic}
- Difficulty: {config.difficulty}
- Experience Level: {config.experience_level}
- Assessment Type: {config.assessment_type}
- Learning Objectives: {objectives}

Requirements:
1. Questions must be technically accurate and reflect real industry scenarios.
2. Each question must have exactly 4 options with meaningful distractors.
3. Match the requested difficulty level ({config.difficulty}).
4. Tailor complexity to {config.experience_level} experience level.
5. Include a detailed explanation for why the correct answer is right.
6. No duplicate or near-duplicate questions.
7. Return ONLY valid JSON — no markdown, no code fences.

JSON schema for each item:
{{
  "question": "Question text",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correctAnswer": "Exact text of one option from the options array",
  "explanation": "Detailed explanation",
  "difficulty": "{config.difficulty}",
  "topic": "{config.topic}"
}}
{avoid_section}

Return a JSON array of {count} objects."""


def build_mcq_fix_json_prompt(raw_response: str) -> str:
    return f"""The following response was invalid JSON. Fix it and return ONLY a valid JSON array of MCQ objects.

Invalid response:
{raw_response}

Each object must have: question, options (4 items), correctAnswer, explanation, difficulty, topic."""


def build_feedback_prompt(
    config: AssessmentConfig,
    results_summary: list[dict],
    accuracy_percent: float,
) -> str:
    return f"""You are an expert technical coach analyzing assessment results.

Assessment context:
- Skill Category: {config.skill_category}
- Topic: {config.topic}
- Difficulty: {config.difficulty}
- Experience Level: {config.experience_level}
- Assessment Type: {config.assessment_type}
- Overall Accuracy: {accuracy_percent}%

Per-question results:
{json.dumps(results_summary, indent=2)}

Generate personalized feedback as JSON only (no markdown):
{{
  "summary": "2-3 sentence personalized narrative about performance",
  "strengths": ["strength 1", "strength 2"],
  "improvements": ["area 1", "area 2"],
  "topic_breakdown": [
    {{ "topic": "topic name", "accuracy": 80.0, "correct": 4, "total": 5 }}
  ]
}}"""

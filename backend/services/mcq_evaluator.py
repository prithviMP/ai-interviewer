from models.questions.mcq import MCQQuestion


class MCQEvaluator:
    def evaluate(self, question: MCQQuestion, selected_answer: str) -> dict:
        correct = selected_answer.strip() == question.correct_answer.strip()
        return {
            "correct": correct,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation,
        }

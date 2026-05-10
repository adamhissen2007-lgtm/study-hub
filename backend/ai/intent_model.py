class IntentClassifier:
    def classify(self, text):
        text = text.lower()
        if "اشرح" in text or "what is" in text:
            return "explain"
        if "مثال" in text:
            return "give_example"
        if "تمرين" in text or "حل" in text:
            return "give_exercise"
        return "ask_question"

    def detect_difficulty(self, text):
        if "مبتدئ" in text or "سهل" in text:
            return 1
        if "متقدم" in text or "صعب" in text:
            return 3
        return 2

intent_model = IntentClassifier()
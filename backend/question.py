class Question:
    def __init__(self, id, statement, answer, image, value, category):
        self.id = id
        self.statement = statement
        self.answer = answer
        self.image = image
        self.value = value
        self.category = category
        self.answered = False

from telegram import Update
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd
import numpy as np

class DecisionTreeClassifier:

    def __init__(self):
        self.questions = [
            "Did the caller verify their identity?",
            "Did the caller ask for personal information?",
            "Did the caller use urgency tactics?",
            "Did the caller have unusual requests or behavior?",
            "Did the caller follow verification procedures?",
            "Were there any spelling or grammar mistakes?"
        ]
        self.responses = []
        self.index = 0
        self.dt_model = self.train_model()

    def start_quiz(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text=self.questions[self.index])

    def collect_response(self, update, context):
        # Here, we assume the responses are 'yes' or 'no', and map them to 1 and 0 respectively
        response = 1 if update.message.text.lower() == 'yes' else 0
        self.responses.append(response)
        self.index += 1
        if self.index < len(self.questions):
            context.bot.send_message(chat_id=update.effective_chat.id, text=self.questions[self.index])

    def is_quiz_complete(self):
        return self.index == len(self.questions)

    def analyze_responses(self):
        pred = self.dt_model.predict([self.responses])
        self.reset()
        return "Potential vishing detected." if pred[0] == 1 else "No vishing detected."

    def reset(self):
        self.responses = []
        self.index = 0

    def train_model(self):
        # You should replace this with your actual data
        df = pd.read_csv('data.csv')
        X = df.iloc[:, :-1].values
        y = df.iloc[:, -1].values

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
        model = DecisionTreeClassifier()
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        print('Accuracy: ', accuracy_score(y_test, y_pred))

        return model

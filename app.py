from flask import Flask, request, render_template, redirect, url_for, session
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
import numpy as np

app = Flask(__name__)
app.secret_key = "choose_db_secret_key"

# Example training data (answers mapped to unique categories)
X_train = np.array([
   [0, 0, 0],  # Operational, Batch, SQL -> 9
   [0, 1, 0],  # Operational, Consistent Data, SQL -> [1, 2]
   [0, 1, 1],  # Operational, Consistent Data, Multi-attribute -> 5
   [0, 2, 2],  # Operational, Near-Real-Time, Key-only -> [4, 9]
   [0, 2, 1],  # Operational, Near-Real-Time, Multi-attribute -> 6
   [1, 0, 0],  # Analytical, Batch, SQL -> 3
   [1, 0, 1],  # Analytical, Batch, Multi-attribute -> 7
   [1, 1, 0],  # Analytical, Consistent Data -> 3
   [1, 2, 1],  # Analytical, Near-Real-Time -> 10
   [2, 1, 0],  # HTAP, SQL -> [1, 11]
   [2, 1, 1],  # HTAP, Multi-attribute -> 12
])

# Flatten the targets to make them compatible with LabelEncoder
y_train_raw = [
   [9], [1, 2], [5], [4, 9], [6], [3], [7], [3], [10], [1, 11], [12]
]

# Encode the labels
label_encoder = LabelEncoder()
y_train_encoded = label_encoder.fit_transform([str(label) for label in y_train_raw])

# Train the Decision Tree model
model = DecisionTreeClassifier()
model.fit(X_train, y_train_encoded)

@app.route('/')
def start():
   session.clear()  # Clear session at the start
   session["answers"] = []  # Initialize an empty answers list
   print("DEBUG: Session cleared and answers initialized.")
   return redirect(url_for('question', step=1))

@app.route('/question/<int:step>', methods=['GET', 'POST'])
def question(step):
   if request.method == 'POST':
       answer = int(request.form.get('answer'))  # Store answers as integers
       session["answers"].append(answer)  # Append to session answers
       print(f"DEBUG: Added '{answer}' to answers: {session['answers']}")
       return redirect(url_for('question', step=step + 1))

   # Define questions based on the step number
   if step == 1:
       question_text = "Select your use case: Operational (0), Analytical (1), or HTAP (2)"
   elif step == 2:
       question_text = "Select your data requirement: Batch (0), Consistent Data (1), or Near-Real-Time (2)"
   elif step == 3:
       question_text = "Select your query type: SQL (0), Multi-attribute (1), or Key-only (2)"
   else:
       return redirect(url_for('result'))

   return render_template('question.html', question=question_text, step=step)

@app.route('/result')
def result():
   answers = np.array(session.get("answers", [])).reshape(1, -1)
   print(f"DEBUG: Answers for prediction: {answers}")

   prediction_encoded = model.predict(answers)[0]
   prediction_decoded = label_encoder.inverse_transform([prediction_encoded])[0]

   print(f"DEBUG: Predicted databases: {prediction_decoded}")

   return render_template('result.html', databases=prediction_decoded)

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000)

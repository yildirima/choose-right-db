from flask import Flask, request, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "choose_db_secret_key"

# Database mapping based on decision paths path_to_databases = {
    ("Operational", "Batch"): [9],  # Object Stores
    ("Operational", "Consistent Data", "SQL"): [1, 2],  # Relational DB & Distributed SQL
    ("Operational", "Consistent Data", "Multi-attribute"): [5],  # Document Data Stores
    ("Operational", "Near-Real-Time Performance", "Key-only"): [4, 9],  # Key-Value & Object Stores
    ("Operational", "Near-Real-Time Performance", "Multi-attribute"): [6],  # Wide-Column Data Stores
    ("Analytical", "Batch", "SQL"): [3],  # Relational Data Warehouses
    ("Analytical", "Batch", "Multi-attribute"): [7],  # Graph Data Stores
    ("Analytical", "Consistent Data"): [3],  # Relational Data Warehouses
    ("Analytical", "Near-Real-Time Performance"): [10],  # Real-time Analytic Engines
    ("HTAP", "SQL"): [1, 11],  # Relational DB & Transactional/Analytical RDBMS
    ("HTAP", "Multi-attribute"): [12]  # In-memory Data Store/Grid }

@app.route('/')
def start():
    session.clear()  # Clear the session at the start
    session["path"] = []  # Initialize an empty path
    print("DEBUG: Session cleared and path initialized.")
    return redirect(url_for('question', step=1))

@app.route('/question/<int:step>', methods=['GET', 'POST']) def question(step):
    # Ensure the path is properly initialized in case of unexpected issues
    if "path" not in session:
        session["path"] = []

    if request.method == 'POST':
        answer = request.form.get('answer')
        session["path"].append(answer)  # Append the answer to the path
        print(f"DEBUG: Added '{answer}' to path: {session['path']}")
        return redirect(url_for('question', step=step + 1))

    # Define questions based on the step number
    if step == 1:
        question_text = "Is your use case Operational, Analytical, or HTAP?"
        options = ['Operational', 'Analytical', 'HTAP']
    elif step == 2 and len(session["path"]) > 0 and session["path"][0] == 'Operational':
        question_text = "Do you need Consistent Data, Near-Real-Time Performance, or Batch?"
        options = ['Consistent Data', 'Near-Real-Time Performance', 'Batch']
    elif step == 2 and len(session["path"]) > 0 and session["path"][0] == 'Analytical':
        question_text = "Do you need Batch, Consistent Data, or Near-Real-Time Performance?"
        options = ['Batch', 'Consistent Data', 'Near-Real-Time Performance']
    elif step == 2 and len(session["path"]) > 0 and session["path"][0] == 'HTAP':
        question_text = "Do you prefer SQL or Multi-attribute queries?"
        options = ['SQL', 'Multi-attribute']
    elif step == 3 and session["path"][:2] == ['Operational', 'Consistent Data']:
        question_text = "Do you prefer SQL or Multi-attribute queries?"
        options = ['SQL', 'Multi-attribute']
    elif step == 3 and session["path"][:2] == ['Operational', 'Near-Real-Time Performance']:
        question_text = "Do you prefer Key-only or Multi-attribute queries?"
        options = ['Key-only', 'Multi-attribute']
    elif step == 3 and session["path"][:2] == ['Analytical', 'Batch']:
        question_text = "Do you prefer SQL or Multi-attribute queries?"
        options = ['SQL', 'Multi-attribute']
    else:
        return redirect(url_for('result'))

    return render_template('question.html', question=question_text, options=options, step=step)

@app.route('/result')
def result():
    path = tuple(session.get("path", []))  # Retrieve the path from session
    print(f"DEBUG: Final path = {path}")

    databases = path_to_databases.get(path, ["No matching databases found."])
    print(f"DEBUG: Databases = {databases}")

    return render_template('result.html', databases=databases)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

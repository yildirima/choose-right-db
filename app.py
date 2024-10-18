from flask import Flask, request, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "choose_db_secret_key"

# Database lists based on the decision tree
database_lists = {
   1: ["Azure SQL Database", "Oracle Database", "Amazon Aurora"],
   2: ["Google Cloud Spanner", "Cockroach Labs", "NuoDB", "Yugabyte"],
   3: ["Amazon Redshift", "Azure Synapse", "Google BigQuery"],
   4: ["Aerospike", "Amazon DynamoDB"],
   5: ["MongoDB", "Couchbase", "RavenDB", "Azure Cosmos DB", "MarkLogic"],
   6: ["Apache Cassandra", "DataStax Enterprise (DSE)"],
   7: ["Apache TinkerPop", "Neo4j", "OrientDB", "TigerGraph"],
   8: ["Amazon EMR", "Cloudera", "Azure HDInsight", "Apache Hadoop Ozone", "Apache HBase"],
   9: ["Amazon S3", "Azure Blob Storage"],
   10: ["Spark", "Storm", "Amazon Kinesis", "Azure Stream Analytics", "Google Cloud Dataflow"],
   11: ["VoltDB", "SAP HANA", "SingleStore"],
   12: ["Hazelcast", "Redis", "Gridgain"]
}

@app.route('/')
def start():
   session.clear()  # Clear previous session data
   return redirect(url_for('question', step=1))

@app.route('/question/<int:step>', methods=['GET', 'POST'])
def question(step):
   if request.method == 'POST':
       answer = request.form.get('answer')
       session[f'answer_{step}'] = answer  # Save answer in session
       return redirect(url_for('question', step=step + 1))

   # Step-based questions with conditional logic
   if step == 1:
       question_text = "Is your use case Operational, Analytical, or HTAP?"
       options = ['Operational', 'Analytical', 'HTAP']
   elif step == 2:
       if session['answer_1'] == 'Operational':
           question_text = "Do you need Consistent Data, Near-Real-Time Performance, or Batch?"
           options = ['Consistent Data', 'Near-Real-Time Performance', 'Batch']
       elif session['answer_1'] == 'Analytical':
           question_text = "Do you need Batch, Consistent Data, or Near-Real-Time Performance?"
           options = ['Batch', 'Consistent Data', 'Near-Real-Time Performance']
       elif session['answer_1'] == 'HTAP':
           question_text = "Do you prefer SQL or Multi-attribute queries?"
           options = ['SQL', 'Multi-attribute']
   elif step == 3:
       if session['answer_2'] == 'Consistent Data' and session['answer_1'] == 'Operational':
           question_text = "Do you prefer SQL or Multi-attribute queries?"
           options = ['SQL', 'Multi-attribute']
       elif session['answer_2'] == 'Near-Real-Time Performance':
           question_text = "Do you prefer Key-only or Multi-attribute queries?"
           options = ['Key-only', 'Multi-attribute']
       elif session['answer_2'] == 'Batch' and session['answer_1'] == 'Analytical':
           question_text = "Do you prefer SQL or Multi-attribute queries?"
           options = ['SQL', 'Multi-attribute']
       else:
           return redirect(url_for('result'))
   else:
       return redirect(url_for('result'))

   return render_template('question.html', question=question_text, options=options, step=step)

@app.route('/result')
def result():
   # Determine the correct database categories based on user input
   db_categories = determine_categories()
   databases = [db for cat in db_categories for db in database_lists.get(cat, [])]
   return render_template('result.html', databases=databases)

def determine_categories():
   # Retrieve answers from session
   answer_1 = session.get('answer_1')
   answer_2 = session.get('answer_2')
   answer_3 = session.get('answer_3')

   # Logic based on the decision tree
   if answer_1 == 'Operational':
       if answer_2 == 'Batch':
           return [9]  # Object Stores
       elif answer_2 == 'Consistent Data':
           return [1, 2] if answer_3 == 'SQL' else [5]  # Relational & Distributed SQL or Document Data Stores
       elif answer_2 == 'Near-Real-Time Performance':
           return [4, 9] if answer_3 == 'Key-only' else [6]  # Key-Value & Object Stores or Wide-Column Data Stores
   elif answer_1 == 'Analytical':
       if answer_2 == 'Batch':
           return [3] if answer_3 == 'SQL' else [7]  # Relational Warehouses or Graph Data Stores
       elif answer_2 == 'Consistent Data':
           return [3]  # Relational Data Warehouses
       else:
           return [10]  # Real-time Analytic Engines
   elif answer_1 == 'HTAP':
       if answer_3 == 'SQL':
           return [1, 11]  # Relational DB Systems + Transactional/Analytical RDBMS
       elif answer_3 == 'Multi-attribute':
           return [12]  # In-memory Data Store/Grid

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000)

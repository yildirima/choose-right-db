# app.py
from flask import Flask, request, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "choose_db_secret_key"

# Database lists based on the decision tree screenshot
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
       session[f'answer_{step}'] = answer  # Store answer in session
       return redirect(url_for('question', step=step + 1))

   # Render questions based on the step
   if step == 1:
       question_text = "Is your use case Operational or Analytical?"
       options = ['Operational', 'Analytical']
   elif step == 2:
       if session['answer_1'] == 'Operational':
           question_text = "Do you need Consistent Data, Near-Real-Time Performance, or Batch?"
           options = ['Consistent Data', 'Near-Real-Time Performance', 'Batch']
       else:
           question_text = "Does your workload need HTAP/Augmented Transactions?"
           options = ['Yes', 'No']
   elif step == 3:
       if session['answer_1'] == 'Operational':
           question_text = "Do you prefer SQL or Multi-attribute queries?"
           options = ['SQL', 'Multi-attribute']
       else:
           question_text = "Do you need Batch, Consistent Data, or Near-Real-Time Performance?"
           options = ['Batch', 'Consistent Data', 'Near-Real-Time Performance']
   else:
       return redirect(url_for('result'))

   return render_template('question.html', question=question_text, options=options, step=step)

@app.route('/result')
def result():
   # Determine the database category based on answers
   db_category = determine_category()
   databases = database_lists.get(db_category, ["No matching database found."])
   return render_template('result.html', databases=databases)

def determine_category():
   answer_1 = session.get('answer_1')
   answer_2 = session.get('answer_2')
   answer_3 = session.get('answer_3')

   # Logic based on the decision tree
   if answer_1 == 'Operational':
       if answer_2 == 'Consistent Data':
           return 1 if answer_3 == 'SQL' else 5
       elif answer_2 == 'Near-Real-Time Performance':
           return 4 if answer_3 == 'SQL' else 6
       else:
           return 9  # Batch
   else:
       if answer_2 == 'Yes':  # HTAP/Augmented Transactions
           return 11 if answer_3 == 'SQL' else 12
       else:
           if answer_3 == 'Batch':
               return 8
           elif answer_3 == 'Consistent Data':
               return 3
           else:
               return 10  # Near-Real-Time Performance

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000)

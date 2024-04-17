from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os


app = Flask(__name__)
template_dir = os.path.abspath('/home/akk1/site/')
app = Flask(__name__, template_folder=template_dir)
db_path = os.path.join(os.path.dirname(__file__), 'tasks.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)  # Дата создания задания
    archived = db.Column(db.Boolean, default=False)

# Создаем базу данных и таблицу, если они не существуют
if not os.path.exists(db_path):
    with app.app_context():
        db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_task_content = request.form['input_text'].strip()
        if new_task_content:
            new_task = Task(content=new_task_content)
            db.session.add(new_task)
            db.session.commit()
    tasks = Task.query.filter_by(archived=False).order_by(Task.created_at.desc()).all()
    archived_tasks = Task.query.filter_by(archived=True).order_by(Task.created_at.desc()).all()
    return render_template('index.html', tasks=tasks, archived_tasks=archived_tasks)

@app.route('/archive/<int:task_id>', methods=['POST'])
def archive_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.archived = not task.archived
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/restore/<int:task_id>', methods=['POST'])
def restore_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.archived = not task.archived
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/clear_archive', methods=['POST'])
def clear_archive():
    Task.query.filter_by(archived=True).delete()
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
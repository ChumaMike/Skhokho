from flask import Flask, render_template, request, redirect, session, url_for
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'secret123'  # needed for session

@app.before_request
def before_request():
    if 'history' not in session:
        session['history'] = []
    if 'diary' not in session:
        session['diary'] = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/balaa', methods=['GET', 'POST'])
def balaa():
    result = None

    if request.method == 'POST':
        try:
            fare = float(request.form['fare'])
            group_size = int(request.form['group_size'])
            amounts = request.form.getlist('amounts')
            amounts = [float(a) for a in amounts if a.strip()]
            total_expected = fare * group_size
            total_received = sum(amounts)
            change = total_received - total_expected

            result = {
                'fare': fare,
                'group_size': group_size,
                'amounts': amounts,
                'expected': total_expected,
                'received': total_received,
                'change': change,
                'time': datetime.now().strftime("%H:%M:%S")
            }

            history = session['history']
            history.append(result)
            session['history'] = history

        except Exception as e:
            result = {'error': str(e)}

    return render_template('balaa.html', result=result, history=session['history'])

def group_entries_by_date(entries):
    grouped = defaultdict(list)
    for entry in entries:
        date = entry['timestamp'][:10]  # YYYY-MM-DD
        grouped[date].append(entry)
    # Sort dates descending
    return dict(sorted(grouped.items(), reverse=True))

@app.route('/diary', methods=['GET', 'POST'])
def diary():
    if request.method == 'POST':
        entry_type = request.form.get('entry_type')
        content = request.form.get('content', '').strip()
        if not entry_type or not content:
            error = "Please select entry type and provide content."
            return render_template('diary.html', error=error, entries=group_entries_by_date(session['diary']))
        
        entry = {
            'type': entry_type,
            'content': content,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        diary = session['diary']
        diary.insert(0, entry)  # newest first
        session['diary'] = diary
        
        return redirect(url_for('diary'))
    
    grouped_entries = group_entries_by_date(session['diary'])
    return render_template('diary.html', entries=grouped_entries)

if __name__ == "__main__":
    app.run(debug=True)

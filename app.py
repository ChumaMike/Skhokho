from flask import Flask, render_template, request, redirect, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret123'  # needed for session

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/balaa', methods=['GET', 'POST'])
def balaa():
    if 'history' not in session:
        session['history'] = []

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

if __name__ == "__main__":
    app.run(debug=True)
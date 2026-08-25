from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "El servidor Backend con Flask está funcionando."

if __name__ == '__main__':
    app.run(debug=True)
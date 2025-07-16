from flask import Flask
import os

app = Flask('')

@app.route('/')
def home():
    return "Attention derriere toi"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


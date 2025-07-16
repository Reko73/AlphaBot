from threading import Thread
from flask import Flask
import threading
import os

app = Flask('')

@app.route('/')
def home():
    return "Bot en ligne"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
  t = Thread(target=run)
  t.start()

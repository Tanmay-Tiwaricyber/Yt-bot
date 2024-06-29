from flask import Flask
import subprocess

app = Flask(__name__)


@app.route('/')
def home():
    return "I am alive"


if __name__ == "__main__":
    # Define the command to run script.py
    command = ["python3", "script.py"
               ]  # Adjust 'python3' as needed for your Python interpreter

    try:
        # Start script.py in a separate process
        subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

        # Run the Flask application on host 0.0.0.0 (all available network interfaces) and port 80
        app.run(host="0.0.0.0", port=80)
    except Exception as e:
        print(f"Error starting script.py: {e}")

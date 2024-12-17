from flask import Flask, request, render_template, redirect, url_for, flash
import joblib
import os

# Load the trained models
model_left = joblib.load('model_decidera_left.pkl')
model_right = joblib.load('model_decidera_right.pkl')

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for flash messages

# Default file path for auto-loading
file_path = r"C:\test.txt"  # Change this path as per your setup

# Ideal frequencies for reference
ideal_values = [250, 500, 1000, 2000, 4000, 8000]

# Function to calculate percentage difference from ideal values
def calculate_percentage_diff(input_frequencies):
    diffs = [abs(input_frequencies[i] - ideal_values[i]) for i in range(len(ideal_values))]
    max_deviation = max(ideal_values)  # Max frequency value is 8000
    percentages = [(diff / max_deviation) * 100 for diff in diffs]
    avg_percentage = sum(percentages) / len(percentages)
    return round(avg_percentage, 2)

# Read file and process frequencies
def process_file(path):
    if os.path.exists(path):
        with open(path, 'r') as file:
            content = file.read().strip().split()
            if len(content) == 12:  # 6 values for left and 6 for right
                left_freqs = list(map(float, content[:6]))
                right_freqs = list(map(float, content[6:]))
                return left_freqs, right_freqs
            else:
                flash("Il file deve contenere esattamente 12 valori.", "error")
                return None, None
    else:
        flash(f"File non trovato nella posizione: {path}", "error")
        return None, None

# Home route
@app.route('/', methods=['GET', 'POST'])
def home():
    left_frequencies = [0] * 6  # Default values
    right_frequencies = [0] * 6
    prediction_results = {}
    percentage_diffs = {}

    # Auto-load values from file
    if request.method == 'GET':
        left_frequencies, right_frequencies = process_file(file_path)

    # Handle form submission
    if request.method == 'POST':
        try:
            # Retrieve input frequencies from the form
            left_frequencies = [float(request.form[f"left_{i}"]) for i in range(6)]
            right_frequencies = [float(request.form[f"right_{i}"]) for i in range(6)]

            # Calculate percentage differences
            percentage_diffs['left'] = calculate_percentage_diff(left_frequencies)
            percentage_diffs['right'] = calculate_percentage_diff(right_frequencies)

            # Make predictions
            prediction_results['left'] = "Normale" if model_left.predict([left_frequencies])[0] == 0 else "Problema"
            prediction_results['right'] = "Normale" if model_right.predict([right_frequencies])[0] == 0 else "Problema"

        except Exception as e:
            flash(f"Errore: {str(e)}", "error")
            return redirect(url_for('home'))

    return render_template('index.html', 
                           left_frequencies=left_frequencies, 
                           right_frequencies=right_frequencies,
                           predictions=prediction_results,
                           percentages=percentage_diffs,
                           file_path=file_path)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request
import pickle
import numpy as np
import os

app = Flask(__name__)

# Load model once when the app starts
model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
model = pickle.load(open(model_path, "rb"))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Extract features from form
        pregnancies = float(request.form.get('pregnancies', 0))
        glucose = float(request.form.get('glucose', 0))
        blood_pressure = float(request.form.get('blood_pressure', 0))
        skin_thickness = float(request.form.get('skin_thickness', 0))
        insulin = float(request.form.get('insulin', 0))
        bmi = float(request.form.get('bmi', 0))
        dpf = float(request.form.get('dpf', 0))
        age = float(request.form.get('age', 0))
        
        # Prepare input data
        input_data = np.array([[pregnancies, glucose, blood_pressure, skin_thickness,
                                insulin, bmi, dpf, age]])
        
        # Predict probability
        probability = model.predict_proba(input_data)[0][1]
        risk_score = round(probability * 100, 2)

        # 🔥 Reason Logic (FIXED INDENTATION)
        reasons = []

        if glucose > 140:
            reasons.append("High glucose level")

        if bmi > 30:
            reasons.append("High BMI")

        if age > 45:
            reasons.append("Age is above 45")

        if insulin > 150:
            reasons.append("High insulin level")

        if dpf > 0.8:
            reasons.append("High genetic risk (DPF)")

        if len(reasons) == 0:
            reasons.append("All values are within normal range")

        # Risk assessment
        threshold = 0.3
        if probability < threshold:
            risk_level = "LOW RISK"
        elif probability < threshold + 0.3:
            risk_level = "MODERATE RISK"
        else:
            risk_level = "HIGH RISK"
            
        return render_template(
            'index.html',
            prediction_text=f'Diabetes Risk Assessment: {risk_level}',
            probability_text=f'Calculated Probability: {risk_score}%',
            risk_level=risk_level,
            reasons=reasons,   # ✅ IMPORTANT
            pregnancies=pregnancies,
            glucose=glucose,
            blood_pressure=blood_pressure,
            skin_thickness=skin_thickness,
            insulin=insulin,
            bmi=bmi,
            dpf=dpf,
            age=age
        )

    except Exception as e:
        return render_template('index.html', error_text=f"Error occurred: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True, port=5000)

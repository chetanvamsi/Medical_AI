import streamlit as st
import numpy as np
import pickle
import shap
import matplotlib.pyplot as plt
st.set_page_config(
    page_title="Explainable Diabetes AI",
    page_icon="🧠",
    layout="wide"
)

st.markdown("""
<style>
body {
    background-color: #0f172a;
}
.stButton>button {
    background-color: #00C853;
    color: white;
    border-radius: 8px;
    height: 45px;
    width: 200px;
    font-size: 16px;
}
.stButton>button:hover {
    background-color: #00A844;
    color: white;
}
</style>
""", unsafe_allow_html=True)



# 📄 PDF Imports
from reportlab.platypus import Image, SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors as rl_colors
from reportlab.lib.units import inch
from io import BytesIO

# ===============================
# 🤖 Load Model
# ===============================
model = pickle.load(open("model.pkl", "rb"))
explainer = shap.Explainer(model)

# Dataset prevalence (PIMA Indians dataset)
DATASET_PREVALENCE = 34.9


# ===============================
# ⚙️ Sidebar
# ===============================
st.sidebar.title("⚙️ Model Control Panel")

threshold = st.sidebar.slider(
    "Risk Sensitivity Threshold",
    0.1, 0.9, 0.3
)

st.sidebar.markdown("""
### 📊 Model Info
- Model: Logistic Regression  
- Dataset: PIMA Indians Diabetes  
- Explainability: SHAP  
""")

# ===============================
# 🏥 Main UI
# ===============================
st.title("🏥 Diabetes Risk Predictor")
st.markdown("""
<div style="
background-color:#111827;
padding:15px;
border-radius:10px;
border-left:5px solid #00C853;
font-size:15px;
color:#E5E7EB;">
<b>About This System:</b><br>
This system combines machine learning predictions with rule-based clinical validation 
to enhance transparency and trust in medical decision support.
</div>
""", unsafe_allow_html=True)

st.write("Enter Patient Details:")

patient_name = st.text_input("Patient Name")

pregnancies = st.number_input("Pregnancies", min_value=0)
glucose = st.number_input("Glucose Level", min_value=0)
bp = st.number_input("Blood Pressure", min_value=0)
skin = st.number_input("Skin Thickness", min_value=0)
insulin = st.number_input("Insulin", min_value=0)
bmi = st.number_input("BMI", min_value=0.0)
dpf = st.number_input("Diabetes Pedigree Function", min_value=0.0)
age = st.number_input("Age", min_value=0)

# ===============================
# 📄 PDF Generator
# ===============================
def generate_pdf(patient_name, probability, level, fig,
                 feature_names, percentage_contributions,
                 glucose, bmi):



    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Diabetes Risk Assessment Report", styles["Heading1"]))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(
    "This system combines machine learning predictions with rule-based clinical validation "
    "to enhance transparency and trust in medical decision support.",
    styles["Normal"]
   ))
    elements.append(Spacer(1, 0.3 * inch))


    elements.append(Paragraph(f"<b>Patient Name:</b> {patient_name}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Risk Level:</b> {level}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Risk Probability:</b> {probability*100:.2f}%", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("<b>Risk Explanation:</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    # Build explanation logic
    if level == "HIGH RISK":
        explanation = "The patient is classified as HIGH RISK due to strong diabetic indicators."
    elif level == "MODERATE RISK":
        explanation = "The patient is classified as MODERATE RISK due to moderate metabolic risk indicators."
    else:
        explanation = "The patient is classified as LOW RISK as most metabolic indicators are within healthy range."

    # Add glucose reasoning
    if glucose >= 126:
        explanation += f" Elevated glucose level ({glucose} mg/dL) is a major contributing factor."
    elif glucose >= 100:
        explanation += f" Glucose is in prediabetic range ({glucose} mg/dL)."

    # Add BMI reasoning
    if bmi >= 30:
        explanation += f" BMI indicates obesity ({bmi}), increasing diabetes risk."
    elif bmi >= 25:
        explanation += f" BMI indicates overweight ({bmi})."

    elements.append(Paragraph(explanation, styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Spacer(1, 0.2 * inch))


    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Spacer(1, 0.3 * inch))

    elements.append(HRFlowable(width="100%", thickness=1, color=rl_colors.grey))
    elements.append(Spacer(1, 0.3 * inch))

        # Precautions
    elements.append(Paragraph("<b>Recommended Precautions:</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    if level == "LOW RISK":
        precautions = [
                "Maintain balanced diet",
                "Exercise regularly",
                "Avoid excessive sugar"
        ]
    elif level == "MODERATE RISK":
        precautions = [
                "Reduce sugar intake",
                "30 mins daily exercise",
                "Maintain healthy weight",
            "Monitor glucose regularly"
        ]
    else:
        precautions = [
            "Strictly reduce sugar",
            "Follow diabetic diet plan",
            "Regular glucose monitoring",
            "Consult doctor immediately",
            "Avoid processed foods"
        ]

    precaution_list = ListFlowable(
        [ListItem(Paragraph(item, styles["Normal"])) for item in precautions],
        bulletType='bullet'
    )

    elements.append(precaution_list)
    elements.append(Spacer(1, 0.4 * inch))
    
    elements.append(Paragraph("<b>Clinical Rule-Based Assessment:</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    clinical_notes = []

    # Glucose rules
    if glucose >= 126:
        clinical_notes.append(f"High fasting glucose detected ({glucose} mg/dL). Strong diabetes indicator.")
    elif glucose >= 100:
        clinical_notes.append(f"Prediabetic glucose range detected ({glucose} mg/dL).")
    else:
        clinical_notes.append(f"Glucose level within normal range ({glucose} mg/dL).")

    # BMI rules
    if bmi >= 30:
        clinical_notes.append(f"BMI indicates obesity ({bmi}). This significantly increases diabetes risk.")
    elif bmi >= 25:
        clinical_notes.append(f"BMI indicates overweight ({bmi}).")
    else:
        clinical_notes.append(f"BMI within healthy range ({bmi}).")

    elements.append(
        ListFlowable(
            [ListItem(Paragraph(note, styles["Normal"])) for note in clinical_notes],
            bulletType='bullet'
        )
    )

    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("<b>Feature Contribution Percentages:</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    feature_list = []

    for name, percent in zip(feature_names, percentage_contributions):
       feature_list.append(
           ListItem(
               Paragraph(f"{name}: {percent:.2f}%", styles["Normal"])
            )
        )

    elements.append(ListFlowable(feature_list, bulletType='bullet'))
    elements.append(Spacer(1, 0.3 * inch))


    # Add Graph
    elements.append(Paragraph("<b>Feature Contribution Graph:</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    img_buffer = BytesIO()
    fig.savefig(img_buffer, format="png", bbox_inches='tight')
    img_buffer.seek(0)

    elements.append(Image(img_buffer, width=400, height=300))

    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(
        "Disclaimer: This is an AI-generated risk estimation, not a medical diagnosis.",
        styles["Italic"]
    ))

    doc.build(elements)
    buffer.seek(0)

    return buffer


# ===============================
# 🔍 Prediction
# ===============================
if st.button("Predict"):

    input_data = np.array([[pregnancies, glucose, bp, skin,
                            insulin, bmi, dpf, age]])

    probability = model.predict_proba(input_data)[0][1]

    if patient_name:
        st.markdown(f"## 🧑 Patient: {patient_name}")

    st.subheader("📊 Risk Assessment")
    st.progress(float(probability))
    st.metric("Diabetes Risk Probability", f"{probability*100:.2f}%")

    # Risk Level
    if probability < threshold:
        level = "LOW RISK"
        banner_color = "#00C853"
    elif probability < threshold + 0.3:
        level = "MODERATE RISK"
        banner_color = "#FFD600"
    else:
        level = "HIGH RISK"
        banner_color = "#D50000"

    st.markdown(f"""
        <div style="
        padding:25px;
        border-radius:15px;
        background: linear-gradient(135deg, {banner_color}, #1f2937);
        color:white;
        font-size:26px;
        font-weight:bold;
        text-align:center;
        box-shadow:0px 4px 20px rgba(0,0,0,0.3);">
        {level} — {probability*100:.2f}%
        </div>
        """, unsafe_allow_html=True)


    # ===============================
    # 🔍 SHAP Graph
    # ===============================
    st.subheader("🔍 Feature Impact Explanation")

    feature_names = [
        "Pregnancies","Glucose","Blood Pressure",
        "Skin Thickness","Insulin","BMI",
        "Diabetes Pedigree","Age"
    ]

    shap_values = explainer(input_data)
    shap_values.feature_names = feature_names

    contributions = shap_values[0][:, 1].values
    abs_values = np.abs(contributions)
    total = np.sum(abs_values)

    percentage_contributions = (abs_values / total) * 100


    sorted_idx = np.argsort(np.abs(contributions))
    sorted_features = [feature_names[i] for i in sorted_idx]
    sorted_values = contributions[sorted_idx]

    bar_colors = ["#D50000" if val > 0 else "#2962FF" for val in sorted_values]

    fig, ax = plt.subplots(figsize=(8,5))
    ax.barh(sorted_features, sorted_values, color=bar_colors)
    ax.axvline(0, color='black')
    ax.set_xlabel("Impact on Diabetes Risk")
    ax.set_title("Feature Contribution to Prediction")

    st.pyplot(fig)

    # ===============================
    # 📄 PDF Download
    # ===============================
    pdf_file = generate_pdf(
    patient_name,
    probability,
    level,
    fig,
    feature_names,
    percentage_contributions,
    glucose,
    bmi
    )



    st.download_button(
        "📄 Download Risk Report",
        data=pdf_file,
        file_name="Diabetes_Risk_Report.pdf",
        mime="application/pdf"
    )

    

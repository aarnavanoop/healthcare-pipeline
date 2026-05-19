import requests
import time

BASE_URL = "http://localhost:8000"

print("1. Registering backfill admin...")
requests.post(f"{BASE_URL}/auth/register", json={"username": "admin", "password": "password123"})

print("2. Logging in...")
res = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin", "password": "password123"})
token = res.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

print("3. Fetching anomalous patients page by page...")

all_anomalies = []
page = 1
size = 100  # Staying safely at the API's maximum limit

while True:
    print(f"Fetching page {page}...")
    res = requests.get(f"{BASE_URL}/patients/anomalies?page={page}&size={size}", headers=headers)
    
    if res.status_code != 200:
        print(f"API Error on page {page}! Status: {res.status_code}, Response: {res.text}")
        break

    data = res.json()
    
    # Safely extract the list
    if isinstance(data, dict):
        current_page_data = data.get("items", data.get("data", []))
    else:
        current_page_data = data

    # If the page is empty, we've reached the end of the database!
    if not current_page_data:
        print("Reached the end of the patient list.")
        break
        
    all_anomalies.extend(current_page_data)
    page += 1

print(f"Successfully fetched {len(all_anomalies)} total anomalies. Triggering OpenAI worker...")

for summary in all_anomalies:
    # Safely extract the ID
    if isinstance(summary, str):
        patient_id = summary
    else:
        patient_id = summary.get("patient_id", summary.get("id"))

    if not patient_id:
        continue

    # Fetch full patient details to get their vitals
    detail_res = requests.get(f"{BASE_URL}/patients/{patient_id}", headers=headers)
    if detail_res.status_code != 200:
        print(f"Failed to fetch details for {patient_id}")
        continue
        
    patient = detail_res.json()
    vitals = patient.get("vitals", {})
    
    payload = {
        "age": patient.get("age", 50),
        "sex": patient.get("sex", 1),
        "resting_blood_pressure": vitals.get("resting_blood_pressure", 0),
        "max_heart_rate": vitals.get("max_heart_rate", 0),
        "serum_cholestrol": vitals.get("serum_cholestrol", 0),
        "st_depression_induced": vitals.get("st_depression_induced", 0),
        "fasting_blood_sugar": 0,
        "exercise_induced_angina": 1,
        "number_of_vessels": 1,
        "diagnosis_of_disease": 1,
        "chest_pain_2": 0, "chest_pain_3": 0, "chest_pain_4": 1,
        "resting_ecg_1": 0, "resting_ecg_2": 1,
        "thal_6": 0, "thal_7": 1,
        "slope_peak_2": 0, "slope_peak_3": 1,
        "is_anomaly": True
    }
    
    post_res = requests.post(f"{BASE_URL}/patients/", json=payload, headers=headers)
    if post_res.status_code == 201:
        print(f"Success: Generated AI notes for Patient ID: {patient_id}")
    else:
        print(f"Error for {patient_id}: {post_res.text}")
    
    # Pause for 2 seconds to avoid hitting OpenAI API rate limits
    time.sleep(2) 

print("Database backfill complete! You can now ask questions about any of these patients.")
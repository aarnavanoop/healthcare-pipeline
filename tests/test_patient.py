# tests/test_patient.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from app.main import app
from app.db.deps import get_db
from app.routes.auth import get_current_user
from app.db.models import User

# --- Auth Bypass Setup ---
def override_get_current_user():
    """Creates a fake user to bypass the JWT requirement during tests."""
    return User(username="test_mock_user", id=uuid4())

# --- Database Mock Setup ---
def make_mock_patient(overrides={}):
    """Creates a fake Patient ORM object for testing."""
    patient = MagicMock()
    patient.patient_id = uuid4()
    patient.age = 55.0
    patient.sex = 1
    patient.diagnosis_of_disease = 1
    patient.is_anomaly = False 
    patient.resting_blood_pressure = 2.5
    patient.serum_cholestrol = 0.3
    patient.fasting_blood_sugar = 0
    patient.max_heart_rate = 3.1      
    patient.exercise_induced_angina = 1
    patient.st_depression_induced = 2.2
    patient.number_of_vessels = 0.5
    patient.chest_pain_2 = 0
    patient.chest_pain_3 = 0
    patient.chest_pain_4 = 1
    patient.resting_ecg_1 = 0
    patient.resting_ecg_2 = 0
    patient.thal_6 = 0
    patient.thal_7 = 0
    patient.slope_peak_2 = 1
    patient.slope_peak_3 = 0

    for key, value in overrides.items():
        setattr(patient, key, value)
    
    return patient

def make_mock_db(return_patients=None, return_one=None):
    """
    Returns a mock AsyncSession.
    return_patients -> used for .scalars().all() (list endpoints)
    return_one      -> used for .scalar_one_or_none() (single record endpoints)
    """
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = return_patients or []
    mock_result.scalar_one_or_none.return_value = return_one
    mock_db.execute = AsyncMock(return_value=mock_result)
    return mock_db

client = TestClient(app)

# --- Dependency Overrides ---
def override_db(mock_db):
    """
    Overrides BOTH the database session AND the current user auth dependency 
    for a single test run to prevent state leakage.
    """
    async def _override():
        yield mock_db
    app.dependency_overrides[get_db] = _override
    app.dependency_overrides[get_current_user] = override_get_current_user

def clear_overrides():
    """Clears overrides so the next test starts clean."""
    app.dependency_overrides.clear()


# --- GET /patients/ ---
class TestGetPatients:

    def test_happy_path_returns_list(self):
        """Should return a list of patients."""
        mock_patients = [make_mock_patient(), make_mock_patient()]
        override_db(make_mock_db(return_patients=mock_patients))

        response = client.get("/patients/")
        
        assert response.status_code == 200
        assert len(response.json()) == 2
        clear_overrides()

    def test_anomaly_flag_filter(self):
        """anomaly_flag=true should only return anomalous patients."""
        mock_patients = [make_mock_patient({"is_anomaly": True})]
        override_db(make_mock_db(return_patients=mock_patients))

        response = client.get("/patients/?anomaly_flag=true")

        assert response.status_code == 200
        assert len(response.json()) == 1
        clear_overrides()

    def test_empty_results(self):
        """Should return empty list, not 404, when no records exist."""
        override_db(make_mock_db(return_patients=[]))

        response = client.get("/patients/")

        assert response.status_code == 200
        assert response.json() == []
        clear_overrides()

    def test_invalid_page_param(self):
        """page=0 should be rejected — ge=1 constraint."""
        override_db(make_mock_db())
        response = client.get("/patients/?page=0")
        assert response.status_code == 422
        clear_overrides()

    def test_size_exceeds_maximum(self):
        """size=200 should be rejected — le=100 constraint."""
        override_db(make_mock_db())
        response = client.get("/patients/?size=200")
        assert response.status_code == 422
        clear_overrides()


# --- GET /patients/anomalies ---
class TestGetAnomalousPatients:

    def test_happy_path_returns_severity(self):
        """Should return anomalous patients with severity_level field."""
        mock_patients = [make_mock_patient()]
        override_db(make_mock_db(return_patients=mock_patients))

        response = client.get("/patients/anomalies")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "severity_level" in data[0]
        assert data[0]["severity_level"] in ["LOW", "MEDIUM", "HIGH"]
        clear_overrides()

    def test_high_severity_patient(self):
        """A patient with extreme z-scores should be classified as HIGH."""
        high_risk = make_mock_patient({
            "diagnosis_of_disease": 1,
            "max_heart_rate": 3.5,       
            "st_depression_induced": 3.2, # 
        })
        override_db(make_mock_db(return_patients=[high_risk]))

        response = client.get("/patients/anomalies")

        assert response.json()[0]["severity_level"] == "HIGH"
        clear_overrides()

    def test_severity_filter(self):
        """severity=HIGH should only return HIGH severity patients."""
        high = make_mock_patient({
            "diagnosis_of_disease": 1,
            "max_heart_rate": 3.5,
            "st_depression_induced": 3.2,
        })
        low = make_mock_patient({
            "diagnosis_of_disease": 0,
            "max_heart_rate": 0.5,
            "st_depression_induced": 0.3,
        })
        override_db(make_mock_db(return_patients=[high, low]))

        response = client.get("/patients/anomalies?severity=HIGH")

        data = response.json()
        assert all(p["severity_level"] == "HIGH" for p in data)
        clear_overrides()

    def test_empty_anomalies(self):
        """Should return empty list when no anomalous patients exist."""
        override_db(make_mock_db(return_patients=[]))

        response = client.get("/patients/anomalies")

        assert response.status_code == 200
        assert response.json() == []
        clear_overrides()

    def test_invalid_severity_filter_returns_empty(self):
        """An unrecognised severity value should return empty list, not 500."""
        override_db(make_mock_db(return_patients=[make_mock_patient()]))

        response = client.get("/patients/anomalies?severity=CRITICAL")

        assert response.status_code == 200
        assert response.json() == []
        clear_overrides()


# --- GET /patients/{patient_id} ---
class TestGetPatientById:

    def test_happy_path(self):
        """Should return a patient with nested vitals."""
        patient = make_mock_patient()
        override_db(make_mock_db(return_one=patient))

        response = client.get(f"/patients/{patient.patient_id}")

        assert response.status_code == 200
        data = response.json()
        assert "vitals" in data
        assert data["patient_id"] == str(patient.patient_id)
        clear_overrides()

    def test_patient_not_found(self):
        """Should return 404 when patient ID doesn't exist."""
        override_db(make_mock_db(return_one=None))

        response = client.get(f"/patients/{uuid4()}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Patient not found"
        clear_overrides()

    def test_invalid_uuid_format(self):
        """A malformed UUID should return 422, not 500."""
        override_db(make_mock_db())
        response = client.get("/patients/not-a-real-uuid")
        assert response.status_code == 422
        clear_overrides()
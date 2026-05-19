import numpy as np



SCALER_PARAMS = {
    'Age': {
        'mean': 54.43894389438944,
        'std': 9.02373483119838,
        'log_transform': False,
    },
    'Resting Blood Pressure': {
        'mean': 4.879536174757237,
        'std': 0.12941697055349283,
        'log_transform': True,   # log1p was applied before scaling
    },
    'Serum Cholestrol in md/dl': {
        'mean': 5.491562488619815,
        'std': 0.20222368029018523,
        'log_transform': True,   # log1p was applied before scaling
    },
    'Max Heart Rate': {
        'mean': 149.6072607260726,
        'std': 22.83722455049312,
        'log_transform': False,
    },
    'ST Depression Induced': {
        'mean': 1.0396039603960396,
        'std': 1.1591574732421364,
        'log_transform': False,
    },
    'Number of Major Vessels': {
        'mean': 0.6633663366336634,
        'std': 0.9328323142577896,
        'log_transform': False,
    },
}


def denormalize_value(z_score: float, field: str) -> float:
    """
    Reverses the StandardScaler transform for a single value.
    For fields that had log1p applied first, also reverses that with expm1.
    """
    params = SCALER_PARAMS[field]
    value = z_score * params['std'] + params['mean']
    if params['log_transform']:
        value = np.expm1(value)
    return round(float(value), 1)


def denormalize_patient(patient) -> dict:
    """
    Returns a dict of human-readable vital values for display purposes.
    The original normalised values remain in the database for ML use.
    """
    return {
        'age': int(round(denormalize_value(patient.age, 'Age'))),
        'resting_blood_pressure': denormalize_value(patient.resting_blood_pressure, 'Resting Blood Pressure'),
        'serum_cholestrol': denormalize_value(patient.serum_cholestrol, 'Serum Cholestrol in md/dl'),
        'max_heart_rate': denormalize_value(patient.max_heart_rate, 'Max Heart Rate'),
        'st_depression_induced': denormalize_value(patient.st_depression_induced, 'ST Depression Induced'),
        'number_of_vessels': denormalize_value(patient.number_of_vessels, 'Number of Major Vessels'),
    }

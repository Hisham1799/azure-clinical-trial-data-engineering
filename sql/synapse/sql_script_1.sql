USE clinical_trial_serving;

CREATE EXTERNAL TABLE patient_study_summary (
    patient_id INT,
    patient_code VARCHAR(50),
    gender VARCHAR(10),
    race VARCHAR(50),
    ethnicity VARCHAR(50),
    date_of_birth DATETIME2,
    age_years BIGINT,
    enrollment_id INT,
    enrollment_date DATETIME2,
    enrollment_status VARCHAR(50),
    study_id INT,
    study_code VARCHAR(50),
    study_title VARCHAR(200),
    therapeutic_area VARCHAR(50),
    phase VARCHAR(20),
    arm_id INT,
    arm_name VARCHAR(100),
    site_id INT,
    site_name VARCHAR(200)
)
WITH (
    LOCATION = 'patient_study_summary/',
    DATA_SOURCE = gold_adls,
    FILE_FORMAT = DeltaSerializationFormat
);

CREATE EXTERNAL TABLE lab_summary (
    lab_result_id INT,
    visit_id INT,
    patient_id INT,
    patient_code VARCHAR(50),
    gender VARCHAR(10),
    age_years BIGINT,
    enrollment_id INT,
    study_id INT,
    site_id INT,
    lab_test_name VARCHAR(100),
    lab_test_code VARCHAR(50),
    lab_panel VARCHAR(100),
    result_value DECIMAL(12,2),
    result_unit VARCHAR(50),
    normal_range_low DECIMAL(12,2),
    normal_range_high DECIMAL(12,2),
    is_abnormal BIT,
    toxicity_grade INT,
    lab_status VARCHAR(20),
    toxicity_risk_category VARCHAR(20),
    collection_datetime DATETIME2,
    result_datetime DATETIME2
)
WITH (
    LOCATION = 'lab_summary/',
    DATA_SOURCE = gold_adls,
    FILE_FORMAT = DeltaSerializationFormat
);

CREATE EXTERNAL TABLE safety_adverse_events (
    ae_id INT,
    patient_id INT,
    visit_id INT,
    enrollment_id INT,
    reporter_investigator_id INT,
    patient_code VARCHAR(50),
    gender VARCHAR(10),
    age_years BIGINT,
    study_id INT,
    site_id INT,
    ae_term VARCHAR(200),
    meddra_pt_code VARCHAR(50),
    severity VARCHAR(50),
    ctcae_grade INT,
    onset_date DATETIME2,
    resolution_date DATETIME2,
    outcome VARCHAR(100),
    is_serious BIT,
    sae_category VARCHAR(100),
    causality VARCHAR(100),
    action_taken VARCHAR(100),
    is_expected BIT,
    ae_risk_category VARCHAR(50),
    ae_status VARCHAR(20),
    ae_duration_days INT,
    created_at DATETIME2,
    updated_at DATETIME2
)
WITH (
    LOCATION = 'safety_adverse_events/',
    DATA_SOURCE = gold_adls,
    FILE_FORMAT = DeltaSerializationFormat
);

CREATE EXTERNAL TABLE visit_summary (
    visit_id INT,
    enrollment_id INT,
    investigator_id INT,
    visit_number INT,
    visit_name VARCHAR(100),
    visit_type VARCHAR(50),
    patient_id INT,
    patient_code VARCHAR(50),
    study_id INT,
    site_id INT,
    scheduled_date DATETIME2,
    actual_visit_date DATETIME2,
    visit_window_start DATETIME2,
    visit_window_end DATETIME2,
    visit_status VARCHAR(50),
    visit_timing_status VARCHAR(20),
    days_from_scheduled INT,
    notes VARCHAR(500),
    created_at DATETIME2,
    updated_at DATETIME2
)
WITH (
    LOCATION = 'visit_summary/',
    DATA_SOURCE = gold_adls,
    FILE_FORMAT = DeltaSerializationFormat
);

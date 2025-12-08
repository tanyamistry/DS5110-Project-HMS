
-- 1) Number of appointments per doctor per week
SELECT doctor_name, strftime('%Y-%W', appointment_date) AS year_week, COUNT(*) AS appointment_count
FROM appointment
GROUP BY doctor_name, year_week
ORDER BY year_week DESC, appointment_count DESC;

-- 2) Doctor workload summary (appointments per day)
SELECT doctor_name, appointment_date, COUNT(*) AS appointments
FROM appointment
GROUP BY doctor_name, appointment_date
ORDER BY appointment_date DESC, appointments DESC;

-- 3) Most common visit reasons
SELECT COALESCE(reason, 'Unknown') AS reason, COUNT(*) AS count_reason
FROM appointment
GROUP BY reason
ORDER BY count_reason DESC;

-- 4) Patient visit frequency by month
SELECT p.mrn, p.full_name, strftime('%Y-%m', a.appointment_date) AS year_month, COUNT(*) AS visits
FROM appointment a
JOIN patient p ON p.id = a.patient_id
GROUP BY p.id, year_month
ORDER BY year_month DESC, visits DESC;

-- 5) Ratio of new to returning patients (per month)
WITH first_visit AS (
    SELECT patient_id, MIN(appointment_date) AS first_date
    FROM appointment
    GROUP BY patient_id
),
monthly_visits AS (
    SELECT
        a.patient_id,
        strftime('%Y-%m', a.appointment_date) AS year_month,
        MIN(a.appointment_date) AS first_in_month
    FROM appointment a
    GROUP BY a.patient_id, year_month
)
SELECT
    mv.year_month,
    SUM(CASE WHEN mv.first_in_month = fv.first_date THEN 1 ELSE 0 END) AS new_patients,
    SUM(CASE WHEN mv.first_in_month != fv.first_date THEN 1 ELSE 0 END) AS returning_patients
FROM monthly_visits mv
JOIN first_visit fv ON fv.patient_id = mv.patient_id
GROUP BY mv.year_month
ORDER BY mv.year_month DESC;

-- 6) Revenue trend analysis over time
SELECT
    strftime('%Y-%m', created_at) AS year_month,
    SUM(total_amount) AS revenue
FROM invoice
WHERE status != 'CANCELLED'
GROUP BY year_month
ORDER BY year_month DESC;

-- 7) Average billing amount per department (inferred from appointments)

SELECT
    COALESCE(a.department, 'Unknown') AS department,
    AVG(i.total_amount) AS avg_billing
FROM invoice i
JOIN appointment a ON a.patient_id = i.patient_id
WHERE i.status != 'CANCELLED'
GROUP BY department
ORDER BY avg_billing DESC;

-- 8) Cancellations and no-show stats
SELECT
    strftime('%Y-%m', appointment_date) AS month,
    status,
    COUNT(*) AS count_status
FROM appointment
GROUP BY month, status
ORDER BY month DESC, count_status DESC;

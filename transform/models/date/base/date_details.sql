WITH sequence_gen AS (
    SELECT '1970-01-01' :: DATE + SEQUENCE.DAY AS datum
    FROM GENERATE_SERIES(0, 29219) AS SEQUENCE (DAY)
    GROUP BY SEQUENCE.DAY
)

SELECT
  TO_CHAR(datum, 'yyyymmdd') :: INT                                   AS date_dim_id,
  datum                                                               AS date_actual,
  EXTRACT(EPOCH FROM datum)                                           AS epoch,
  TO_CHAR(datum, 'fmDDth')                                            AS day_suffix,
  TO_CHAR(datum, 'Day')                                               AS day_name,
  EXTRACT(DOW FROM datum) + 1                                         AS day_of_week,
  EXTRACT(ISODOW FROM datum)                                          AS day_of_week_iso,
  EXTRACT(DAY FROM datum)                                             AS day_of_month,
  datum - DATE_TRUNC('quarter', datum) :: DATE + 1                    AS day_of_quarter,
  EXTRACT(DOY FROM datum)                                             AS day_of_year,
  TO_CHAR(datum, 'W') :: INT                                          AS week_of_month,
  EXTRACT(WEEK FROM datum)                                            AS week_of_year,
  TO_CHAR(datum, 'YYYY"-W"IW-') || EXTRACT(ISODOW FROM datum)         AS week_of_year_iso,
  EXTRACT(MONTH FROM datum)                                           AS month_actual,
  TO_CHAR(datum, 'Month')                                             AS month_name,
  TO_CHAR(datum, 'Mon')                                               AS month_name_abbreviated,
  EXTRACT(QUARTER FROM datum)                                         AS quarter_actual,
  CASE
  WHEN EXTRACT(QUARTER FROM datum) = 1
    THEN 'First'
  WHEN EXTRACT(QUARTER FROM datum) = 2
    THEN 'Second'
  WHEN EXTRACT(QUARTER FROM datum) = 3
    THEN 'Third'
  WHEN EXTRACT(QUARTER FROM datum) = 4
    THEN 'Fourth'
  END                                                                 AS quarter_name,
  EXTRACT(YEAR FROM datum)                                            AS year_actual,
  EXTRACT(ISOYEAR FROM datum)                                         AS year_actual_iso,
  datum + (1 - EXTRACT(ISODOW FROM datum)) :: INT                     AS first_day_of_week,
  datum + (7 - EXTRACT(ISODOW FROM datum)) :: INT                     AS last_day_of_week,
  datum + (1 - EXTRACT(DAY FROM datum)) :: INT                        AS first_day_of_month,
  (DATE_TRUNC('MONTH', datum) + INTERVAL '1 MONTH - 1 day') :: DATE   AS last_day_of_month,
  DATE_TRUNC('quarter', datum) :: DATE                                AS first_day_of_quarter,
  (DATE_TRUNC('quarter', datum) + INTERVAL '3 MONTH - 1 day') :: DATE AS last_day_of_quarter,
  TO_DATE(EXTRACT(ISOYEAR FROM datum) || '-01-01', 'YYYY-MM-DD')      AS first_day_of_year,
  TO_DATE(EXTRACT(ISOYEAR FROM datum) || '-12-31', 'YYYY-MM-DD')      AS last_day_of_year,
  TO_CHAR(datum, 'mmyyyy')                                            AS mmyyyy,
  TO_CHAR(datum, 'mmddyyyy')                                          AS mmddyyyy,
  CASE
  WHEN EXTRACT(ISODOW FROM datum) IN (6, 7)
    THEN TRUE
  ELSE FALSE
  END                                                                 AS weekend_indr
FROM sequence_gen
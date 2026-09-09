select
  as_of_year, respondent_id, agency_code, loan_type, loan_purpose,
  loan_amount_000s, preapproval, action_taken,
  nullif(state_code, '') as state_code,
  nullif(county_code, '') as county_code,
  applicant_ethnicity, applicant_race_1, applicant_sex,
  applicant_income_000s, purchaser_type
from {{ source('raw', 'hmda_applications') }}

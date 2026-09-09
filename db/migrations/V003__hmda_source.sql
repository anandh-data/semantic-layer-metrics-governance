drop table if exists raw.hmda_applications cascade;
create table raw.hmda_applications (
  as_of_year smallint not null,
  respondent_id text not null,
  agency_code smallint,
  loan_type smallint,
  loan_purpose smallint,
  loan_amount_000s numeric,
  preapproval smallint,
  action_taken smallint not null,
  state_code text,
  county_code text,
  applicant_ethnicity smallint,
  applicant_race_1 smallint,
  applicant_sex smallint,
  applicant_income_000s numeric,
  purchaser_type smallint
);

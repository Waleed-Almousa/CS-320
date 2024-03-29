import json
from zipfile import ZipFile
import io
import csv

race_lookup = {
    "1": "American Indian or Alaska Native",
    "2": "Asian",
    "21": "Asian Indian",
    "22": "Chinese",
    "23": "Filipino",
    "24": "Japanese",
    "25": "Korean",
    "26": "Vietnamese",
    "27": "Other Asian",
    "3": "Black or African American",
    "4": "Native Hawaiian or Other Pacific Islander",
    "41": "Native Hawaiian",
    "42": "Guamanian or Chamorro",
    "43": "Samoan",
    "44": "Other Pacific Islander",
    "5": "White",
}

class Applicant:
    def __init__(self, age, race):
        self.age = age
        self.race = set()
        for r in race:
            if r in race_lookup:
                self.race.add(race_lookup[r])
            
    def __repr__(self):
        race_L=list()
        for r in self.race:
            race_L.append(r)
            race_L.sort()
        return f"Applicant('{self.age}', {race_L})"
    
    def lower_age(self):
        lower=self.age.replace(">", "")
        lower=lower.replace("<", "")
        lower=lower.split("-")
        return int(lower[0]) 
    
    def __lt__(self, other):
        return self.lower_age() < other.lower_age()
    
values = {'activity_year': '2020', 'lei': '549300FX7K8PTEQUU487', 'derived_msa-md': '31540', 'state_code': 'WI',
         'county_code': '55025', 'census_tract': '55025002402', 'conforming_loan_limit': 'C',
         'derived_loan_product_type': 'Conventional:First Lien',
         'derived_dwelling_category': 'Single Family (1-4 Units):Site-Built',
         'derived_ethnicity': 'Not Hispanic or Latino', 'derived_race': 'White', 'derived_sex': 'Male',
         'action_taken': '3', 'purchaser_type': '0', 'preapproval': '2', 'loan_type': '1', 'loan_purpose': '4',
         'lien_status': '1', 'reverse_mortgage': '2', 'open-end_line_of_credit': '1',
         'business_or_commercial_purpose': '2', 'loan_amount': '225000.0', 'loan_to_value_ratio': '78.671',
         'interest_rate': '3.000', 'rate_spread': 'NA', 'hoepa_status': '3', 'total_loan_costs': 'NA',
         'total_points_and_fees': 'NA', 'origination_charges': 'NA', 'discount_points': 'NA',
         'lender_credits': 'NA', 'loan_term': '360', 'prepayment_penalty_term': 'NA', 'intro_rate_period': '1',
         'negative_amortization': '2', 'interest_only_payment': '2', 'balloon_payment': '2',
         'other_nonamortizing_features': '2', 'property_value': '285000', 'construction_method': '1',
         'occupancy_type': '1', 'manufactured_home_secured_property_type': '3',
         'manufactured_home_land_property_interest': '5', 'total_units': '1', 'multifamily_affordable_units': 'NA',
         'income': '0', 'debt_to_income_ratio': '>60%', 'applicant_credit_score_type': '1',
         'co-applicant_credit_score_type': '10', 'applicant_ethnicity-1': '2', 'applicant_ethnicity-2': '',
         'applicant_ethnicity-3': '', 'applicant_ethnicity-4': '', 'applicant_ethnicity-5': '',
         'co-applicant_ethnicity-1': '5', 'co-applicant_ethnicity-2': '', 'co-applicant_ethnicity-3': '',
         'co-applicant_ethnicity-4': '', 'co-applicant_ethnicity-5': '', 'applicant_ethnicity_observed': '2',
         'co-applicant_ethnicity_observed': '4', 'applicant_race-1': '5', 'applicant_race-2': '',
         'applicant_race-3': '', 'applicant_race-4': '', 'applicant_race-5': '', 'co-applicant_race-1': '8',
         'co-applicant_race-2': '', 'co-applicant_race-3': '', 'co-applicant_race-4': '', 'co-applicant_race-5': '',
         'applicant_race_observed': '2', 'co-applicant_race_observed': '4', 'applicant_sex': '1',
         'co-applicant_sex': '5', 'applicant_sex_observed': '2', 'co-applicant_sex_observed': '4',
         'applicant_age': '55-64', 'co-applicant_age': '9999', 'applicant_age_above_62': 'Yes',
         'co-applicant_age_above_62': 'NA', 'submission_of_application': '1', 'initially_payable_to_institution': '1',
         'aus-1': '6', 'aus-2': '', 'aus-3': '', 'aus-4': '', 'aus-5': '', 'denial_reason-1': '1',
         'denial_reason-2': '', 'denial_reason-3': '', 'denial_reason-4': '', 'tract_population': '3572',
         'tract_minority_population_percent': '41.1499999999999986', 'ffiec_msa_md_median_family_income': '96600',
         'tract_to_msa_income_percentage': '64', 'tract_owner_occupied_units': '812',
         'tract_one_to_four_family_homes': '910', 'tract_median_age_of_housing_units': '45'}

class Loan:
    def __init__(self, values):
        try:
            self.loan_amount = float(values["loan_amount"])
        except ValueError:
            self.loan_amount= -1
        try:
            self.property_value=float(values["property_value"])
        except ValueError:
            self.property_value= -1
        try:
            self.interest_rate=float(values["interest_rate"])
        except ValueError:
            self.interest_rate= -1

        self.applicants= []
        races=[]
        for v in values:
            if v.startswith("applicant_race-") and values[v] !='':
                races.append(values[v])
                
        self.applicants.append(Applicant(values["applicant_age"], races))
        races2=[]
        if values["co-applicant_age"] != "9999":
            for v in values:
                if v.startswith("co-applicant_race-") and values[v] !='':
                    races2.append(values[v])
                
            self.applicants.append(Applicant(values["co-applicant_age"], races2))
            
            
    def __str__(self):
        return f"<Loan: {self.interest_rate}% on ${self.property_value} with {len(self.applicants)} applicant(s)>"

    def __repr__(self):
        return f"<Loan: {self.interest_rate}% on ${self.property_value} with {len(self.applicants)} applicant(s)>"
    
    
    def yearly_amounts(self, yearly_payment):
        assert self.interest_rate>0
        assert self.loan_amount>0
        amt = self.loan_amount
        while amt>0:
            try:
                yield amt
                amt= amt + (amt* (self.interest_rate*.01))
                amt = amt - yearly_payment
            except ValueError:
                pass
            

            
class Bank:
    def __init__(self, name):
        f = open("banks.json", encoding = "UTF-8")
        data = json.load(f)
        f.close()
        self.name=name
        
        for row in data:
            if self.name == row["name"]:
                assert self.name in row["name"]
                self.lei= row["lei"]
                break
        
        assert self.lei != None
        
        self.matches= []
        with ZipFile('wi.zip') as z:
            with z.open("wi.csv") as csvf:
                tio = io.TextIOWrapper(csvf)
                reader = csv.DictReader(tio)
                for row in reader:
                    if row["lei"]==self.lei:
                        self.matches.append(Loan(row))
        
    def __getitem__(self, index):
        return self.matches[index]
    
    def __len__(self):
        return len(self.matches)
                    
          
                
            
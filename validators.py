
import re
from datetime import datetime


def validate_phone_number(phone: str) -> tuple[bool, str]:
    if not phone or not phone.strip():
        return False, "Phone number is required."
    
    phone = phone.strip()
    
    clean_phone = re.sub(r'[\s\-\(\)\+]', '', phone)
    
    if not clean_phone.isdigit():
        return False, "Phone number must contain only digits and standard separators."
    

    if len(clean_phone) != 10:
        return False, "Phone number must be exactly 10 digits."
    
    return True, ""


def validate_date(date_str: str, field_name: str = "Date") -> tuple[bool, str]:
   
    if not date_str or not date_str.strip():
        return False, f"{field_name} is required."
    
    date_str = date_str.strip()
    
    # Check format with regex
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return False, f"{field_name} must be in YYYY-MM-DD format."
    
    # Try to parse the date
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return False, f"{field_name} is not a valid date."
    
    # Check if year is reasonable (1900-2100)
    if date_obj.year < 1900 or date_obj.year > 2100:
        return False, f"{field_name} year must be between 1900 and 2100."
    
    return True, ""


def validate_date_of_birth(dob_str: str) -> tuple[bool, str]:
   
    is_valid, error_msg = validate_date(dob_str, "Date of birth")
    if not is_valid:
        return False, error_msg
    
    try:
        dob = datetime.strptime(dob_str.strip(), '%Y-%m-%d')
        if dob > datetime.now():
            return False, "Date of birth cannot be in the future."
        
        # Check if person is not too old (>150 years)
        age_years = (datetime.now() - dob).days / 365.25
        if age_years > 150:
            return False, "Date of birth indicates age over 150 years."
            
    except ValueError:
        return False, "Invalid date of birth."
    
    return True, ""


def validate_appointment_date(date_str: str) -> tuple[bool, str]:
 
    is_valid, error_msg = validate_date(date_str, "Appointment date")
    if not is_valid:
        return False, error_msg
    
    return True, ""


def validate_time(time_str: str, field_name: str = "Time") -> tuple[bool, str]:
  
    if not time_str or not time_str.strip():
        return False, f"{field_name} is required."
    
    time_str = time_str.strip()
    
    # Check format with regex
    if not re.match(r'^\d{2}:\d{2}$', time_str):
        return False, f"{field_name} must be in HH:MM format (e.g., 09:30, 14:00)."
    
    # Try to parse the time
    try:
        time_obj = datetime.strptime(time_str, '%H:%M')
    except ValueError:
        return False, f"{field_name} is not a valid time."
    
    return True, ""


def validate_month(month_str: str) -> tuple[bool, str]:

    if not month_str or not month_str.strip():
        return False, "Month is required."
    
    month_str = month_str.strip()
    
    # Check if it's a number
    if not month_str.isdigit():
        return False, "Month must be a number between 1 and 12."
    
    month_num = int(month_str)
    
    if month_num < 1 or month_num > 12:
        return False, "Month must be between 1 and 12."
    
    return True, ""


def validate_year(year_str: str) -> tuple[bool, str]:
  
    if not year_str or not year_str.strip():
        return False, "Year is required."
    
    year_str = year_str.strip()
    
    # Check if it's a number
    if not year_str.isdigit():
        return False, "Year must be a number."
    
    year_num = int(year_str)
    
    if year_num < 1900 or year_num > 2100:
        return False, "Year must be between 1900 and 2100."
    
    return True, ""


def validate_email(email: str) -> tuple[bool, str]:
  
    if not email or not email.strip():
        # Email is optional in most cases
        return True, ""
    
    email = email.strip()
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Email format is invalid. Expected format: user@example.com"
    
    return True, ""


def validate_amount(amount_str: str, field_name: str = "Amount") -> tuple[bool, str]:
 
    if not amount_str or not amount_str.strip():
        return False, f"{field_name} is required."
    
    amount_str = amount_str.strip()
    
    # Try to convert to float
    try:
        amount = float(amount_str)
    except ValueError:
        return False, f"{field_name} must be a valid number."
    
    if amount < 0:
        return False, f"{field_name} cannot be negative."
    
    if amount > 1000000:
        return False, f"{field_name} seems unreasonably large (max 1,000,000)."
    
    return True, ""


def validate_mrn(mrn: str) -> tuple[bool, str]:
 
    if not mrn or not mrn.strip():
        return False, "MRN is required."
    
    mrn = mrn.strip()
    
    if len(mrn) < 3:
        return False, "MRN must be at least 3 characters."
    
    if not mrn.replace('-', '').replace('_', '').isalnum():
        return False, "MRN must be alphanumeric (can include - or _)."
    
    return True, ""


def validate_sex(sex: str) -> tuple[bool, str]:

    if not sex or not sex.strip():
        return False, "Sex is required."
    
    sex = sex.strip().upper()
    
    if sex not in ("M", "F", "O"):
        return False, "Sex must be M (Male), F (Female), or O (Other)."
    
    return True, ""


def validate_required_field(value: str, field_name: str) -> tuple[bool, str]:
   
    if not value or not value.strip():
        return False, f"{field_name} is required."
    
    return True, ""

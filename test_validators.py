
from validators import (
    validate_phone_number,
    validate_date,
    validate_date_of_birth,
    validate_appointment_date,
    validate_time,
    validate_month,
    validate_year,
    validate_email,
    validate_amount,
    validate_mrn,
    validate_sex,
    validate_required_field,
)


def test_phone_validation():
    test_cases = [
        "1234567890",          
        "(123) 456-7890",      
        "123-456-7890",         
        "+1-123-456-7890",      
        "12345",              
        "abc-def-ghij",        
        "",                   
    ]
    
    for phone in test_cases:
        is_valid, msg = validate_phone_number(phone)
        status = "✓ VALID" if is_valid else "✗ INVALID"
        print(f"{status}: '{phone}' - {msg if msg else 'OK'}")


def test_date_validation():
    print("\n=== DATE VALIDATION ===")
    test_cases = [
        "2025-12-08",         
        "1990-01-15",           
        "2025-13-01",           
        "2025-02-30",          
        "25-12-08",            
        "2025/12/08",          
        "",                     
    ]
    
    for date_str in test_cases:
        is_valid, msg = validate_date(date_str)
        status = "✓ VALID" if is_valid else "✗ INVALID"
        print(f"{status}: '{date_str}' - {msg if msg else 'OK'}")


def test_dob_validation():
    print("\n=== DATE OF BIRTH VALIDATION ===")
    test_cases = [
        "1990-05-15",          
        "2025-12-08",          
        "2026-01-01",          
        "1800-01-01",           
        "2010-06-20",          
    ]
    
    for dob in test_cases:
        is_valid, msg = validate_date_of_birth(dob)
        status = "✓ VALID" if is_valid else "✗ INVALID"
        print(f"{status}: '{dob}' - {msg if msg else 'OK'}")


def test_time_validation():
    print("\n=== TIME VALIDATION ===")
    test_cases = [
        "09:30",               
        "14:00",                
        "23:59",               
        "25:00",                
        "12:60",                
        "9:30",                 
        "09:30 AM",            
        "",                    
    ]
    
    for time_str in test_cases:
        is_valid, msg = validate_time(time_str)
        status = "✓ VALID" if is_valid else "✗ INVALID"
        print(f"{status}: '{time_str}' - {msg if msg else 'OK'}")


def test_month_validation():
    print("\n=== MONTH VALIDATION ===")
    test_cases = [
        "1",                   
        "12",                  
        "0",                   
        "13",                   
        "June",               
        "",                     
    ]
    
    for month in test_cases:
        is_valid, msg = validate_month(month)
        status = "✓ VALID" if is_valid else "✗ INVALID"
        print(f"{status}: '{month}' - {msg if msg else 'OK'}")


def test_email_validation():
    print("\n=== EMAIL VALIDATION ===")
    test_cases = [
        "user@example.com",     
        "john.doe@company.co.uk", 
        "test@test",          
        "invalid.email",     
        "@example.com",        
        "",                     
    ]
    
    for email in test_cases:
        is_valid, msg = validate_email(email)
        status = "✓ VALID" if is_valid else "✗ INVALID"
        print(f"{status}: '{email}' - {msg if msg else 'OK'}")


def test_amount_validation():
    print("\n=== AMOUNT VALIDATION ===")
    test_cases = [
        "100.50",               
        "0",                    
        "1000",                 
        "-50",                  
        "abc",                  
        "1000000.01",          
        "",                     
    ]
    
    for amount in test_cases:
        is_valid, msg = validate_amount(amount)
        status = "✓ VALID" if is_valid else "✗ INVALID"
        print(f"{status}: '{amount}' - {msg if msg else 'OK'}")


def test_mrn_validation():
    print("\n=== MRN VALIDATION ===")
    test_cases = [
        "MRN12345",            
        "12345",              
        "ABC-123",             
        "AB",                 
        "MRN@123",           
        "",                  
    ]
    
    for mrn in test_cases:
        is_valid, msg = validate_mrn(mrn)
        status = "✓ VALID" if is_valid else "✗ INVALID"
        print(f"{status}: '{mrn}' - {msg if msg else 'OK'}")


def test_sex_validation():
    print("\n=== SEX VALIDATION ===")
    test_cases = [
        "M",                  
        "F",                   
        "O",                    
        "m",                   
        "X",                   
        "Male",                
        "",                    
    ]
    
    for sex in test_cases:
        is_valid, msg = validate_sex(sex)
        status = "✓ VALID" if is_valid else "✗ INVALID"
        print(f"{status}: '{sex}' - {msg if msg else 'OK'}")


if __name__ == "__main__":
    print("=" * 60)
    print("HMS PROJECT - VALIDATION TESTING")
    print("=" * 60)
    
    test_phone_validation()
    test_date_validation()
    test_dob_validation()
    test_time_validation()
    test_month_validation()
    test_email_validation()
    test_amount_validation()
    test_mrn_validation()
    test_sex_validation()
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)

import re
from typing import Optional

# Regular expressions for validation
NAME_REGEX = re.compile(r"^[A-Za-zА-Яа-яЁёҒғҚқЎўҲҳЇїІіЄє'`'\-\\s]+$")
WORKING_DAYS_REGEX = re.compile(r"^[A-Za-zА-Яа-яЁёҒғҚқЎўҲҳЇїІіЄє\-\\s,]+$")
PHONE_DIGITS_REGEX = re.compile(r"\d+")
WORKING_HOURS_REGEX = re.compile(r"^\s*(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})\s*$")

def validate_name(name: str) -> bool:
    """
    Validate user name input.
    
    Args:
        name: Name string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not name or not name.strip():
        return False
    name = name.strip()
    if any(ch.isdigit() for ch in name):
        return False
    return bool(NAME_REGEX.match(name))

def normalize_phone(raw_phone: Optional[str]) -> Optional[str]:
    """
    Normalize phone number to +998XXXXXXXXX format.
    
    Args:
        raw_phone: Raw phone number input
        
    Returns:
        Optional[str]: Normalized phone number or None if invalid
    """
    if not raw_phone:
        return None
    raw = raw_phone.strip()
    plus = raw.startswith("+")
    digits = "".join(re.findall(r"\d", raw))
    if not digits:
        return None
    if len(digits) == 9 and digits[0] == "9":
        return "+998" + digits
    if len(digits) == 12 and digits.startswith("998"):
        return "+" + digits
    if plus and len(digits) == 12 and digits.startswith("998"):
        return "+" + digits
    return None

def validate_working_days(text: str) -> bool:
    """
    Validate working days input.
    
    Args:
        text: Working days string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not text or not text.strip():
        return False
    text = text.strip()
    if any(ch.isdigit() for ch in text):
        return False
    return bool(WORKING_DAYS_REGEX.match(text))

def validate_working_hours(text: str) -> bool:
    """
    Validate working hours input.
    
    Args:
        text: Working hours string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not text or not text.strip():
        return False
    clean = text.strip().lower().replace(" ", "")
    if clean == "24/7":
        return True
    m = WORKING_HOURS_REGEX.match(text)
    if not m:
        return False
    sh, sm, eh, em = m.group(1), m.group(2), m.group(3), m.group(4)
    try:
        sh_i = int(sh); sm_i = int(sm); eh_i = int(eh); em_i = int(em)
    except ValueError:
        return False
    if not (0 <= sh_i <= 23 and 0 <= eh_i <= 23 and 0 <= sm_i <= 59 and 0 <= em_i <= 59):
        return False
    start_minutes = sh_i * 60 + sm_i
    end_minutes = eh_i * 60 + em_i
    if start_minutes >= end_minutes:
        return False
    return True
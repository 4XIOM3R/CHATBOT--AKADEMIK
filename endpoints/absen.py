from endpoints.base import get_table_rows
from utils.parser_absen import parse_absen, extract_semester_from_page

def fetch_absen(driver) -> dict:
    rows = get_table_rows(driver, "/std/absen")
    
    # Extract semester info dari halaman SIA
    semester_info = extract_semester_from_page(driver)
    
    absen_data = parse_absen(rows, semester_info=semester_info)
    
    return {
        "data": absen_data,
        "semester_info": semester_info,
    }
from endpoints.base import get_table_rows
from utils.parser_absen import parse_absen

def fetch_absen(driver) -> list[dict]:
    rows = get_table_rows(driver, "/std/absen")
    return parse_absen(rows)
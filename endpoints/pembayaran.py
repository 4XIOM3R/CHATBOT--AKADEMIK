from endpoints.base import get_table_rows
from utils.parser_pembayaran import parse_pembayaran

def fetch_pembayaran(driver):
    rows = get_table_rows(driver, "/std/statuspembayaran")

    data, total = parse_pembayaran(rows)

    return {
        "data": data,
        "total_tagihan": total
    }
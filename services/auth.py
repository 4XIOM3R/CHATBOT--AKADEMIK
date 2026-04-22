from config import BASE_URL

def login(driver):
    driver.get(f"{BASE_URL}/login")
    input("👉 Login dulu, lalu tekan ENTER...")
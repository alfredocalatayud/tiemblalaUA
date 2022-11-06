from time import sleep

from requests_html import HTMLSession, AsyncHTMLSession
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import time
import pandas as pd

LOGIN = "https://autentica.cpd.ua.es/cas/login?service=https://deportesua.deporsite.net/cas/login"
BODYBUILDING = "https://deportesua.deporsite.net/reserva-pistas?IdDeporte=533"
USERNAME = "acs128@alu.ua.es"
PASSWORD = "Caramelos1998#"
DICTIONARY = dict(
    [("08:00", "2"), ("09:00", "3"), ("10:00", "4"), ("11:00", "5"), ("12:00", "6"), ("13:00", "7"), ("14:00", "8"),
     ("15:00", "9"), ("16:00", "10"), ("17:00", "11"), ("18:00", "12"), ("19:00", "13"), ("20:00", "14"),
     ("21:00", "15"), ("22:00", "16")])
PRIORITY = ["19:00", "18:00", "20:00", "21:00", "17:00"]


# 2to16 hours 8:00-22:00

def select_day(driver, day):
    WebDriverWait(driver, 5).until(
        expected_conditions.element_to_be_clickable((By.ID, "fecha"))).click()
    calendar = driver.find_element(By.CLASS_NAME, "datepicker-days")
    columns = calendar.find_elements(By.TAG_NAME, "td")

    for cell in columns:
        if cell.text == day:
            cell.click()
            break

    sleep(0.2)
    WebDriverWait(driver, 5).until(
        expected_conditions.element_to_be_clickable((By.ID, "fecha"))).click()
    WebDriverWait(driver, 5).until(
        expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, "td.active"))).click()


def login(driver, username, password):
    driver.get(LOGIN)
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.NAME, "submit").click()


def get_available_hours(driver, day):
    select_day(driver, day)

    WebDriverWait(driver, 5).until(
        expected_conditions.element_to_be_clickable((By.XPATH,
                                                     "/html/body/div[4]/div[3]/div/div/div/main/section[2]/div[3]/div[2]/div[1]/table")))
    tabla = driver.find_element(By.XPATH,
                                "/html/body/div[4]/div[3]/div/div/div/main/section[2]/div[3]/div[2]/div[1]/table")
    try:
        WebDriverWait(tabla, 2).until(
            expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, "td.celdaDisponible")))

        disponibles = tabla.find_elements(By.CSS_SELECTOR, "td.celdaDisponible")

        for disponible in disponibles:
            print(disponible.text)
    except:
        print("No hay dias disponibles.")


def main():
    options = webdriver.FirefoxOptions()
    options.add_argument('--start-maximiezed')
    options.add_argument('--disable-extensions')

    driver = webdriver.Firefox(options=options)

    # login(driver, USERNAME, PASSWORD)

    driver.get(BODYBUILDING)

    get_available_hours(driver, 10)

    # WebDriverWait(driver, 5).until(
    #   expected_conditions.element_to_be_clickable((By.XPATH,
    #                                               "/html/body/div[4]/div[3]/div/div/div/main/section[2]/div[3]/div[2]/div[1]/table/tbody/tr[11]/td[2]"))).click()

    # WebDriverWait(driver, 5).until(
    # expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, "div.btn-modal-horas"))).click()

    print("OK")


if __name__ == "__main__":
    main()

from time import sleep

from requests_html import HTMLSession, AsyncHTMLSession
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from threading import Thread
from datetime import datetime, timedelta
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


class Temp(Thread):
    def __init__(self, hora, delay, function):
        super(Temp, self).__init__()
        self._estado = True
        self.hora = hora
        self.delay = delay
        self.function = function

    def stop(self):
        self._estado = False

    def run(self):
        # String to type datetime
        aux = datetime.strptime(self.hora, '%H:%M:%S')

        # Get current datetime
        hora = datetime.now()

        # Replace the hour for the time we want the program to execute
        hora = hora.replace(hour=aux.hour, minute=aux.minute, second=aux.second, microsecond=0)

        # Check if it is time or not, if has passed we add one day (no execution today)
        if hora <= datetime.now():
            hora += timedelta(seconds=10)

        print('Ejecución automática iniciada.')
        print('Próxima ejecución el {} a las {}'.format(hora.date(), hora.time()))

        while self._estado:
            # Compare current hour with execution and execute or not function
            # If it has executed, one day added to objective date
            if hora <= datetime.now():
                self.function()
                print('Ejecución programada ejecutada el {} a las {}'.format(hora.date(), hora.time()))
                hora += timedelta(seconds=10)
                print('Próxima ejecución programada el {} a las {}'.format(hora.date(), hora.time()))

            # Wait x seconds to restart
            sleep(self.delay)
        else:
            print("Ejecución finalizada")


# 2to16 hours 8:00-22:00
def execute():
    print("Escogiendo hora")
    driver = init_driver()
    get_best_hour("11", driver)


def login(driver, username, password):
    driver.get(LOGIN)
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.NAME, "submit").click()


# Selects the day on the calendar
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


def get_available_hours(driver, day):
    driver.get(BODYBUILDING)
    select_day(driver, day)
    output = []

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
            output.append(disponible.text)
    except:
        print("No hay dias disponibles.")

    return output


def get_best_hour(day, driver=None):
    if not driver:
        driver = init_driver()

    #login(driver, USERNAME, PASSWORD)

    driver.get(BODYBUILDING)

    select_day(driver, day)

    for n in PRIORITY:
        xpath = "/html/body/div[4]/div[3]/div/div/div/main/section[2]/div[3]/div[2]/div[1]/table/tbody/tr[" + \
                DICTIONARY[n] + "]/td[2]"
        try:
            WebDriverWait(driver, 1).until(
                expected_conditions.element_to_be_clickable((By.XPATH, xpath))).click()
            WebDriverWait(driver, 5).until(
                expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, "div.btn-modal-horas"))).click()
            sleep(5)
            WebDriverWait(driver, 5).until(
                expected_conditions.element_to_be_clickable((By.CSS_SELECTOR,
                                                             "div.col-md-3:nth-child(4) > div:nth-child(2)"))).click()

            WebDriverWait(driver, 5).until(
                expected_conditions.element_to_be_clickable((By.CSS_SELECTOR,
                                                             ".alert")))

            print("¡A las {} hay sitio! ¡Reservado!".format(n))
            break
        except:
            print("A las {} no hay sitio.".format(n))
            sleep(3)


# driver.close()


def init_driver():
    options = webdriver.FirefoxOptions()

    options.add_argument('--start-maximiezed')
    options.add_argument('--disable-extensions')

    driver = webdriver.Firefox(options=options)

    return driver


def removeReservation(driver, res):
    login(driver, USERNAME, PASSWORD)

    WebDriverWait(driver, 3).until(
        expected_conditions.element_to_be_clickable((By.XPATH,
                                                     "/html/body/div[4]/div[1]/nav/div/div[2]/ul[2]/li[1]/a"))).click()

    WebDriverWait(driver, 3).until(
        expected_conditions.element_to_be_clickable((By.XPATH,
                                                     "/html/body/div[4]/div[1]/nav/div/div[2]/ul[2]/li[1]/ul/li[3]/a"))).click()

    WebDriverWait(driver, 3).until(
        expected_conditions.element_to_be_clickable((By.XPATH,
                                                     "/html/body/div[4]/div[3]/div/div/div/main/div/div[3]/section[2]/div[4]/div/table/tbody/tr[2]/td[7]/button"))).click()

    WebDriverWait(driver, 3).until(
        expected_conditions.element_to_be_clickable((By.CSS_SELECTOR,
                                                     "div.col-md-3:nth-child(2) > div:nth-child(2) > button:nth-child(1)"))).click()

    WebDriverWait(driver, 3).until(
        expected_conditions.element_to_be_clickable((By.ID,
                                                     "botonAnular"))).click()

    WebDriverWait(driver, 3).until(
        expected_conditions.element_to_be_clickable((By.CSS_SELECTOR,
                                                     "button.btn-primary:nth-child(1)"))).click()

    print("Reserva borrada.")


def getCurrentReservations(driver):
    reservations = []

    login(driver, USERNAME, PASSWORD)

    WebDriverWait(driver, 3).until(
        expected_conditions.element_to_be_clickable((By.XPATH,
                                                     "/html/body/div[4]/div[1]/nav/div/div[2]/ul[2]/li[1]/a"))).click()

    WebDriverWait(driver, 3).until(
        expected_conditions.element_to_be_clickable((By.XPATH,
                                                     "/html/body/div[4]/div[1]/nav/div/div[2]/ul[2]/li[1]/ul/li[3]/a"))).click()

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.element_to_be_clickable((By.XPATH,
                                                         "/html/body/div[4]/div[3]/div/div/div/main/div/div[3]/section[2]/div[4]/div/table/tbody/tr[2]/td[2]")))
        date1 = driver.find_element(By.XPATH,
                                    "/html/body/div[4]/div[3]/div/div/div/main/" + \
                                    "div/div[3]/section[2]/div[4]/div/table/tbody/tr[2]/td[2]")
        hour1 = driver.find_element(By.XPATH,
                                    "/html/body/div[4]/div[3]/div/div/div/main/" + \
                                    "div/div[3]/section[2]/div[4]/div/table/tbody/tr[2]/td[3]")
        t_date = date1.text
        t_hour = hour1.text
        date = datetime.strptime(t_date + " " + t_hour.split("-", 1)[0], "%d/%m/%Y %H:%M")

        reservations.append(date)

    except:
        print("No encuentro el dia.")
        day1 = False

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.element_to_be_clickable((By.XPATH,
                                                         "/html/body/div[4]/div[3]/div/div/div/main/div/div[3]/section[2]/div[4]/div/table/tbody/tr[3]/td[2]")))
        date2 = driver.find_element(By.XPATH,
                                    "/html/body/div[4]/div[3]/div/div/div/main/div/div[3]/section[2]/div[4]/div/table/tbody/tr[3]/td[2]")
        hour2 = driver.find_element(By.XPATH,
                                    "/html/body/div[4]/div[3]/div/div/div/main/div/div[3]/section[2]/div[4]/div/table/tbody/tr[3]/td[3]")
        t_date = date2.text
        t_hour = hour2.text
        date = datetime.strptime(t_date + " " + t_hour.split("-", 1)[0], "%d/%m/%Y %H:%M")

        reservations.append(date)

    except:
        print("No encuentro el dia.")
        day1 = False

    return reservations


def main():
    # t = Temp('18:25:00', 1, execute)
    # t.start()
    #
    # sleep(1800)
    # t.stop()
    # driver = init_driver()

    # reservations = getCurrentReservations(driver)

    # print("Tienes {} reservas activas: ".format(len(reservations)))
    # for r in reservations:
    #     print("     El día {} a las {}.".format(r.strftime("%d/%m"), r.strftime("%H:%M")))
    #
    # get_best_hour("11", driver)
    # date = datetime.now()
    # print(date.time())

    driver = init_driver()

    removeReservation(driver, 0)

    get_best_hour("11", driver)
    # availables = get_available_hours(driver, "11")
    #
    # for i in availables:
    #     if i in PRIORITY:
    #         get_best_hour("11", driver)
    #         break

    print("OK")


if __name__ == "__main__":
    main()

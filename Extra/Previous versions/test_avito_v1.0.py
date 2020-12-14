from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Если обобщенная категория - то без 2 пробелов ('Недвижимость')!!!
# Если конкретная подкатегория - то с 2 пробелами в начале ('  Квартиры')!!!
#####################################
catName = '  Коллекционирование'    # Название категории можно изменить тут, правописание важно!!!
cityName = 'Новосибирск'            # Название города можно изменить тут, правописание важно!!!
input_text = 'lego'                 # Название категории можно изменить тут
min_price = 10000                   # Значение мин. стоимости можно изменить тут
#####################################

# Задаем путь к хром драйверу
browser = webdriver.Chrome('/Users/nikolay/Documents/Selenium/chromedriver')

# Переходим на avito.ru
browser.get("http://avito.ru")

# Открываем поп-ап ввода города
select_city = browser.find_element(By.XPATH, '//div[@class="main-text-2PaZG"]')
select_city.click()

# Вводим название города
input_city = browser.find_element(By.XPATH, '//div/input[@class="suggest-input-3p8yi"]')
input_city.send_keys(cityName)
time.sleep(2)

# Подтверждаем выбор города
input_city_submit_button = browser.find_element(By.XPATH, '//div/button[@data-marker="popup-location/save-button"]')
input_city_submit_button.click()

# Выбираем нужную категорию
select_category = browser.find_element(By.NAME, 'category_id')
select_category_object = Select(select_category)
select_category_object.select_by_visible_text(catName)

# Вводим в поле поиска искомую фразу
search_field = browser.find_element(By.ID, 'search')
search_field.send_keys(input_text)

# Инициируем поисковый запрос
input_city_submit_button = browser.find_element(By.XPATH, '//div/button[@data-marker="search-form/submit-button"]')
input_city_submit_button.click()

# Фильтруем по мин. цене
min_price_field = browser.find_element(By.XPATH, '//label/input[@data-marker="price/from"]')
min_price_field.send_keys(min_price)
time.sleep(1)
add_filters_button = browser.find_element(By.XPATH, '//div/button[@data-marker="search-filters/submit-button"]') # Кнопка применения фильтров
add_filters_button.click()

wait = WebDriverWait(browser, 10)
original_window = browser.current_window_handle
assert len(browser.window_handles) == 1

# Создаем файл Result.csv для записи данных
f = open('/Users/nikolay/Documents/Selenium/Autotests/Result.csv', 'w')
f.write('Заголовок;')
f.write('Ссылка на товар;')
f.write('Стоимость;')
f.write('Имя продавца;')
f.write('Адрес;')
f.write('\n')

# Начинаем цикл по перебору результатов поиска
for i in range(2, 7): # Включая 2, но НЕ включая 7

    item_1 = browser.find_element(By.XPATH, f'//div[@data-marker="catalog-serp"]/div[{i}]//a').click()
    wait.until(EC.number_of_windows_to_be(2)) # Ждет открытия второй вкладки

    # Loop through until we find a new window handle
    for window_handle in browser.window_handles:
        if window_handle != original_window:
            browser.switch_to.window(window_handle)
            break
    print(f'**********Сcылка №{i-1}**********')
    # 1 - Заголовок - Print item title
    item_title = browser.find_element(By.XPATH, '//div[@class="title-info-main"]//span[@class="title-info-title-text"]')
    print(item_title.text + ';')
    f.write(item_title.text + ';')
    # 2 - Ссылка на товар - Print URL
    print(browser.current_url + ';')
    f.write(browser.current_url + ';')
    # 3 - Стоимость - Print price
    item_price = browser.find_element(By.XPATH, '//div[@class="item-price"]')
    print(item_price.text + ';')
    f.write(item_price.text + ';')
    # 4 - Имя продавца - Print seller's name
    item_seller_name= browser.find_element(By.XPATH, '//div[@data-marker="seller-info/name"]/a')
    print(item_seller_name.text + ';')
    f.write(item_seller_name.text + ';')
    # 5 - Адрес - Print seller's address
    item_seller_addr= browser.find_element(By.XPATH, '//div[@class="item-address"]//span')
    print(item_seller_addr.text + ';')
    f.write(item_seller_addr.text + ';')
    # Последний шаг - переход на новую строку
    print('Переход на новую строку')
    f.write('\n')
    print('**********Конец**********')
    browser.close()
    browser.switch_to.window(original_window)
# Закрываем файл Result.csv с данными
f.close()
# Закрываем браузер
browser.quit()
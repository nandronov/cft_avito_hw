from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time, math
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Если обобщенная категория - то без 2 пробелов ('Недвижимость')!!!
# Если конкретная подкатегория - то с 2 пробелами в начале ('  Квартиры')!!!
#####################################
catName = '  Коллекционирование'    # Название категории можно изменить тут, правописание важно!!!
cityName = 'Новосибирск'            # Название города можно изменить тут, правописание важно!!!
input_text = 'lego'                 # Название категории можно изменить тут
min_price = 3000                   # Значение мин. стоимости можно изменить тут
#####################################

# Задаем путь к хром драйверу
browser = webdriver.Chrome('/Users/nikolay/Documents/Selenium/chromedriver')

# Переходим на avito.ru
browser.get("http://avito.ru")

# Открываем поп-ап ввода города
select_city = browser.find_element(By.XPATH, '//div[@class="main-text-2PaZG"]')
select_city.click()
time.sleep(1)

# Вводим название города
input_city = browser.find_element(By.XPATH, '//div/input[@class="suggest-input-3p8yi"]')
input_city.send_keys(cityName)
time.sleep(2)

# Подтверждаем выбор города
input_city_submit_button = browser.find_element(By.XPATH, '//div/button[@data-marker="popup-location/save-button"]')
input_city_submit_button.click()
time.sleep(1)

# Выбираем нужную категорию
select_category = browser.find_element(By.NAME, 'category_id')
select_category_object = Select(select_category)
select_category_object.select_by_visible_text(catName)
time.sleep(1)

# Вводим в поле поиска искомую фразу
search_field = browser.find_element(By.ID, 'search')
search_field.send_keys(input_text)
time.sleep(1)

# Инициируем поисковый запрос
input_city_submit_button = browser.find_element(By.XPATH, '//div/button[@data-marker="search-form/submit-button"]')
input_city_submit_button.click()
time.sleep(2)

# Фильтруем по мин. цене
min_price_field = browser.find_element(By.XPATH, '//label/input[@data-marker="price/from"]')
min_price_field.send_keys(min_price)
time.sleep(1)
add_filters_button = browser.find_element(By.XPATH, '//div/button[@data-marker="search-filters/submit-button"]') # Кнопка применения фильтров
add_filters_button.click()
time.sleep(2)

# Исменяем вид на ячейки (а не список)
pic_view = browser.find_element(By.XPATH, '//div[@class="checkbox-group-item-bkY3s"]').click()

# Запоминаем иcходную вкладку
wait = WebDriverWait(browser, 10)
original_window_tab1 = browser.current_window_handle #
assert len(browser.window_handles) == 1

# Создаем файл Result.csv для записи данных
f = open('/Users/nikolay/Documents/Selenium/Autotests/Result.csv', 'w')
f.write('Заголовок;Ссылка на товар;Стоимость;Имя продавца;Адрес;Телефон \n')

# Проверка на многостраничность выданных результатов
pages = browser.find_element(By.XPATH, '//span[@data-marker="page-title/count"]')
y = int(pages.text)
x = math.ceil(y/30)
if y > 30:
    print('**********Результатов больше 30**********')
# Начинаем цикл по перебору 1-15 результатов поиска
    for j in range(1, x):
        print(f'Всего страниц: {x}')
        for i in range(1, 16): # Включая 1, но НЕ включая второе число
            try:
                item = browser.find_element(By.XPATH, f'//div[@data-marker="catalog-serp"]/div[@data-marker="item"][{i}]//a').click()
                wait.until(EC.number_of_windows_to_be(2)) # Ждет открытия второй вкладки

                # Цикл одидания и перехода на новую вкладку
                for window_handle in browser.window_handles:
                    if window_handle != original_window_tab1:
                        browser.switch_to.window(window_handle)
                        break
                print(f'**********Сcылка №{i}**********')
                # 1 - Заголовок
                item_title = browser.find_element(By.XPATH, '//div[@class="title-info-main"]//span[@class="title-info-title-text"]')
                print(item_title.text + ';')
                f.write(item_title.text + ';')
                # 2 - Ссылка на товар
                print(browser.current_url + ';')
                f.write(browser.current_url + ';')
                # 3 - Стоимость
                item_price = browser.find_element(By.XPATH, '//div[@class="item-price"]')
                print(item_price.text + ';')
                f.write(item_price.text + ';')
                # 4 - Имя продавца
                item_seller_name= browser.find_element(By.XPATH, '//div[@data-marker="seller-info/name"]/a')
                print(item_seller_name.text + ';')
                f.write(item_seller_name.text + ';')
                # 5 - Адрес
                item_seller_addr= browser.find_element(By.XPATH, '//div[@class="item-address"]//span')
                print(item_seller_addr.text + ';')
                f.write(item_seller_addr.text + ';')
                # Проверка есть ли у продавца номер телефона
                try:
                    WebDriverWait(browser, timeout=1).until(EC.text_to_be_present_in_element((By.XPATH, '//span[@class="messenger-button-onboardingButtonText-2_Xgw"]'), "Без звонков"))
                except TimeoutException:
                    ph_calls = 1 # Если происходит Timeout, то кнопка "Без звонков" не найдена, значит телефон есть, поэтому ph_calls = 1
                else:
                    ph_calls = 0 # В противном случае, если найдена, значит телефона нет, поэтому ph_calls = 0
                # В зависимости от результата выбираем как будем обрабатывать карточку товара
                if ph_calls == 0:
                    print('Нет телефона')
                    f.write('Нет телефона')
                    browser.close()
                elif ph_calls == 1:
                    # Открываем ссылку в мобильной версии
                    url = browser.current_url
                    mobile_emulation = { "deviceName": "Nexus 5" }
                    options = webdriver.ChromeOptions()
                    options.add_experimental_option("mobileEmulation", mobile_emulation)
                    browser2 = webdriver.Chrome(executable_path='/Users/nikolay/Documents/Selenium/chromedriver', options=options)
                    browser2.get(url)
                    # Проверка появляется ли на мобильной версии поп-ап логина
                    try:
                        WebDriverWait(browser, timeout=1).until(EC.presence_of_element_located((By.XPATH, '//*[@id="modal"]//div[@data-marker="login-button"]')))
                    except TimeoutException:
                        mob_login = 0 # Если происходит Timeout, то поп-ап логина не появляется, поэтому mob_login = 0
                    else:
                        mob_login = 1 # В противном случае, поп-ап появляется, поэтому mob_login = 1
                    # В зависимости от результата выбираем как будем обрабатывать поп-ап
                    if mob_login == 0:
                        pass
                    elif mob_login == 1:
                        browser.find_element(By.XPATH, '//*[@id="modal"]/div').click()
                    # 6 - Выводим и записываем номер продавца
                    item_ph_button = browser2.find_element(By.XPATH, '//*[@id="app"]//div[@class="css-1nyljbo"]').click()
                    time.sleep(1) # Ждем загрузку
                    item_ph_num = browser2.find_element(By.XPATH, '//*[@id="modal"]//span[@data-marker="phone-popup/phone-number"]')
                    print(item_ph_num.text)
                    f.write(item_ph_num.text + ';')
                    browser2.close()
                    browser.close()
                # Последний шаг - переход на новую строку в файле
                print('Переход на новую строку')
                f.write('\n')
                time.sleep(3) # Ждем ограничение на число запросов
                # Переходим на вкладку со списком поиска
                browser.switch_to.window(original_window_tab1)
                time.sleep(1)
            except NoSuchElementException:
                print("**********Конец списка 1-15 товаров**********")
                break

        time.sleep(5) # Без этой паузы авито выкидывает 404 на ˜20 позиции

        # Начинаем цикл по перебору 16-30 результатов поиска
        for i in range(16, 31): # Включая 1, но НЕ включая второе число

            try:
                item = browser.find_element(By.XPATH, f'//div[@data-marker="catalog-serp"]/div[@data-marker="item"][{i}]//a').click()
                wait.until(EC.number_of_windows_to_be(2)) # Ждет открытия второй вкладки

                # Цикл одидания и перехода на новую вкладку
                for window_handle in browser.window_handles:
                    if window_handle != original_window_tab1:
                        browser.switch_to.window(window_handle)
                        break
                print(f'**********Сcылка №{i}**********')
                # 1 - Заголовок
                item_title = browser.find_element(By.XPATH, '//div[@class="title-info-main"]//span[@class="title-info-title-text"]')
                print(item_title.text + ';')
                f.write(item_title.text + ';')
                # 2 - Ссылка на товар
                print(browser.current_url + ';')
                f.write(browser.current_url + ';')
                # 3 - Стоимость
                item_price = browser.find_element(By.XPATH, '//div[@class="item-price"]')
                print(item_price.text + ';')
                f.write(item_price.text + ';')
                # 4 - Имя продавца
                item_seller_name= browser.find_element(By.XPATH, '//div[@data-marker="seller-info/name"]/a')
                print(item_seller_name.text + ';')
                f.write(item_seller_name.text + ';')
                # 5 - Адрес
                item_seller_addr= browser.find_element(By.XPATH, '//div[@class="item-address"]//span')
                print(item_seller_addr.text + ';')
                f.write(item_seller_addr.text + ';')
                # Проверка есть ли у продавца номер телефона
                try:
                    WebDriverWait(browser, timeout=1).until(EC.text_to_be_present_in_element((By.XPATH, '//span[@class="messenger-button-onboardingButtonText-2_Xgw"]'), "Без звонков"))
                except TimeoutException:
                    ph_calls = 1 # Если происходит Timeout, то кнопка "Без звонков" не найдена, значит телефон есть, поэтому ph_calls = 1
                else:
                    ph_calls = 0 # В противном случае, если найдена, значит телефона нет, поэтому ph_calls = 0
                # В зависимости от результата выбираем как будем обрабатывать карточку товара
                if ph_calls == 0:
                    print('Нет телефона')
                    f.write('Нет телефона')
                    browser.close()
                elif ph_calls == 1:
                    # Открываем ссылку в мобильной версии
                    url = browser.current_url
                    mobile_emulation = { "deviceName": "Nexus 5" }
                    options = webdriver.ChromeOptions()
                    options.add_experimental_option("mobileEmulation", mobile_emulation)
                    browser2 = webdriver.Chrome(executable_path='/Users/nikolay/Documents/Selenium/chromedriver', options=options)
                    browser2.get(url)
                    # Проверка появляется ли на мобильной версии поп-ап логина
                    try:
                        WebDriverWait(browser, timeout=2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="modal"]//div[@data-marker="login-button"]')))
                    except TimeoutException:
                        mob_login = 0 # Если происходит Timeout, то поп-ап логина не появляется, поэтому mob_login = 0
                    else:
                        mob_login = 1 # В противном случае, поп-ап появляется, поэтому mob_login = 1
                    # В зависимости от результата выбираем как будем обрабатывать поп-ап
                    if mob_login == 0:
                        pass
                    elif mob_login == 1:
                        browser.find_element(By.XPATH, '//*[@id="modal"]/div').click()
                    # 6 - Выводим и записываем номер продавца
                    item_ph_button = browser2.find_element(By.XPATH, '//*[@id="app"]//div[@class="css-1nyljbo"]').click()
                    time.sleep(1) # Ждем загрузку
                    item_ph_num = browser2.find_element(By.XPATH, '//*[@id="modal"]//span[@data-marker="phone-popup/phone-number"]')
                    print(item_ph_num.text)
                    f.write(item_ph_num.text + ';')
                    browser2.close()
                    browser.close()
                # Последний шаг - переход на новую строку в файле
                print('Переход на новую строку')
                f.write('\n')
                time.sleep(3) # Ждем ограничение на число запросов
                # Переходим на вкладку со списком поиска
                browser.switch_to.window(original_window_tab1)
                time.sleep(1)
            except NoSuchElementException:
                print("**********Конец списка 16-30 товаров**********")
                break
        # Начинаем перебор страниц
        print(f'**********Страница №{j+1}**********')
        page = browser.find_element(By.XPATH, f'//div[@class="pagination-pages clearfix"]/a[@class="pagination-page"][{j+1}]')
        browser.execute_script("arguments[0].click();", page)
        time.sleep(5)
        print(f'**********Страница №{j+1} загружена**********')
else:
    print('**********Результатов меньше 30**********')
    # Начинаем цикл по перебору 1-15 результатов поиска
    for i in range(1, 16): # Включая 1, но НЕ включая второе число

        try:
            item = browser.find_element(By.XPATH, f'//div[@data-marker="catalog-serp"]/div[@data-marker="item"][{i}]//a').click()
            wait.until(EC.number_of_windows_to_be(2)) # Ждет открытия второй вкладки

            # Цикл одидания и перехода на новую вкладку
            for window_handle in browser.window_handles:
                if window_handle != original_window_tab1:
                    browser.switch_to.window(window_handle)
                    break
            print(f'**********Сcылка №{i}**********')
            # 1 - Заголовок
            item_title = browser.find_element(By.XPATH, '//div[@class="title-info-main"]//span[@class="title-info-title-text"]')
            print(item_title.text + ';')
            f.write(item_title.text + ';')
            # 2 - Ссылка на товар
            print(browser.current_url + ';')
            f.write(browser.current_url + ';')
            # 3 - Стоимость
            item_price = browser.find_element(By.XPATH, '//div[@class="item-price"]')
            print(item_price.text + ';')
            f.write(item_price.text + ';')
            # 4 - Имя продавца
            item_seller_name= browser.find_element(By.XPATH, '//div[@data-marker="seller-info/name"]/a')
            print(item_seller_name.text + ';')
            f.write(item_seller_name.text + ';')
            # 5 - Адрес
            item_seller_addr= browser.find_element(By.XPATH, '//div[@class="item-address"]//span')
            print(item_seller_addr.text + ';')
            f.write(item_seller_addr.text + ';')
            # Проверка есть ли у продавца номер телефона
            try:
                WebDriverWait(browser, timeout=1).until(EC.text_to_be_present_in_element((By.XPATH, '//span[@class="messenger-button-onboardingButtonText-2_Xgw"]'), "Без звонков"))
            except TimeoutException:
                ph_calls = 1 # Если происходит Timeout, то кнопка "Без звонков" не найдена, значит телефон есть, поэтому ph_calls = 1
            else:
                ph_calls = 0 # В противном случае, если найдена, значит телефона нет, поэтому ph_calls = 0
            # В зависимости от результата выбираем как будем обрабатывать карточку товара
            if ph_calls == 0:
                print('Нет телефона')
                f.write('Нет телефона')
                browser.close()
            elif ph_calls == 1:
                # Открываем ссылку в мобильной версии
                url = browser.current_url
                mobile_emulation = { "deviceName": "Nexus 5" }
                options = webdriver.ChromeOptions()
                options.add_experimental_option("mobileEmulation", mobile_emulation)
                browser2 = webdriver.Chrome(executable_path='/Users/nikolay/Documents/Selenium/chromedriver', options=options)
                browser2.get(url)
                # 6 - Выводим и записываем номер продавца
                item_ph_button = browser2.find_element(By.XPATH, '//*[@id="app"]//div[@class="css-1nyljbo"]').click()
                time.sleep(1) # Ждем загрузку
                # Возможно придется тут сделать обход запроса на логин
                item_ph_num = browser2.find_element(By.XPATH, '//*[@id="modal"]//span[@data-marker="phone-popup/phone-number"]')
                print(item_ph_num.text)
                f.write(item_ph_num.text + ';')
                browser2.close()
                browser.close()
            # Последний шаг - переход на новую строку в файле
            print('Переход на новую строку')
            f.write('\n')
            time.sleep(3) # Ждем ограничение на число запросов
            # Переходим на вкладку со списком поиска
            browser.switch_to.window(original_window_tab1)
            time.sleep(1)

        except NoSuchElementException:
            print("**********Конец списка 1-15 товаров**********")
            break

    time.sleep(5) # Без этой паузы авито выкидывает 404 на ˜20 позиции

        # Начинаем цикл по перебору 16-30 результатов поиска
    for i in range(16, 31): # Включая 1, но НЕ включая второе число

        try:
            item = browser.find_element(By.XPATH, f'//div[@data-marker="catalog-serp"]/div[@data-marker="item"][{i}]//a').click()
            wait.until(EC.number_of_windows_to_be(2)) # Ждет открытия второй вкладки

            # Цикл одидания и перехода на новую вкладку
            for window_handle in browser.window_handles:
                if window_handle != original_window_tab1:
                    browser.switch_to.window(window_handle)
                    break
            print(f'**********Сcылка №{i}**********')
            # 1 - Заголовок
            item_title = browser.find_element(By.XPATH, '//div[@class="title-info-main"]//span[@class="title-info-title-text"]')
            print(item_title.text + ';')
            f.write(item_title.text + ';')
            # 2 - Ссылка на товар
            print(browser.current_url + ';')
            f.write(browser.current_url + ';')
            # 3 - Стоимость
            item_price = browser.find_element(By.XPATH, '//div[@class="item-price"]')
            print(item_price.text + ';')
            f.write(item_price.text + ';')
            # 4 - Имя продавца
            item_seller_name= browser.find_element(By.XPATH, '//div[@data-marker="seller-info/name"]/a')
            print(item_seller_name.text + ';')
            f.write(item_seller_name.text + ';')
            # 5 - Адрес
            item_seller_addr= browser.find_element(By.XPATH, '//div[@class="item-address"]//span')
            print(item_seller_addr.text + ';')
            f.write(item_seller_addr.text + ';')
            # Проверка есть ли у продавца номер телефона
            try:
                WebDriverWait(browser, timeout=1).until(EC.text_to_be_present_in_element((By.XPATH, '//span[@class="messenger-button-onboardingButtonText-2_Xgw"]'), "Без звонков"))
            except TimeoutException:
                ph_calls = 1 # Если происходит Timeout, то кнопка "Без звонков" не найдена, значит телефон есть, поэтому ph_calls = 1
            else:
                ph_calls = 0 # В противном случае, если найдена, значит телефона нет, поэтому ph_calls = 0
            # В зависимости от результата выбираем как будем обрабатывать карточку товара
            if ph_calls == 0:
                print('Нет телефона')
                f.write('Нет телефона')
                browser.close()
            elif ph_calls == 1:
                # Открываем ссылку в мобильной версии
                url = browser.current_url
                mobile_emulation = { "deviceName": "Nexus 5" }
                options = webdriver.ChromeOptions()
                options.add_experimental_option("mobileEmulation", mobile_emulation)
                browser2 = webdriver.Chrome(executable_path='/Users/nikolay/Documents/Selenium/chromedriver', options=options)
                browser2.get(url)
                # 6 - Выводим и записываем номер продавца
                item_ph_button = browser2.find_element(By.XPATH, '//*[@id="app"]//div[@class="css-1nyljbo"]').click()
                time.sleep(1) # Ждем загрузку
                # Возможно придется тут сделать обход запроса на логин
                item_ph_num = browser2.find_element(By.XPATH, '//*[@id="modal"]//span[@data-marker="phone-popup/phone-number"]')
                print(item_ph_num.text)
                f.write(item_ph_num.text + ';')
                browser2.close()
                browser.close()
            # Последний шаг - переход на новую строку в файле
            print('Переход на новую строку')
            f.write('\n')
            time.sleep(3) # Ждем ограничение на число запросов
            # Переходим на вкладку со списком поиска
            browser.switch_to.window(original_window_tab1)
            time.sleep(1)

        except NoSuchElementException:
            print("**********Конец списка 16-30 товаров**********")
            break

print('**********Конец**********')
print('**********Результаты записаны в файл Result.csv **********')
# Закрываем файл Result.csv с данными
f.close()
# Закрываем браузер
browser.quit()




















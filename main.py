import csv
import pathlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import time


options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={UserAgent().chrome}")
# options.add_argument("--headless")


def get_product_info(product_url, file_name):
    browser = webdriver.Chrome(options=options)

    try:
        browser.get(url=product_url)
        response = browser.page_source
        bs_object = BeautifulSoup(response, "lxml")

        basic_info_class = 'ltr-13pqkh2 exjav150'
        basic_info = bs_object.find(name="div", attrs={'id': "tabpanel-0"}).find(name="div", class_=basic_info_class)
        title = basic_info.div.find(name="p", class_="ltr-4y8w0i-Body e1s5vycj0").text.strip()
        brand = basic_info.div.a.text.strip()
        made_in = basic_info.find(name="div", class_="ltr-jeopbd").text.strip()
        highlights = basic_info.find(name="div", class_='ltr-fzg9du e1yiqd0').ul.find_all(name="li")
        highlights = [highlight.text.strip() for highlight in highlights]
        highlights = "; ".join(highlights)
        description = basic_info.find(name="div", class_="ltr-4y8w0i-Body e1s5vycj0")
        if description is not None:
            description = description.text.strip()
        else:
            description = "Not information"

        additional_info = bs_object.find(name="div", class_="ltr-15eja7h exjav152").div
        if "Composition" in additional_info.text:
            composition = additional_info.div.find_all(name="p")
            composition = [element.text.strip() for element in composition]
            composition = "; ".join(composition)
        else:
            composition = "Not information"

        if "Washing instructions" in additional_info.text:
            washing_instruction = additional_info.find_all(name="div")[1].find_all(name="p")
            washing_instruction = [element.text.strip() for element in washing_instruction]
            washing_instruction = "; ".join(washing_instruction)
        else:
            washing_instruction = "Not information"

        if "Product IDs" in additional_info.text:
            product_ids = additional_info.find_all(name="div")[-1].find_all(name="p")
            farfetch_id = product_ids[0].span.text.strip()
            brand_style_id = product_ids[1].span.text.strip()
        else:
            farfetch_id = "Not information"
            brand_style_id = "Not information"

        full_price = bs_object.find(name="p", class_='ltr-194u1uv-Heading e54eo9p0')
        if full_price is not None:
            full_price = full_price.text.strip()
            purchase_price = full_price
        else:
            full_price = bs_object.find(name="p", class_="ltr-jp8o8r-Footnote e9urw9y0").text.strip()
            purchase_price = bs_object.find(name="p", class_="ltr-o8ptjq-Heading ex663c10").text.strip()

        images = bs_object.find_all(name="div", class_="ltr-bjn8wh ed0fyxo0")
        images = [image.img["src"] for image in images]
        images = "; ".join(images)

        categories = bs_object.find(name="ol", class_="ltr-fhxb3m e5zn8qx0").find_all(name="li")
        categories = [category.text.strip() for category in categories]
        categories = " -> ".join(categories)

        size_button_xpath = "/html/body/div[2]/main/div/div[1]/div[2]/div/div/div[3]/div[1]/div/div/div"
        size_button = browser.find_element(By.XPATH, size_button_xpath)
        size_button.click()
        time.sleep(1)
        response = browser.page_source
        bs_object = BeautifulSoup(response, "lxml")
        sizes = bs_object.find(name="div", class_="ltr-0 eqfcws00")
        size_values = sizes.find_all(name="span", class_="ltr-vcsfaw-Body-BodyBold eq12nrx0")
        size_values = [size_value.text.strip() for size_value in size_values]
        size_prices = sizes.find_all(name="div", class_="ltr-qq8qm9 e4w1h5m0")
        size_prices = [size_price.text.strip() for size_price in size_prices]
        sizes = list()
        for index in range(len(size_values)):
            if size_prices[index] != "":
                size = f"{size_values[index]} ({size_prices[index]})"
            else:
                size = f"{size_values[index]} ({purchase_price})"
            sizes.append(size)
        sizes = "; ".join(sizes)

        delivery_button = browser.find_element(By.XPATH, "/html/body/div[2]/main/div/div[3]/div/div[1]/button[3]")
        delivery_button.click()
        time.sleep(4)
        response = browser.page_source
        bs_object = BeautifulSoup(response, "lxml")
        estimated_delivery = bs_object.find(name="div", class_="ltr-15eja7h e2xvq5z1")
        estimated_delivery = estimated_delivery.find_all(name="p")
        estimated_delivery = [element.text.strip() for element in estimated_delivery]
        estimated_delivery = "; ".join(estimated_delivery[:-1])

        path = pathlib.Path("result", f"{file_name}.csv")
        with open(path, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([title, brand, full_price, purchase_price, sizes, product_url, images,
                             categories, description, made_in, highlights, composition, washing_instruction,
                             farfetch_id, brand_style_id, estimated_delivery])
    finally:
        browser.close()
        browser.quit()


def create_file_csv(file_name):
    path = pathlib.Path("result", f"{file_name}.csv")
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Название товара", "Бренд товара", "Цена", "Цена со скидкой", "Размеры", "Ссылка на товар",
                         "Ссылки на все фотографии", "Категории и подкатегории", "Описание", "Где сделано",
                         "Highlights", "Состав (Composition)", "Washing instructions",
                         "Farfetch id", "Brand style ID", "Estimated delivery"])


def main():
    product_url = input("Введите url товара: ")
    file_name = input("Введите название файла, в который необходимо записать результат: ")
    create_file_csv(file_name=file_name)
    get_product_info(product_url=product_url, file_name=file_name)


if __name__ == "__main__":
    main()

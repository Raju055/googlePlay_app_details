from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import os
import csv
from bs4 import BeautifulSoup as soup
import time




def driver_parser(root_dir, url):
    try:
        option = Options()
        # option.add_argument("--headless")

        driver = webdriver.Chrome(options=option, service_log_path="NUL",
                                  executable_path=root_dir + "/chromedriver.exe")
        driver.maximize_window()
        time.sleep(1)

        driver.get(url)
        time.sleep(3)

        old_position = 0
        new_position = None

        i = 0
        while i < 3:
            while new_position != old_position:
                # Get old scroll position
                old_position = driver.execute_script(
                    ("return (window.pageYOffset !== undefined) ?"
                     " window.pageYOffset : (document.documentElement ||"
                     " document.body.parentNode || document.body);"))
                # Sleep and Scroll
                time.sleep(5)
                driver.execute_script((
                    "var scrollingElement = (document.scrollingElement ||"
                    " document.body);scrollingElement.scrollTop ="
                    " scrollingElement.scrollHeight;"))
                # Get new position
                new_position = driver.execute_script(
                    ("return (window.pageYOffset !== undefined) ?"
                     " window.pageYOffset : (document.documentElement ||"
                     " document.body.parentNode || document.body);"))

                i = 0
            time.sleep(10)
            # Get new position
            new_position = driver.execute_script(
                ("return (window.pageYOffset !== undefined) ?"
                 " window.pageYOffset : (document.documentElement ||"
                 " document.body.parentNode || document.body);"))
            i += 1

        page_content = soup(driver.page_source, "html.parser")
        driver.quit()
        return page_content

    except:
        pass



def app_details(root_dir, apps_url_lst, file_name):
    try:
        columns = ["App Name", "Logo Source URL", "Rating", "Description", "No of Users Installed",
                   "Offered By", "In-app Products", "Updated At", "Size", "Interactive Elementes",
                   "Current Version", "Required Android", "Developer Email", "Website",
                   "Contact Address", "App URL"]

        f = open(root_dir + "/" + file_name + ".csv", "w", encoding='utf-8', newline='')
        csv_writer = csv.writer(f, delimiter=',')
        csv_writer.writerow(columns)
        f.close()

        for link in apps_url_lst:
            try:
                r = requests.get(link)
                page_soup = soup(r.content, "html.parser")

                app_name = page_soup.find("h1", {"itemprop":"name"}).text.strip()
                app_logo = page_soup.find("div", {"class":"xSyT2c"}).find("img")["src"]
                rating = page_soup.find("div", {"class":"BHMmbe"}).text.strip()
                description = page_soup.find("div", {"jsname":"sngebd"}).text.replace("\n", " "
                    ).replace("\t", " ").replace("\r", " ").replace("  ", " ").strip()

                while "  " in description:
                    description = description.replace("  ", " ").strip()

                installs = ''
                offered_by = ''
                in_app_products = ''
                updated_at = ''
                size = ''
                interactive_elements = ''
                developer_email = ''
                website = ''
                contact_address = ''
                current_version = ''
                required_android = ''

                app_info_lst = page_soup.find("div", {"class":"IxB2fe"}).findAll("div", {"class": "hAyfc"})
                for info in app_info_lst:
                    try:
                        info_txt = info.text.strip()
                        if 'updated' in info_txt.lower():
                            updated_at = info_txt.replace("Updated", " ").strip()
                        elif 'size' in info_txt.lower():
                            size = info_txt.replace("Size", " ").strip()
                        elif 'installs' in info_txt.lower():
                            installs = info_txt.replace("Installs", " ").strip()
                        elif 'version' in info_txt.lower():
                            current_version = info_txt.split("rsion")[-1].strip()
                        elif 'android' in info_txt.lower():
                            required_android = info_txt.split("Android")[-1].strip()
                        elif 'in-app products' in info_txt.lower():
                            in_app_products = info_txt.split("Products")[-1].strip()
                        elif 'interactive' in info_txt.lower():
                            interactive_elements = info_txt.split("elements")[-1].strip()
                        elif 'offered by' in info_txt.lower():
                            offered_by = info_txt.replace("Offered By", " ").strip()
                        elif 'developer' in info_txt.lower():
                            try:
                                contact_details = info.findAll("span")[-1].findAll("a")[0:2]
                                for contact in contact_details:
                                    try:
                                        dev_link = contact["href"]
                                        if "mailto" in dev_link:
                                            developer_email = contact.text.strip()
                                        else:
                                            website = dev_link
                                    except:
                                        pass
                                contact_address = info.findAll("span")[-1].findAll("div")[-1].text.replace(
                                                "\n", " ").replace("\t", " ").replace("\r", " ").replace(
                                                "   ", " ").replace("  ", " ").strip()
                            except:
                                pass

                    except:
                        pass

                csv_columns = [app_name, app_logo, rating, description, installs, offered_by,
                               in_app_products, updated_at, size, interactive_elements, current_version,
                               required_android, developer_email, website, contact_address, link]

                f = open(root_dir + "/" + file_name + ".csv", "a", encoding='utf-8', newline='')
                csv_writer = csv.writer(f, delimiter=',')
                csv_writer.writerow(csv_columns)
                f.close()

            except:
                pass
    except:
        pass



def books_details(root_dir, search_key, file_name):
    try:
        x = "https://play.google.com"

        main_url = "https://play.google.com/store/search?q="+search_key+"&c=apps"

        page_soup = driver_parser(root_dir, main_url)

        app_lst = page_soup.findAll("div", attrs={"class": "wXUyZd"})

        apps_url_lst = []
        for app_url in app_lst:
            try:
                apps_url_lst.append(x + str(app_url.find("a")["href"]))
            except:
                pass

        app_details(root_dir, apps_url_lst, file_name)

    except:
        pass



if __name__ == '__main__':
    root_dir = os.path.dirname(os.path.abspath(__file__))
    search_key = str(input("Enter the app name search for:  "))
    file_name = search_key.lower().strip().replace(" ", "_")

    search_key = search_key.lower().strip().replace(" ", "+")

    books_details(root_dir, search_key, file_name)

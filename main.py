import selenium 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager 
from time import sleep
import pandas as pd


# Credentials, url and driver
user = "test"
password = "test"
url = "https://www.montmere.com/test.php"
driver = webdriver.Chrome(ChromeDriverManager().install()) # Install the lastest chrome driver

def navigate():
    print(f'Navigating to {url}')
    driver.get(url)

def login():
    print('Login credentials')
    driver.find_element(By.ID, "username").send_keys(user)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.XPATH, "//input[@type='submit']").click()

def extract():
    print('Extracting the data')
    # Extract the elements that contains the data
    elements = driver.find_elements(By.XPATH, "//table[@id='the-table']/tr/td")
    data = {
        "Make": [],
        "Model": [],
        "Year": []
    }
    num_rows = int(len(elements) / 3)
    for i in range(num_rows):
        # Extract the text from web elements td, in groups of three
        make = elements[i * 3].text
        model = elements[i * 3 + 1].text
        year = elements[i * 3 + 2].text
        
        # Store the text in the dictionary
        data["Make"].append(make)
        data["Model"].append(model)
        data["Year"].append(year)


    return data


def wait_until(max_tries, xpath_value, timeout=5):
    wait = WebDriverWait(driver, timeout);
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath_value)))
        return True
            
    except TimeoutError:
        driver.refresh()
        tries += 1
        if (tries > max_tries):
            return False
        
    return False

def run():
    loginPageLoaded = False
    tablePageLoaded = False
    max_tries = 3
    tries = 0

    navigate()
    
    # Wait until the login page loads
    while (not loginPageLoaded) and (not tablePageLoaded) and (tries < max_tries):
        print('Wait until the login page or the home page loads...')
        try:
            # Verify if the login page appears
            loginPageLoaded = wait_until(max_tries=3, xpath_value="//input[@id='username']", timeout=5)
        except:
            loginPageLoaded = False
            # Verify if the table page appears because the user can be already cached
            tablePageLoaded = wait_until(max_tries=3, xpath_value="//table[@id='the-table']/tr/td", timeout=5)

        if(loginPageLoaded or tablePageLoaded):
            # Break the bucle if the login page or the table page appears
            break
        
        navigate()
        tries += 1

    # Enter credentials if we are in the login page
    sleep(3)
    if loginPageLoaded and not tablePageLoaded:
        login()
        # Wait until the home page loads
        while (not tablePageLoaded) and (tries < max_tries):
            print('Wait until the home page loads...')

            try:
                # Verify if the login page appears
                tablePageLoaded = wait_until(max_tries=3, xpath_value="//table[@id='the-table']/tr/td", timeout=5)
                break
            except:
                # Navigates again to the page
                navigate()
                tablePageLoaded = False
                
            if tablePageLoaded:
                # Break the bucle if the table page appears
                break

            tries += 1
        
        
    if tablePageLoaded:
        data = extract()
        print('Saving the data...')
        df = pd.DataFrame.from_dict(data)
        df.to_csv("output.csv", index=False, header=True)
        print('Data saved on output.csv...')



    if tries > max_tries:
        print("Try run again the script. Many tries failed to extract the data")
        

if __name__ == "__main__":
    print("Running the script...")
    run()
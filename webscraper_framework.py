from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import re
import ast
import pymongo

# Scrapes the news categories available on the website. Returns a list containing the landing webpage for
# each category.
def get_cat_links():

    # Enables the programming to access cookies. Significantly improves scraping performance.
    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=C:/Users/Shern/AppData/Local/Google/Chrome/User Data")
    # Initializes a webdriver for Google Chrome.
    driver = webdriver.Chrome(executable_path='C:/Users/Shern/Downloads/chromedriver_win32/chromedriver.exe'
                              , options=chrome_options)
    # Access the supplied URL.
    driver.get('https://www.freemalaysiatoday.com/')
    # Scrapes the object identified by the supplied XPATH.
    category_links = driver.find_elements_by_xpath('//*[@id="menu-header-menu-1"]/li[*]/ul/li[*]/a')
    cat_links = []
    for elem in category_links:
        cat_links.append(elem.get_attribute('href'))
    driver.quit()
    return cat_links

# Writes a Python list object to a file.
def list_to_file(filename_out,your_list):
    file = open(filename_out,'a+')
    file.writelines(["%s\n" % item for item in your_list])
    file.close()

# Reads a textfile and returns a Python list object.
def file_to_list(your_file):
    listname_out = []
    with open(your_file) as file_in:
        for line in file_in:
            line = line.rstrip('\n')
            listname_out.append(line)
    return listname_out

# Scrapes a list of links that fall between 1st Jan and 30th June.
def get_valid_links(links):
    # Enables the program to access cookies. Significantly improves performance.
    chrome_options = Options()
    chrome_options.add_argument("<path to Chrome user data directory>")
    # Initializes the driver.
    driver = webdriver.Chrome(executable_path='<path to Chrome driver executable>')

    for link in links:
        driver.get(link)
        cont = True
        while cont:
            # Scrolls down the infinite-scroll page.
            html = driver.find_element_by_tag_name('html')
            html.send_keys(Keys.END)
            print('looped')
            try:
                load_more = driver.find_element_by_xpath('//*[@id="td-outer-wrap"]/div[4]/div/div/div[1]/div/div[*]/a')
                # Clicks on the load-more button.
                driver.execute_script("arguments[0].click();", load_more)
                # driver.find_element_by_xpath('//*[@id="td-outer-wrap"]/div[4]/div/div/div[1]/div/div[*]/a').click()
            except (NoSuchElementException,ElementNotInteractableException):
                pass

            # Checks if date of article is valid.
            dates = driver.find_elements_by_xpath('//*[@id="td-outer-wrap"]/div[4]/div/div/div[1]/div/div[*]/div[*]/div/div[2]/span/time')
            date = dates[-1].get_attribute('textContent')
            if (re.search('April',date) == None)\
                    and (re.search('February',date) == None)\
                    and (re.search('January',date) == None)\
                    and (re.search('March',date) == None)\
                    and (re.search('December',date) == None)\
                    and (re.search('May',date) == None):
                print(date)
            else:
                print('reached date cutoff')
                links = driver.find_elements_by_xpath('//*[@id="td-outer-wrap"]/div[4]/div/div/div[1]/div/div[*]/div[*]/div/h3/a')
                for elem in links:
                    # Write URL to file if date is valid.
                    if ((re.search('2020/06/30', elem.get_attribute('href')) != None)) or \
                            ((re.search('2020/07/01', elem.get_attribute('href')) != None)):
                        print('Writing link to file:',elem.get_attribute('href'))
                        file = open('valid_links_finalday.txt', 'a+')
                        file.write(elem.get_attribute('href') + '\n')
                        file.close()
                    else:
                        cont = False
                        break


# Main web scraper. Extracts headline, content, author, government, language and timestamp.
def scrape(all_links, link_num,driver):

    # list of keywords to ensure each scraped article is topic-related.
    keywords = ['coronavirus', 'wuhan', 'virus', 'influenza', 'symptom', 'wuhan virus',
                'pneumonia', 'covid', 'covid-19', 'movement control order', 'mco', 'emco',
                'rmo', 'restricted movement order', 'restriction of movement order',
                'enhanced movement control order', 'ncov', 'n-cov', 'novelcoronavirus',
                '2019-nCoV', 'flu', 'social distancing', 'hand sanitizer', 'wash hands',
                'cmco','conditional movement control order','pandemic','koronavirus',
                'perintah kawalan pergerakan']
    newspaper = '<newspaper name>'
    headline_keyword_present = False
    while True:
        print(link_num)
        driver.get(all_links[link_num])

        # Scrape article headline.
        try:
            # Locate and scrape the headline.
            headline = driver.find_element_by_class_name('td-post-header')
            headline = headline.get_attribute('textContent')

            # Cleans unwanted symbols, whitespaces and linebreaks. De-capitalizes words.
            headline = headline.strip()
            headline = re.sub('\\n','',headline)
            headline = headline.lower()
            headline = re.sub('-(.*)','',headline)

            # Check if headline has a keyword.
            for keyword in keywords:
                if re.search(r'\b' + keyword + r'\b', headline):
                    print(str(link_num) + 'has keyword in headline.')
                    headline_keyword_present = True
                    break
        # In case of error (cannot find element or unicode error).
        except (NoSuchElementException,UnicodeEncodeError):
            try:
                # Re-runs the scraping process with a different locator.
                headline = driver.find_element_by_css_selector('div.td-post-header > header > h1')
                headline = headline.get_attribute('textContent')
                headline = headline.strip()
                headline = re.sub('\\n', '', headline)
                headline = headline.lower()
                headline = re.sub('-(.*)', '', headline)
                for keyword in keywords:
                    if re.search(r'\b' + keyword + r'\b', headline):
                        print(str(link_num) + 'has keyword in headline.')
                        headline_keyword_present = True
                        break
            # If error persists, write to a file.
            except(NoSuchElementException,UnicodeEncodeError):
                # Write to error log file.
                print('headline error')
                write_to_file('error_links_2.0.txt',all_links[link_num])
                link_num+=1
                continue

        # Scrapes article content.
        try:
            content = driver.find_element_by_class_name('td-post-content')
            content = content.get_attribute('textContent')
            content = content.lower()
            if headline_keyword_present:
                print('Headline already has keyword.')
                content = content.strip()
                content = content.replace("\r", "")
                content = content.replace("\n", "")
                content = content.replace(">", "")
                content = re.sub('[^a-zA-Z]+', ' ', content)

            else:
                for keyword in keywords:
                    if re.search(r'\b' + keyword + r'\b', content):
                        print(str(link_num) + ' has keyword in content.')
                        content = content.strip()
                        content = content.replace("\r", "")
                        content = content.replace("\n", "")
                        content = re.sub('[^a-zA-Z]+', ' ', content)
                        break
                else:
                    link_num += 1
                    continue
        except (NoSuchElementException, UnicodeEncodeError):
            # Write to error log file.
            print('Does not have keyword.')
            write_to_file('error_links_2.0.txt', all_links[link_num])
            link_num += 1
            continue

        # Scrapes article category.
        try:
            category = re.findall('category/(.*)/2020', all_links[link_num])[0]
            if category == 'bahasa':
                language = 'Bahasa Malaysia'
            else:
                language = 'English'
        except (NoSuchElementException,UnicodeEncodeError, IndexError):
            # Write to error log file.
            print('Category error.')
            write_to_file('error_links_2.0.txt', all_links[link_num])
            link_num += 1
            continue

        # Scrapes article timestamp.
        try:
            timestamp = re.findall('category/(.*)', all_links[link_num])[0]
            timestamp = timestamp.replace('opinion/','')
            timestamp = timestamp.replace('bahasa/','')
            timestamp = timestamp.replace('nation/','')
            timestamp = timestamp[:10]
        except (NoSuchElementException, UnicodeEncodeError):
            # Write to error log file.
            print('Timestamp error.')
            write_to_file('error_links_2.0.txt', all_links[link_num])
            link_num += 1
            continue

        print('Has keyword.')
        headline_keyword_present = False
        link = all_links[link_num]
        try:
            # Checking if article is from the government.
            origin = content.split()
            if origin[0] == 'kuala':
                source = origin[0] + ' ' + re.sub('[^a-zA-Z]+', '', origin[1])
            else:
                source = origin[0]
            if (source == 'putrajaya') or (origin[-1] == 'bernama'):
                FromGovernment = 1
            else:
                FromGovernment = 0

            # Writes scraped URLS to a text file in document format.
            doc = {"URL":all_links[link_num],"headline":headline,
                   "language":language,"category":category,
                   "timestamp":timestamp,"content":content,
                   "government":FromGovernment,"newspaper":newspaper}
            file = open('content_finalday.txt','a+')
            file.write(str(doc)+'\n')
            file.close()
        except UnicodeEncodeError:
            write_to_file('error_links_2.0.txt', all_links[link_num])

        link_num += 1
        headline_keyword_present = False

# Ends the session.
def kill_session(driver):
    driver.close()
    driver.quit()

# Write list to a file.
def write_to_file(file_in,content):
    file = open(file_in,'a+')
    file.write(content+'\n')
    file.close()

# Retrieve MongoDB account password.
def get_Mongo_pwd(file_in):
    file = open(file_in,'r')
    pwd = file.readline()
    return pwd

# Writes file contents to MongoDB Atlas (cloud).
def send_to_mongodb(content):
    pwd = get_Mongo_pwd('<file containing mongodb pwd>')
    client = pymongo.MongoClient('<connection string>')
    news = client['<db name>']
    articles = news['<collection name>']
    keywords = ['coronavirus', 'wuhan', 'virus', 'influenza', 'symptom', 'wuhan virus',
                'pneumonia', 'covid', 'covid-19', 'movement control order', 'mco', 'emco',
                'rmo', 'restricted movement order', 'restriction of movement order',
                'enhanced movement control order', 'ncov', 'n-cov', 'novelcoronavirus',
                '2019-nCoV', 'flu', 'social distancing', 'hand sanitizer', 'wash hands',
                'cmco', 'conditional movement control order', 'pandemic','koronavirus',
                'perintah kawalan pergerakan']

    send_DB = False
    bad_docs = []
    for doc in content:
        try:
            doc = ast.literal_eval(doc)
            for keyword in keywords:
                if re.search(keyword,doc['content']) != None:
                    send_DB = True
                    break
            if send_DB:
                articles.insert_one(doc)
                print('sent to mongo')
                send_DB = False
        except SyntaxError:
            bad_docs.append(doc)
    file = open('bad_links.txt','a+')
    file.writelines(["%s\n" % item for item in bad_docs])
    file.close()
import time
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup



#! make sure to replace [account_username] [bot_token] [chat_id]  
# instagram account usernmae that you want to monitor
account_username = 'ACCOUNT_USERNAME'
# your telegaram bot-token
bot_token = 'BOT-TOKEN'
# your account chat-id
chat_id = 'CHAT-ID'


monitoredUrl = f'https://www.instagram.com/{account_username}/'


#     method to extract data from the page source
def extract_data(source):
    try:
        if source:
            scraper = BeautifulSoup(source, 'html.parser')
            # finding number of posts, following and followers.
            ffp = scraper.findAll('span', class_='html-span xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 '
                                                 'xkhd6sd x1hl2dhg x16tdsg8 x1vvkbs')
            postN = ffp[0].text
            followersN = ffp[1].text
            followingN = ffp[2].text
            
            # finding bio
            bioE = scraper.find('h1', class_="_ap3a _aaco _aacu _aacx _aad6 _aade")
            bio = 'None'
            if bioE:
                bio = bioE.text.strip()
                
            #     finding Name of the account
            pName = scraper.find('span', class_="x1lliihq x1plvlek xryxfnj x1n2onr6 x193iq5w xeuugli x1fj9vlw x13faqbe "
                                                "x1vvkbs x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1i0vuye "
                                                "xvs91rp x1s688f x5n08af x10wh9bi x1wdrske x8viiok x18hxmgj")
            name = pName.text
            
            
            # find prfile url
            profileUrl = scraper.find('img', class_="_aadp")
            profilePicturUrl = profileUrl.get('src')
            
            
            # finding urls that on profile
            urlsE = scraper.find('div', class_="_ap3a _aaco _aacw _aacz _aada _aade")
            links = 'None'
            if urlsE:
                links = urlsE.text.strip()
            else:
                urlsE = scraper.find('span', class_="x1lliihq x193iq5w x6ikm8r x10wlt62 xlyipyv xuxw1ft")
                if urlsE:
                    links = urlsE.text.strip()


            # find if its private or public
            pdE = scraper.find('div',
                               class_="x6s0dn4 x5ur3kl x13fuv20 x178xt8z x1w9h7q7 x78zum5 x1pg5gke x1s688f xl56j7k "
                                      "x1r0g7yl x2b8uid xtvhhri")
            isPrivate = True
            if pdE:
                isPrivate = False

            finalResult = {
                'Name': name,
                'Bio': bio,
                'Posts': postN,
                'Followers': followersN,
                'Following': followingN,
                'Links': links,
                'isPrivate': isPrivate,
                'Profile': profilePicturUrl
            }
            print(finalResult)
            return finalResult
        else:
            print('page source was None')
            return None
    except:
        print('there was an error while scraping')
        send_constum_message('request have been blocked!')
        return None


# to get webpage source
def get_data():
    try:
        options = Options()
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Navigate to the Instagram page you want to scrape
        driver.get(monitoredUrl)

        # Wait until the page is fully loaded
        time.sleep(10)

        # getting the page source
        source = driver.page_source

        # close driver
        driver.quit()

        
        # Now, you can proceed with extracting data using Selenium as before
        return extract_data(source)
    except:
        print('there was an error while getting page source')
        send_constum_message('there was an error occur while getting page resource')
        return None


# to send the messages (every 4 hours) 
def send_message(message):
    finalMessage = preperMessage(message)
    response = requests.post(
        f'https://api.telegram.org/bot{bot_token}/sendMessage',
        json={'chat_id': chat_id, 'text': finalMessage}
    )
    print("Message response", response.status_code)

    return response

# to send the message 
def send_constum_message(message):
    response = requests.post(
        f'https://api.telegram.org/bot{bot_token}/sendMessage',
        json={'chat_id': chat_id, 'text': message}
    )
    print("Message response", response.status_code)
    return response

# use to prepare a message that send every 4 hours  
def preperMessage(result):
    if result:
        privaicy = '🔓'
        if result["isPrivate"] is True:
            privaicy = '🔒'
        message = f'        {result["Name"]}    \n\n\nProfile Picture url : \n{result["Profile"]} \n\n\nBio : \n{result["Bio"]}\n\nPosts : {result["Posts"]}\nFollowing : {result["Following"]}\nFollowers : {result["Followers"]}\nLinks : {result["Links"]}\nAccount Privacy : {privaicy}\n\n'
        return message
    else:
        message = "There was an error occur please check it!"
        return message

# checking if there is any change on the profile 
def checkChanges(new_data, old_data):
    
    if new_data is None: 
        print('there was an error occur!\nnew_data was None!')
        send_constum_message('there was an error occur \nnew_data was None!')
        return
    if old_data is None:
        print('there was an error occur!\nold_data was None!')
        send_constum_message('there was an error occur!\nold_data was None!')
    
    
    if new_data == old_data:
        return
    else:
        if new_data['Name'] != old_data['Name']:
            send_constum_message(f'Name have been changed form {old_data["Name"]} to {new_data["Name"]}')
        if new_data['Posts'] != old_data['Posts']:
            send_constum_message(f'Post count have been changed from {old_data["Posts"]} to {new_data["Posts"]}')
        if new_data['Bio'] != old_data['Bio']:
            send_constum_message(f'Bio have been changed from \n{old_data["Posts"]} \nto \n{new_data["Posts"]}')
        if new_data['Followers'] != old_data['Followers']:
            send_constum_message(
                f'Followers count have been changed from{old_data["Followers"]} to {new_data["Followers"]}')
        if new_data['Following'] != old_data['Following']:
            send_constum_message(
                f'Following count have been changed form {old_data["Following"]} to {new_data["Following"]}')
        if new_data['Links'] != old_data['Links']:
            send_constum_message(f'Links have been changed form {old_data["Links"]} to {new_data["Links"]}')
        if new_data['isPrivate'] != old_data['isPrivate']:
            if new_data['isPrivate'] is True:
                send_constum_message(f'Profile privacy have been changed, now its Private 🔒')
            else:
                send_constum_message(f'Profile privacy have been changed, now its Public 🔓')

        if new_data['Profile'] != old_data['Profile']:
            send_constum_message(
                f'Profile picture haven changed to \n{new_data["Profile"]}\n\nthe old one was \n{old_data["Profile"]} ')


def main():
    old_data = get_data()
    counter = 0
    
    while True:
        counter += 1
        print(counter)      
        new_data = get_data()
        checkChanges(new_data , old_data)
        # wait 1 hour for next checking
        print('sleep for 1 hour..')
        time.sleep(3600)


if __name__ == '__main__':
    main()


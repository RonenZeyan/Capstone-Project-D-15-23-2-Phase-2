import unittest
from selenium import webdriver
from run import app
from threading import Thread
from selenium.webdriver.common.by import By
import time

########################################################################################
'''                                                                                    #
 to start this testing you must write in the terminal                                  #
 "PIP INSTALL SELENIUM" and wait for install finished then and run this python file    #
 if not work you should write in the TERMINAL SET FLASK_APP=capstone.py                #
 to stop the testing you must kill the terminal because here we start flask by thread  #
 and because of that no direct way to stop the server                                  #
 (just kill the terminal after the tests finished and the server will stop )           #
                                                                                       #
'''                                                                                    #
########################################################################################

class TestUI(unittest.TestCase):

    '''
    this method called before each test method called 
    '''
    def setUp(self):
        self.driver = webdriver.Chrome() #in case you dont have chrome you must put firfox or what you have in your computer 
        self.flask_thread = Thread(target=lambda: app.run(use_reloader=False))
        self.flask_thread.start()

    '''
    after each testing. the browser of selenium closed 
    '''
    def tearDown(self):
        self.driver.close()
    
    '''
    this method make login (reuse it in testing methods )
    '''
    def login_user(self, email, password):
        """Helper function to perform login."""
        self.driver.get("http://localhost:5000/login")
        self.driver.find_element(By.ID, "emailInput").send_keys(email) #set value in input that have this id 
        self.driver.find_element(By.ID, "passwordInput").send_keys(password)
        self.driver.find_element(By.ID, "submit").click()
     
    '''
    this tester make failed register (exist email and exist username)
    result = display message that user failed to register because email and password exist
    '''
    def test_wrongUsernameEmail_register(self):
        self.driver.get("http://localhost:5000/register")
        self.driver.find_element(By.ID, "fnameID").send_keys("admin")
        self.driver.find_element(By.ID, "lnameID").send_keys("admin")
        self.driver.find_element(By.ID, "usernameID").send_keys("ronen") #username exist then get error msg
        self.driver.find_element(By.ID, "emailID").send_keys("ronen@gmail.com") #email exist then get error msg
        self.driver.find_element(By.ID, "passwordID").send_keys("admin1234")
        self.driver.find_element(By.ID, "cpasswordID").send_keys("admin1234")
        self.driver.find_element(By.ID, "submitID").click()      
        assert "Username already exist, Please choose another one!!!" in self.driver.page_source #this message we expect that it displayed
        assert "Email already exist, Please choose another one!!!" in self.driver.page_source #this message we expect that it displayed 

    '''
    this tester make success register (not exist email and not exist username)
    result = display message that user registered succesfully
    '''
    def test_success_register(self):
        self.driver.get("http://localhost:5000/register")
        self.driver.find_element(By.ID, "fnameID").send_keys("admin")
        self.driver.find_element(By.ID, "lnameID").send_keys("admin")
        self.driver.find_element(By.ID, "usernameID").send_keys("admin") #username not exist then get error msg
        self.driver.find_element(By.ID, "emailID").send_keys("admin@gmail.com") #email not exist then get error msg
        self.driver.find_element(By.ID, "passwordID").send_keys("admin")
        self.driver.find_element(By.ID, "passwordID").send_keys("admin")
        self.driver.find_element(By.ID, "cpasswordID").send_keys("admin")
        self.driver.find_element(By.ID, "submitID").click()      
 
    '''
    this tester make failed login (not exist email)
    result = display message that user loggedIN failed
    '''
    def test_failed_login(self):
        self.driver.get("http://localhost:5000/login")
        self.driver.find_element(By.ID, "emailInput").send_keys("notExist@gmail.com")
        self.driver.find_element(By.ID, "passwordInput").send_keys("notExist")
        self.driver.find_element(By.ID, "submit").click()
        assert "your email or password is wrong,please check again" in self.driver.page_source #this message we expect that it displayed 


    '''
    this tester make success login (exist email and correct password)
    result = display message that user loggedIN succesfully
    '''
    def test_success_login(self):
        self.driver.get("http://localhost:5000/login")
        self.driver.find_element(By.ID, "emailInput").send_keys("ronen@gmail.com")
        self.driver.find_element(By.ID, "passwordInput").send_keys("ronen")
        self.driver.find_element(By.ID, "submit").click()
        assert "You have been logged in successfully" in self.driver.page_source #this message we expect that it displayed 
        self.driver.find_element(By.ID,"accountID").click()
        self.driver.find_element(By.ID,"logoutID").click()

    '''
    this tester make success updateprofile for exist user 
    result = display message that profile has been updated successfully
    '''
    def test_updateProfile_success_user(self):
        self.login_user("ronen@gmail.com","ronen")
        self.driver.get("http://localhost:5000/updateProfile")
        self.driver.find_element(By.ID, "fnameID").clear()
        self.driver.find_element(By.ID, "fnameID").send_keys("israel") #change firstname from ronen to israel 
        self.driver.find_element(By.ID, "submitID").click()
        assert "Your Profile Has Been Updated Successfully" in self.driver.page_source
        self.driver.get("http://localhost:5000/updateProfile")
        assert "israel" in self.driver.page_source #check that the page of updateProfile include the word israel 
        self.driver.find_element(By.ID,"accountID").click()
        self.driver.find_element(By.ID,"logoutID").click() #logout by press in logout in navbar


    '''
    this tester make failed updateprofile for exist user (using exist username and exist email)
    result = dipslay error message that username and email exist and choose another one
    '''
    def test_updateProfile_failed_existUsername_user(self):
        self.login_user("ronen@gmail.com","ronen")
        self.driver.get("http://localhost:5000/updateProfile")
        self.driver.find_element(By.ID, "usernameID").clear() #clear the input of username before edit 
        self.driver.find_element(By.ID, "usernameID").send_keys("adham")
        self.driver.find_element(By.ID, "submitID").click()
        assert "Username already exist, Please choose another one!!!" in self.driver.page_source #this message we expect that it displayed 
        self.driver.find_element(By.ID,"accountID").click()
        self.driver.find_element(By.ID,"logoutID").click()

    '''
    this tester check if we go global home(mean the home of login and register) in case user not loggedIN
    result = display global home (home that displayed when user not login)
    '''
    def test_home_not_loggedIN(self):
        self.driver.get("http://localhost:5000")
        assert "login" in self.driver.page_source #login display in global home
        assert "register" in self.driver.page_source
        assert "http://localhost:5000" in self.driver.current_url #check that the url is this string

    '''
    this tester check if we go to user_home in case user loggedIN
    result = display user_home and not global Home
    '''
    def test_home_loggedIN(self):
        self.login_user("ronen@gmail.com","ronen") #make login
        assert "history" in self.driver.page_source
        assert "filter" in self.driver.page_source #user_home page include filter and history words 
        self.driver.find_element(By.ID,"accountID").click()
        self.driver.find_element(By.ID,"logoutID").click()

    '''
    this tester go to filtering page and enter data (url+enteredWords option then entered the word testingSelenium) and go filtering
    then check that the history updated with the new data
    result = history table in history page updated and new row (with the data entered) appear in the table in this row 
    '''
    def test_enteredDetails_history_filtering(self):
        self.login_user("ronen@gmail.com","ronen") #make login
        self.driver.find_element(By.ID, "filteringID").click()
        self.driver.find_element(By.ID, "urlID").send_keys("https://www.newsWebsiteURL.com")
        self.driver.find_element(By.ID,"filter_type-1").click()
        self.driver.find_element(By.ID, "enteredWord1").send_keys("testingSelenium")
        self.driver.find_element(By.ID, "submitID").click()
        self.driver.find_element(By.ID, "homeID").click()
        self.driver.find_element(By.ID, "historyID").click() #check that history table updated with the new filtering done by the user 
        assert "testingSelenium" in self.driver.page_source #this word we expect that it displayed in the row in table of history 
        self.driver.find_element(By.ID,"accountID").click()        
        self.driver.find_element(By.ID,"logoutID").click()

    '''
    this tester make filtering by enter url of not exist newswebsite (not exist url)
    result = display page that said the filtering not success 
    '''
    def test_filtering_with_not_exist_newWebsite(self):
        self.login_user("ronen@gmail.com","ronen") #make login
        self.driver.find_element(By.ID, "filteringID").click()
        self.driver.find_element(By.ID, "urlID").send_keys("https://www.notExistURL.com") #entered not exist website 
        self.driver.find_element(By.ID,"filter_type-1").click()
        self.driver.find_element(By.ID, "enteredWord1").send_keys("testingSelenium")
        self.driver.find_element(By.ID, "submitID").click()
        time.sleep(5)
        assert "filtering not success" in self.driver.page_source #expected that filtering not success display in the page 
        self.driver.find_element(By.ID,"accountID").click()
        self.driver.find_element(By.ID,"logoutID").click()


    ########### i will comment this test because it take some minutes to finish because ###########
    ############  the filtering time (you can test by remove the comment and wait :) )#######################

    '''
    this tester make filtering by enter url of exist newswebsite (exist url)
    result = display the newswebsite filtered (customized for user)
    '''
    # def test_filtering_with_exist_newWebsite(self):
    #     self.login_user("ronen@gmail.com","ronen") #make login
    #     self.driver.find_element(By.ID, "filteringID").click()
    #     self.driver.find_element(By.ID, "urlID").send_keys("https://www.jpost.com/") #entered exist news website 
    #     self.driver.find_element(By.ID,"filter_type-1").click()
    #     self.driver.find_element(By.ID, "enteredWord1").send_keys("testingSelenium")
    #     self.driver.find_element(By.ID, "submitID").click()
    #     time.sleep(5)
    #     assert "filtering not success" not in self.driver.page_source #expected that filtering please wait msg display in the page 
    #     self.driver.find_element(By.ID,"accountID").click()
    #     self.driver.find_element(By.ID,"logoutID").click()





        

if __name__ == "__main__":
    unittest.main()
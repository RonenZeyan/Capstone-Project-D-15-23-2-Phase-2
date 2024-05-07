import unittest
from flask import url_for,redirect
from flask_testing import TestCase
from assr import app,db
from flask_sqlalchemy import SQLAlchemy
from assr.models import User,FilteringHistory,wordsHistory,optionHistory
from flask_login import login_user,logout_user,current_user

'''
to run this tests you must comment the database in row 13 in path  assr/__init__.py 
and remove the comment from row 14.
comment this : app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///websiteFilteringDB'
un comment this : # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbfortesting'
and run this file 
'''

class TestBase(TestCase):

    def create_app(self):
        # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/dbfortesting' 
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbfortesting' 

        app.config['TESTING'] = True  #this configuration help us to set that the app in testing mode
        return app

    '''
    this method called everytime test starting
    in this method,we create user,and create tables and add user to db 
    '''
    def setUp(self):
        db.create_all()
        self.user = User(username="ronen", firstName="ronen", lastName="zeyan", email="ronen@gmail.com", password="ronen")
        db.session.add(self.user)  #add user to db
        db.session.commit()  # commit the add of the user to db 
    '''
    this method called everytime test ended
    in this method, userlogout in case he loggedIN, remove all tables in db,and remove db
    '''
    def tearDown(self):
        logout_user()
        db.session.remove()
        db.drop_all()


class test_db_and_models(TestBase):
    """
    test entered new user to User Model in DB (User table) and check if it contain 1 user after we add him
    """
    def test_create_user_and_UserModel(self):
        expected = User(username="admin", firstName="ronen", lastName="zeyan", email="admin@gmail.com", password="ronen")
        user = User(username="admin", firstName="ronen", lastName="zeyan", email="admin@gmail.com", password="ronen")
        db.session.add(user)  #add user to db
        db.session.commit()  # commit the add of the user to db 
        self.assertEqual(User.query.count(), 2)  # check that the user really saved in db (db is empty before save the user )
        retrieved_user = User.query.get(user.id)
        self.assertIsNotNone(retrieved_user, "User should be found in the database.")
        self.assertEqual(retrieved_user.username, expected.username, "Username should be the same")
        self.assertEqual(retrieved_user.firstName, expected.firstName, "First name should be the same")
        self.assertEqual(retrieved_user.lastName, expected.lastName, "Last name should be the same")
        self.assertEqual(retrieved_user.email, expected.email, "Email should be the same")

    '''
    test to check that filtering details saved in db and that they saved correctly 
    '''
    def test_filtering_history_and_FilteringHistoryModel(self):
        history = FilteringHistory(user_id=self.user.id,websiteURL="https://www.jpost.com",data_type="option")
        db.session.add(history)
        db.session.commit()
        saved_history = FilteringHistory.query.first()
        self.assertEqual(FilteringHistory.query.count(), 1)  # check that the user really saved in db (db is empty before save the user )
        #check the getten history 
        self.assertIsNotNone(saved_history,"history should be found in the database") #check that history add to db
        self.assertEqual(saved_history.user_id,self.user.id) #check that user with id that enter the history his id saved in db 
        self.assertEqual(saved_history.websiteURL,"https://www.jpost.com")
        self.assertEqual(saved_history.data_type,"option")

    '''
    test that check that db saved the correct option data for history 
    '''
    def test_option_and_OptionModel(self):
        #adding user and history (crucial for optionHistory)
        history = FilteringHistory(user_id=self.user.id,websiteURL="https://www.jpost.com",data_type="option")
        db.session.add(history)
        db.session.commit()

        option = optionHistory(history_id=history.id, politics=True, criminal=False, sexual=True)
        db.session.add(option)
        db.session.commit()
        #here we make the testing for model and add new optionHistory to db
        self.assertEqual(optionHistory.query.count(),1)  #check optionHistory model
        saved_option = optionHistory.query.first()
        self.assertIsNotNone(saved_option) 
        self.assertTrue(saved_option.politics)
        self.assertFalse(saved_option.criminal)
        self.assertTrue(saved_option.sexual)

    '''
    test that check that db saved the correct enteredwords data for history 
    '''
    def test_enteredWords_and_entereWordsModel(self):
        #adding user and history (crucial for optionHistory)
        history = FilteringHistory(user_id=self.user.id,websiteURL="https://www.jpost.com",data_type="option")
        db.session.add(history)
        db.session.commit()

        words = wordsHistory(history_id=history.id, enterWord_1="test1", enterWord_2="test2", enterWord_3="test3")
        db.session.add(words)
        db.session.commit()
        #here we make the testing for model and add new optionHistory to db
        self.assertEqual(wordsHistory.query.count(),1)  #check optionHistory model
        saved_words = wordsHistory.query.first()
        self.assertIsNotNone(saved_words)
        self.assertEqual(saved_words.enterWord_1, "test1")
        self.assertEqual(saved_words.enterWord_2, "test2")
        self.assertEqual(saved_words.enterWord_3, "test3")


    

class test_Views(TestBase):

    '''
    test that check if user loggedIN, the loggedIN status updated 
    '''
    def test_login_user(self):
        with self.client:
            #make loggedIn for user 
            login_user(self.user)
            # check that user really loggedIN
            self.assertTrue(current_user.is_authenticated)
            self.assertEqual(current_user.username, 'ronen')

    '''
    test that in case user loggedIN and try to go to route login then he navigated to home
    '''        
    def test_login_view(self):
        with self.client:
            login_user(self.user)
            target_url = url_for('login')
            response = self.client.get(target_url, follow_redirects=True)
            expected_url = url_for('home', _external=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.request.url, expected_url)
    
    """
    test that home page is accessable (status 200 mean page founded)
    """
    def test_homePage_view(self):
        response = self.client.get(url_for('home'))
        self.assertEqual(response.status_code,200)

    '''
    test that in case user loggedIn then he navigated for user_home and not global home (home when user not loggedIN)
    '''
    def user_home_displayed_loggedIN(self):
        with self.client:
            login_user(self.user)
            target_url = url_for('home')
            response = self.client.get(target_url, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('user_home',response.request.url)

    """
    test that FilterPageDetails page is inaccessable (status 200 mean page founded,401 mean not get it )
    """
    def test_FilterPageDetails_view_access_denied(self):
        response = self.client.get(url_for('FilterPageDetails'))
        self.assertEqual(response.status_code,401)

    '''
    test that FilterPageDetails page is accessable when user loggedIN
    '''
    def test_FilterPageDetails_view_access_success(self):
        login_user(self.user)
        response = self.client.get(url_for('FilterPageDetails'))
        self.assertEqual(response.status_code,200)

    '''
    test that updateProfile page is inaccessable when user not loggedIN
    '''
    def test_updateProfile_view_access_denied(self):
        response = self.client.get(url_for('updateProfile'))       
        self.assertEqual(response.status_code,401)

    '''
    test that updateProfile page is accessable when user loggedIN
    '''
    def test_updateProfile_view_access_success(self):
        login_user(self.user)
        response = self.client.get(url_for('updateProfile'))       
        self.assertEqual(response.status_code,200)

    '''
    test that history page is inaccessable when user not loggedIN
    '''
    def test_history_view_access_denied(self):
        response = self.client.get(url_for('history'))       
        self.assertEqual(response.status_code,401)

    '''
    test that history page is accessable when user loggedIN
    '''
    def test_history_view_access_success(self):
        login_user(self.user)
        response = self.client.get(url_for('history'))       
        self.assertEqual(response.status_code,200)

    '''
    test that in case user enter wrong route (not exist) then 404 error page displayed
    '''
    def test_404_not_found(self):
        response = self.client.get('/notExistPage')
        self.assertEqual(response.status_code, 404)




if __name__ == "__main__":
    unittest.main()
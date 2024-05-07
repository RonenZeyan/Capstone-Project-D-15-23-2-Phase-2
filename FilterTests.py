import unittest
from bs4 import BeautifulSoup
import re
from nltk.stem import PorterStemmer
from urllib.parse import urljoin,urlparse
from requests.exceptions import ConnectionError, HTTPError, Timeout
from urllib3.exceptions import NewConnectionError, MaxRetryError
from assr import filter

'''
this class including unit testing for all methods about testing crawling and extracting all links from page(main page of news website and another pages)
'''
class TestingLinkExtractor(unittest.TestCase):  

    '''
    this method run before each test in this class
    '''
    def setUp(self):
        html_content ='''
            <!DOCTYPE html>
                <html lang="en">
                <head>
                    <title>Document</title>
                </head>
                <body>
                    <a href="http://example.com/article1">exampleLink</a>
                    <div>
                        <p>
                            <a href="http://example.com/article2">example inner link</a>
                        </p>
                    </div>
                    <a href="/example2">relative link</a>
                </body>
            </html>
        '''
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.base_url = 'http://example.com'
        self.checked_links = set()

    '''
    this tester check that the get_links_inPage in filter can extract the relevant links 
    '''
    def test_crawling_all_links(self):
        expected_SetLinks = {'http://example.com/article1', 'http://example.com/article2', 'http://example.com/example2'}
        expected_links_absoluteLinks = {'http://example.com/article1':'http://example.com/article1', 'http://example.com/article2':'http://example.com/article2', 'http://example.com/example2':'/example2'}
        expected_absolute_Links = {'http://example.com/article1':'http://example.com/article1', 'http://example.com/article2':'http://example.com/article2', '/example2':'http://example.com/example2'}
        SetLinks, links_abosluteLinks, absolute_Links = filter.get_links_inPage(self.soup, self.base_url, self.checked_links)
        self.assertEqual(SetLinks,expected_SetLinks)
        self.assertEqual(links_abosluteLinks,expected_links_absoluteLinks)
        self.assertEqual(absolute_Links,expected_absolute_Links)

    '''
    this tester check that in case soup is empty then all backed links sets and dict returned empty
    '''
    def test_crawling_empty_links(self):
        expected_SetLinks = set()
        expected_links_absoluteLinks = {}
        expected_absolute_Links = {}
        empty_soup = BeautifulSoup('','html.parser')
        SetLinks, links_abosluteLinks, absolute_Links = filter.get_links_inPage(empty_soup, self.base_url, self.checked_links)
        self.assertEqual(SetLinks,expected_SetLinks)
        self.assertEqual(links_abosluteLinks,expected_links_absoluteLinks)
        self.assertEqual(absolute_Links,expected_absolute_Links)


'''
this class including unit testing for all methods about extracting textual content(articles and others...) from pages 
'''
class TestTextualContentExtractor(unittest.TestCase):
    
    '''
    this method run before each test in this class
    '''
    def setUp(self):
        html_content ='''
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <title>Test Document</title>
            </head>
            <body>
                <h1>Welcome to the test page</h1>
                <p>This is a test page. This page contains simple text to test the function. Test test test.</p>
                <div>Another section with text. Text is important for testing.</div>
                <footer>This is the footer. The footer also has some text.</footer>
            </body>
        </html>
        '''
        self.soup = BeautifulSoup(html_content, 'html.parser')

    '''
    this tester check the extracting of textual content by regular expressions
    '''
    def test_extract_textual_content(self):
        expected = {
    'test': 7,'document': 1,'welcome': 1,'to': 2,'the': 4,'page': 3,'this': 3,'is': 3,'a': 1,'contains': 1,'simple': 1,'text': 4,'function': 1,'another': 1,'section': 1,'with': 1,'important': 1,'for': 1,'testing': 1,'footer': 2,'also': 1,'has': 1,'some': 1
    }

        result = filter.index_words(self.soup)
        self.assertEqual(result,expected,f"Should be {expected}")

    '''
    this tester check that the exception handeled and return empty dict {}
    '''
    def test_exceptionHandling_extract_textualContent(self):
        souping = BeautifulSoup('','html.parser')  #in case text is empty then exception throwed 
        expected = {} #we excpect that the exception handled and return empty dict {}
        result = filter.index_words(souping)
        self.assertEqual(result,expected,f"Should handeled the exception and return empty dict")


'''
this class including unit testing for all methods about testing stemming mission and their occur and stopwords 
'''
class test_stemming_index_words(unittest.TestCase):
    
    '''
    this method run before each test in this class
    '''
    def setUp(self):
        self.index = {
        'test': 7,'document': 1,'welcome': 1,'to': 2,'the': 4,'page': 3,'this': 3,'is': 3,'a': 1,'contains': 1,'simple': 1,'text': 4,'function': 1,'another': 1,'section': 1,'with': 1,'important': 1,'for': 1,'testing': 1,'footer': 2,'also': 1,'has': 1,'some': 1
        }
        self.entered_words = ['testing','welcome']
        
    '''
    this tester check if stemming done fine 
    '''
    def test_apply_stemming(self):
        #words in stemming mode 
        expected = {
            'test': 8,'document': 1,'welcom': 1,'to': 2,'the': 4,'page': 3,'thi': 3,'is': 3,'a': 1,'contain': 1,'simpl': 1,'text': 4,'function': 1,'anoth': 1,'section': 1,'with': 1,'import': 1,'for': 1,'footer': 2,'also': 1,'ha': 1,'some': 1
        }
        result = filter.apply_stemming(self.index)
        self.assertEqual(result,expected,f"should be {expected}")

    '''
    this tester check if stemming done successfully for entered_words by user 
    '''
    def test_entered_words(self):
        expected = ['test','welcom'] #the stem of this words (we can see how testing back to his stem that is test )
        result = filter.Stemming_entered_words(self.entered_words)
        self.assertEqual(result,expected,f"should be {expected}")


    '''
    this tester check if stemming_exist return true when entered_words occur in the textual content of page 
    '''
    def test_check_stemming_exist(self):
        expected = True
        stemming_index = filter.apply_stemming(self.index)
        stemming_words = filter.Stemming_entered_words(self.entered_words) #make stemming for entered words 
        result = filter.check_stemming_exist(stemming_index,stemming_words)
        self.assertEqual(result,expected,f"should be true because words exist")
        self.assertTrue(result,"should returned true")

    '''
    this tester check if stemming_exist return false when entered_words not occur in the textual content of page 
    '''
    def test_check_stemming_not_exist(self):
        expected = False
        stemming_index = filter.apply_stemming(self.index)
        stemming_words = filter.Stemming_entered_words(['playing','murder']) #make stemming for entered words 
        result = filter.check_stemming_exist(stemming_index,stemming_words)
        self.assertEqual(result,expected,f"should be false because words not exist")
        self.assertFalse(result,"should returned false")
    '''
    this tester check if stop words removed successfully from extracted textual content 
    '''    
    def test_removing_stop_words(self):
        expected = {
        'test': 7,'document': 1,'welcome': 1,'to': 2,'page': 3,'this': 3,'is': 3,'contains': 1,'simple': 1,'text': 4,'function': 1,'another': 1,'section': 1,'with': 1,'important': 1,'for': 1,'testing': 1,'footer': 2,'also': 1,'has': 1,'some': 1
        }
        result = filter.remove_stop_words(self.index)
        self.assertEqual(result,expected,f"should be {expected}")


'''
this class including unit testing for all methods about editing and manuplating html page that we will display for user 
'''
class test_editing_page(unittest.TestCase):

    '''
    this method run before each test in this class
    '''
    def setUp(self):
        self.html_content = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Document</title>
            <link rel="stylesheet" href="/testcss.css">
            <link rel="stylesheet" href="https://www.example.com/testingcss.css">
        </head>
        <body>
            <div style="border:solid black;">
                <div style="display: flex;">
                    <article style="border:solid black;">
                        <a href="https://www.example.com/articleA">
                            <img src="testingPic.png" alt="pic">
                            <h3>Lorem ipsum dolor sit amet consectetur.</h3>
                            <p>Lorem ipsum dolor sit amet consectetur adipisicing elit.</p>
                        </a>
                    </article>
                    <article style="border:solid black;">
                        <a href="/articleB">
                            <img data-src="testingPic.png" alt="pic">
                            <h3>Lorem ipsum dolor sit amet consectetur.</h3>
                            <p>Lorem ipsum dolor sit amet consectetur adipisicing elit.</p>
                        </a>
                    </article>
                </div>
                <div>
                    <article style="border:solid black;">
                        <a href="https://www.example.com/articleC">
                            <img src="testingPic.png" alt="pic">
                            <h3>Lorem ipsum dolor sit amet consectetur.</h3>
                            <p>Lorem ipsum dolor sit amet consectetur adipisicing elit.</p>
                        </a>
                    </article>
                </div>
                <div style="display: flex; flex-direction: column; margin: 3px;">
                    <a href="https://www.example.com/article1">article1 - Lorem ipsum dolor sit.</a>
                    <a href="/article2">article2 - Lorem ipsum dolor sit.</a>
                    <a href="https://www.anotherWebsite.com/article3">article3 - Lorem ipsum dolor sit.</a>
                    <a href="https://www.example.com/article4">article4 - Lorem ipsum dolor sit.</a>
                </div>
                <div style="border: 1px solid black;">
                <article>
                    <div style="display: flex; flex-direction: column;">
                        <a href="https://www.example.com/article5">article5 - Lorem ipsum, dolor sit amet consectetur adipisicing elit. Maiores, sequi!</a>
                        <img src="article5-pic.png" alt="pic">
                        <a href="https://www.example.com/article6">
                            <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Amet iste voluptatibus illo placeat itaque quis!</p>
                        </a>
                    </div>
                </article>
                </div>
            </div>
            <script src="/testScript.js"></script>
            <script src="https://www.example.com/testingScript.js"></script>
        </body>
        </html>
    '''
        self.base_url = "https://www.example.com"

    '''
    this tester check if src of image is absolute then nothing changed
    '''
    def test_update_image_sources_with_src(self):
        data = '<img alt="pic" src="https://www.example.com/testingPic.png"/>'
        soup = BeautifulSoup(data,'html.parser')
        expected = '<img alt="pic" src="https://www.example.com/testingPic.png"/>'
        result = filter.update_image_sources(soup,self.base_url)
        self.assertEqual(expected,str(result))
    
    '''
    this tester check if img with data_src or onother attribute then we add src to display for user 
    '''
    def test_update_image_sources_with_data_src(self):
        data = '<img alt="pic" data-src="testingPic.png"/>'
        soup = BeautifulSoup(data,'html.parser')
        expected = '<img alt="pic" data-src="testingPic.png" src="https://www.example.com/testingPic.png"/>'
        result = filter.update_image_sources(soup,self.base_url)
        self.assertEqual(expected,str(result))

    '''
    this tester check if src of image is relative then src changed to absolute path
    '''
    def test_update_image_sources_with_relative_srv(self):
        data = '<img alt="pic" data-src="testingPic.png"/>'
        soup = BeautifulSoup(data,'html.parser')
        expected = '<img alt="pic" data-src="testingPic.png" src="https://www.example.com/testingPic.png"/>'
        result = filter.update_image_sources(soup,self.base_url)
        self.assertEqual(expected,str(result))

    '''
    this testing check if convert link tags(css links) from relative to absolute done successfully
    '''
    def test_convert_relative_path_css(self):
        data = '<link href="/testcss.css"/>'
        expected = '<link href="https://www.example.com/testcss.css"/>'
        soup = BeautifulSoup(data,'html.parser')
        result = filter.change_css_js_href_to_absoulute(soup,self.base_url)
        self.assertEqual(expected,str(result))
    
    '''
    this tester check delete page tags in div with others pages tags (check that tags belong to others pages not deleted and all tags in article want to delete has been deleted successfully)
    '''
    def test_delete_article_in_div_with_another(self):
        data = '<a href="https://www.example.com/articleA">'
        img_belong_article = '<img src="testingPic.png" alt="pic">'
        h3_belong_article = '<h3>Lorem ipsum dolor sit amet consectetur-article1</h3>'
        p_belong_article = '<p>Lorem ipsum dolor sit amet consectetur adipisicing elit-article1</p>'
        data1 = '<a href="/articleB">'
        links_to_delete = ['https://www.example.com/articleA']
        soup = BeautifulSoup(self.html_content,'html.parser')
        result = filter.herarchial_delete_of_article_bounds(soup,links_to_delete)
        self.assertNotIn(data,str(result),"the article should be deleted and not exist in the html_code")
        self.assertNotIn(img_belong_article,str(result),"the article should be deleted and not exist in the html_code")
        self.assertNotIn(h3_belong_article,str(result),"the article should be deleted and not exist in the html_code")
        self.assertNotIn(p_belong_article,str(result),"the article should be deleted and not exist in the html_code")
        self.assertIn(data1,str(result),"the article B should be exist and not deleted") #article B in html_code is in the same div with article 1 

    '''
    this tester checking delete page/article in a_tag and other pages with a_tags also (other pages should not be deleted (data1))
    '''
    def test_delete_article_in_aTag(self):
        data = '<a href="https://www.example.com/article1">article1 - Lorem ipsum dolor sit.</a>'
        data1 = '<a href="/article2">article2 - Lorem ipsum dolor sit.</a>'
        links_to_delete = ['https://www.example.com/article1']
        soup = BeautifulSoup(self.html_content,'html.parser')
        result = filter.herarchial_delete_of_article_bounds(soup,links_to_delete)
        self.assertNotIn(data,str(result),"the article1 should be deleted")
        self.assertIn(data1,str(result),"the article 2 should be exist and not deleted") #article B in html_code is in the same div with article 1 

    '''
    this tester checking delete page/article in a_tag with that included in article tag with other articles (code in html_content in )
    '''
    def test_delete_article_in_articleTag_with_other_articles(self):
        data = '<a href="https://www.example.com/article6">'
        p_belong_article = '<p>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Amet iste voluptatibus illo placeat itaque quis!</p>'
        img_not_belong_article = '<img alt="pic" src="article5-pic.png"/>'
        article_not_belong = '<a href="https://www.example.com/article5">article5 - Lorem ipsum, dolor sit amet consectetur adipisicing elit. Maiores, sequi!</a>'
        links_to_delete = ['https://www.example.com/article6']
        soup = BeautifulSoup(self.html_content,'html.parser')
        result = filter.herarchial_delete_of_article_bounds(soup,links_to_delete)
        self.assertNotIn(data,str(result),"the article should be deleted and not exist in the html_code")
        self.assertNotIn(p_belong_article,str(result),"the p should be deleted and not exist in the html_code")
        self.assertIn(img_not_belong_article,str(result),"the img should be not deleted and exist in the html_code")
        self.assertIn(article_not_belong,str(result),"the article 5 should be exist and not deleted") #article B in html_code is in the same div with article 1 
       
    '''
    this tester check manipulate html_code of page by check if it change the href of a_tag to another href
    '''
    def test_manipulate_html_code(self):
        links_to_delete = ['https://www.example.com/article1']
        absolute_links = {'https://www.example.com/article6':'https://www.example.com/article6'}
        expected = '<a href="/displayFilteredArticle/https:**www.example.com*article6">'
        article_deleted = '<a href="https://www.example.com/article1">article1 - Lorem ipsum dolor sit.</a>'
        soup = BeautifulSoup(self.html_content,'html.parser')
        result = filter.manipulate_toDisplay_htmlPage(soup,links_to_delete,absolute_links,self.base_url)
        self.assertIn(expected,str(result),"check that href path changed successfully")
        self.assertNotIn(article_deleted,str(result),"check that article 1 deleted")
        self.assertIsNotNone(soup,"soup should not returned none")

    '''
    this tester check that soup returned none in case links_to_delete is none
    '''
    def test_manipulate_html_code_return_null_with_Nonearticles(self):
        links_to_delete = None
        soup = BeautifulSoup(self.html_content,'html.parser')
        expected = True
        result = filter.manipulate_toDisplay_htmlPage(soup,links_to_delete,{},self.base_url)
        self.assertIsNone(result,"should return none")

    '''
    this tester check that soup returned none in case soup(before editing) is none
    ''' 
    def test_manipulate_html_code_return_null_with_noneSoup(self):
        links_to_delete = []
        soup = None
        expected = True
        result = filter.manipulate_toDisplay_htmlPage(soup,links_to_delete,{},self.base_url)
        self.assertIsNone(result,"should return none")

    # '''
    # this tester check that soup has returned as same soup sended in case no links to delete 
    # '''
    # def test_manipulate_html_code_return_soup_with_empty_links(self):
    #     links_to_delete = ()
    #     soup = "hello world"
    #     result = filter.manipulate_toDisplay_htmlPage(soup,links_to_delete,{},self.base_url)
    #     self.assertEqual(soup,result)



if __name__ == "__main__":
    unittest.main()
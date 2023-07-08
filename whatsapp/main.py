from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.remote_connection import LOGGER as selenium_logger
from selenium.common.exceptions import NoSuchElementException, WebDriverException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from . import commands
import threading
import platform
import urllib3
import getpass
import logging
import shutil
import time
import json
import sys
import os

dir = __file__.replace(f'{os.path.basename(__file__)}','').replace('\\','/')
sys.path.append(dir)

with open(f'{dir}/xpath.json', 'r') as openfile:
    xpathData = json.load(openfile)

driver = None

system = platform.uname()
sysinfo = {
"System"    : system.system,
"Node Name" : system.node,
"Release"   : system.release,
"Version"   : system.version,
"Machine"   : system.machine,
"Processor" : system.processor
}


class run:
    '''
    An unofficial Python wrapper for Whatsapp
    '''
    def __init__(
        self,
        browser : str = 'Chrome',
        headless : bool = True,
        spawn_qrwindow : bool = True,
        terminal_qr : bool = True,
        profile : str = "Default",
        waitTime : int = 0,
        command_classes : list = [],
        customDriver = None,
        profileDir : str = "Default",
        clean_start : bool = False,
        log : bool = True,
        logFile : bool = False,
        logLevel : logging = logging.CRITICAL
    ) -> None:
        """
        This function is the constructor for a class and initializes its attributes with default values.
        
        :param browser: The browser parameter is a string that specifies the browser to be used. The
        default value is 'Chrome', defaults to Chrome
        :type browser: str (optional)
        :param headless: The "headless" parameter determines whether the browser should run in headless
        mode or not. Headless mode means that the browser will run without a graphical user interface,
        which can be useful for running automated tests or scraping data from websites, defaults to True
        :type headless: bool (optional)
        :param spawn_qrwindow: A boolean value indicating whether to spawn a separate window to display
        the QR code for logging in, defaults to True
        :type spawn_qrwindow: bool (optional)
        :param terminal_qr: A boolean value indicating whether to display the QR code in the terminal or
        not. If set to True, the QR code will be displayed in the terminal, defaults to True
        :type terminal_qr: bool (optional)
        :param profile: The `profile` parameter is used to specify the profile directory to be used by
        the browser. By default, it is set to "Default", which means the default profile directory will
        be used. However, you can specify a different profile directory if needed, defaults to Default
        :type profile: str (optional)
        :param waitTime: The `waitTime` parameter is an integer that represents the time in seconds to
        wait till whatsapp.web loads. If whatsapp.web fails to load before waitTime program is terminated.
        When waitTime is 0 it waits forever, defaults to 0
        :type waitTime: int (optional)
        :param command_classes: The `command_classes` parameter is a list that allows you to pass custom
        command written inside classes.
        :type command_classes: list
        :param customDriver: The `customDriver` parameter is used to provide a custom WebDriver
        instance. This allows you to use a different browser driver other than the default one provided
        by the library
        :param profileDir: The `profileDir` parameter is used to specify the directory where the user
        profile for the browser is located. By default, it is set to "Default", which means it will use
        the default profile directory for the browser. However, you can specify a different directory if
        needed, defaults to Default
        :type profileDir: str (optional)
        :param clean_start: The `clean_start` parameter is a boolean flag that determines whether the
        browser should start with a fresh profile or not. If `clean_start` is set to `True`, the browser
        will start with a new profile, discarding any existing user data, defaults to False
        :type clean_start: bool (optional)
        :param log: A boolean value indicating whether or not to enable logging, defaults to True
        :type log: bool (optional)
        :param logFile: A boolean value indicating whether to log the output to a file or not, defaults
        to False
        :type logFile: bool (optional)
        :param logLevel: The `logLevel` parameter is used to specify the level of logging that should be
        recorded, defaults to logging.CRITICAL
        :type logLevel: logging
        """

        global driver
        driver = customDriver

        self.browser = browser
        self.driver = driver
        self.headless = headless
        self.profile = profile
        self.profileDir = profileDir
        self.log = log
        self.logFile = logFile
        self.logLevel = logLevel
        self.user = getpass.getuser()
        self.os = sysinfo["System"]
        self.ready = False
        self.spawn_qrwindow = spawn_qrwindow
        self.terminal_qr = terminal_qr
        self.waitTime = waitTime
        self.command_classes = command_classes

        if(self.os == "Linux"):
            self.spawn_qrwindow = False

        if(log):
            if(logFile):
                logging.basicConfig(filename='Debug.log', format="%(levelno)s:%(asctime)s:%(levelname)s:%(message)s", filemode="w", encoding='utf-8', level=logLevel)
            else:
                logging.basicConfig(format="%(levelno)s:%(asctime)s:%(levelname)s:%(message)s", level=logLevel)

            selenium_logger.setLevel(logging.CRITICAL)
            urllib3_logger = logging.getLogger("urllib3")
            urllib3_logger.setLevel(logging.CRITICAL)

        if(clean_start):
            self.__clean_start__()

        threading.Thread(target=commands.setup_extension, args=(self.command_classes,), daemon=True).start() #Sets up all the commands inside classes
        self.__setup_driver_preference__()
        self.__on_ready__()

    def __setup_driver_preference__(self):
        self.browser = self.browser.lower()
        if(self.browser == None and self.driver == None):
            logging.warning("No Browser Defined!")
            raise Exception("No Browser Defined!")

        if(self.browser != "chrome" and self.browser != "firefox" and self.driver == None):
            logging.warning("UnSupported Browser!")
            raise Exception("Supported Browsers Are Chrome And Firefox")

        if(self.driver == None):
            if(sysinfo["System"] == "Windows"):
                self.__initialize_driver__()
                get_link("https://web.whatsapp.com/")
                
            elif(sysinfo["System"] == "Linux"):
                self.__initialize_driver__()
                get_link("https://web.whatsapp.com/")

            else:
                raise Exception("UnSupported OS")

        elif(str(type(self.driver)) == "<class 'selenium.webdriver.chrome.webdriver.WebDriver'>"):
            logging.info("Using Custom Driver!")
            self.__initialize_driver__()
            get_link("https://web.whatsapp.com/")

        else:
            logging.warning("Invalid Driver!")
            raise Exception("Driver Error! / Invalid Driver!")
        
        startup_checks(spawn_qrwindow=self.spawn_qrwindow, terminal_qr=self.terminal_qr).wait_to_load(waitTime=self.waitTime)
        if(self.driver == None and self.os != None and self.browser != None):
            
            self._defaultDriver()

    def __initialize_driver__(self):
        global driver

        logging.info(f"Initializing Driver for {self.os},{self.browser},Headless={self.headless}")

        #Driver setup for Windows
        if(self.driver == None and self.os == "Windows" and self.browser == "chrome"):
            chrome_options = Options()
            chrome_options.add_argument(f"user-agent={xpathData.get('userAgent_Chrome')}")

            if(self.profileDir == "Default" and self.profile != "Default"):
                chrome_options.add_argument(f"user-data-dir=C:\\Users\\{self.user}\\AppData\\Local\\Google\\Chrome\\User Data")
                chrome_options.add_argument(f"profile-directory={self.profile}")

            elif(self.profileDir != "Default"):
                chrome_options.add_argument(f"user-data-dir={self.profileDir}")
                chrome_options.add_argument(f"profile-directory={self.profile}")

            elif(self.profileDir == "Default" and self.profile == "Default"):
                chrome_options.add_argument(f"user-data-dir={dir}/dependences/ChromeProfile")
                chrome_options.add_argument(f"profile-directory={self.profile}")

            if(self.headless):
                chrome_options.add_argument("--start-maximized")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-gpu")

            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("disable-infobars")
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--max-connections=5")
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')

            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            driver = webdriver.Chrome(options=chrome_options)
            self.driver = driver

            logging.info("Driver Initialized!")
        
        #Driver setup for Linux
        elif(self.driver == None and self.os == "Linux" and self.browser == "chrome"):
            chrome_options = Options()
            chrome_options.add_argument(f"user-agent={xpathData.get('userAgent_Chrome')}")

            if(self.profileDir == "Default" and self.profile != "Default"):
                chrome_options.add_argument(f"user-data-dir=/home/{self.user}/.config/google-chrome")
                chrome_options.add_argument(f"profile-directory={self.profile}")

            elif(self.profileDir != "Default"):
                chrome_options.add_argument(f"user-data-dir={self.profileDir}")
                chrome_options.add_argument(f"profile-directory={self.profile}")

            elif(self.profileDir == "Default" and self.profile == "Default"):
                chrome_options.add_argument(f"user-data-dir={dir}/dependences/ChromeProfile")
                chrome_options.add_argument(f"profile-directory={self.profile}")

            if(self.headless):
                chrome_options.add_argument("--start-maximized")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-gpu")

            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("disable-infobars")
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--max-connections=5")
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')

            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            driver = webdriver.Chrome(options=chrome_options)
            self.driver = driver

            logging.info("Driver Initialized!")
        
        else:
            logging.CRITICAL("Unsupported Operating System")
            raise Exception("Unsupported Operating System")

    def __clean_start__(self):
        logging.info("Clean Start")
        if(os.path.exists(f"{dir}/dependences/ChromeProfile/Default")):
            try:
                shutil.rmtree(rf"{dir}/dependences/ChromeProfile/Default")
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))

    def __on_ready__(self):
        global __on_ready_callbacks__
        if(self.driver != None):
            for i in __on_ready_callbacks__:
                threading.Thread(target=i).start()

class startup_checks:
    def __init__(self, spawn_qrwindow : bool, terminal_qr : bool) -> None:
        self.stop_threads = False
        self.login_check_thread = None
        self.is_loggedin = False
        self.was_loggedout = False
        self.qr_manager = None
        self.spawn_qrwindow = spawn_qrwindow
        self.terminal_qr = terminal_qr
        pass

    def wait_to_load(self, waitTime : int):

        self.login_check_thread = threading.Thread(target=self.login_check, daemon=True)
        self.login_check_thread.start()
        logging.info(f"login_check Thread Started!, is_Alive? = {self.login_check_thread.is_alive()}")

        while time.time() < time.time() + waitTime or waitTime == 0:
            if(self.stop_threads):
                if(self.was_loggedout):
                    if(self.qr_manager != None and not self.qr_manager.stop):
                        self.qr_manager.quit()

                    self.qr_manager = None
                    print("Waiting for Whatsapp.web to store cache")
                    driver.refresh() #Refresh to ensure whatsapp keeps logged in
                    quit() #Quitting safely to ensure whatsapp is logged in
                    
                    if(os.path.exists(f"qrcode.png")):
                        try:
                            os.remove(f"qrcode.png")
                        except OSError as e:
                            print("Error: %s - %s." % (e.filename, e.strerror))

                    print("Restart needed after login")

                    exit()
                    # while True:
                    #     try:
                    #         driver.find_element(By.XPATH, xpathData.get('searchBox'))
                    #         logging.info("Stopping Startup Thread")
                    #         logging.info(f"Is LoggedIn = {self.is_loggedin}")
                    #         break
                    #     except NoSuchElementException:
                    #         time.sleep(0.1)
                    #         continue
                    # break
                else:
                    break
            time.sleep(0.5)
        else:
            self.stop_threads = True
            logging.info("Stopping Startup Threads")
            logging.warning("Session Time Expired!,(Login Error ?)")
            quit()
            raise Exception("Session Time Expired!,(Login Error ?)")


    def login_check(self):
        while True:
            if(self.stop_threads == True):
                logging.info("login_check Thread Stopped!")
                break

            try:
                driver.find_element(By.XPATH, xpathData.get('searchBox'))
                self.stop_threads = True
                self.is_loggedin = True
                logging.info("Stopping Startup Thread")
                logging.info(f"Is LoggedIn = {self.is_loggedin}")
                break
            except NoSuchElementException:
                try:
                    qr_id = driver.find_element(By.XPATH, '//div[@data-testid="qrcode"]').get_attribute("data-ref")
                    logging.warning("Not Loggedin!")
                    print("Not Loggedin, Waiting for Whatsapp.web to generate QRCODE")
                    self.qr_manager = qr_manager(self.spawn_qrwindow, self.terminal_qr)
                    self.is_loggedin = False
                    self.was_loggedout = True
                    self.qr_manager.start(qr_id=qr_id)
                except NoSuchElementException:
                    time.sleep(0.1)
                    continue

class qr_manager:
    def __init__(self, spawn_qrwindow : bool, terminal_qr : bool):
        self.__qrcode__ = __import__("qrcode")
        self.stop = False
        self.spawn_qrwindow = spawn_qrwindow
        self.terminal_qr = terminal_qr

        if(spawn_qrwindow):
            from PIL import Image, ImageTk
            self.__tk__ = __import__("tkinter")
            self.__Image__ = Image
            self.__ImageTK__ = ImageTk
            self.qrwindow_root = self.__tk__.Tk()

            if sys.platform.startswith("win"):
                self.qrwindow_root.wm_attributes("-topmost", 1)
            elif sys.platform.startswith("darwin"):
                self.qrwindow_root.createcommand('tk::mac::ReopenApplication',
                                lambda: self.qrwindow_root.event_generate('<<ReopenApplication>>'))
                self.qrwindow_root.createcommand('tk::mac::Preferences',
                                lambda: self.qrwindow_root.event_generate('<<Preferences>>'))
                self.qrwindow_root.createcommand('tk::mac::Quit',
                                lambda: self.qrwindow_root.event_generate('<<Quit>>'))
                self.qrwindow_root.createcommand('::tk::mac::ShowPreferences',
                                lambda: self.qrwindow_root.event_generate('<<ShowPreferences>>'))
                self.qrwindow_root.createcommand('::tk::mac::ShowHelp',
                                lambda: self.qrwindow_root.event_generate('<<ShowHelp>>'))
                self.qrwindow_root.createcommand('::tk::mac::Hide',
                                lambda: self.qrwindow_root.event_generate('<<Hide>>'))
            else:
                # Linux (requires external libraries like python-xlib)
                self.qrwindow_root.wm_attributes("-topmost", 1)

            self.qrwindow_root.overrideredirect(True)
            self.qrwindow_root.attributes("-toolwindow", 1)
            self.qrwindow_root.protocol("WM_DELETE_WINDOW", lambda: None)

            self.filename = "qrcode.png"
            self.label = None

    def create_qr_image(self):
        try:
            image = self.__Image__.open(self.filename)
            image = image.resize((300, 300))
            photo = self.__ImageTK__.PhotoImage(image)

            if self.label is not None:
                self.label.configure(image=photo)
                self.label.image = photo  # Keep a reference to avoid garbage collection
            else:
                self.label = self.__tk__.Label(self.qrwindow_root, image=photo)
                self.label.image = photo  # Keep a reference to avoid garbage collection
                self.label.pack()
        except:
            pass

        if(not self.stop):
            self.qrwindow_root.after(1000, self.create_qr_image)

    def print_terminal_qr(self,data, update:bool):
        qr = self.__qrcode__.QRCode(
            version=1,
            error_correction=self.__qrcode__.constants.ERROR_CORRECT_L,
            box_size=1,
            border=0,
        )
        qr.add_data(data)
        qr.make(fit=True)

        if(update):
            sys.stdout.write("\033[s")
            sys.stdout.write("\033[27A")
    
        # qr.print_tty()
        qr.print_ascii()

    def update_qr(self, qr_id):
        previous_qr_id = qr_id
        if(self.spawn_qrwindow == False and self.terminal_qr == False):
            return
        while not self.stop:
            try:
                qr_id = driver.find_element(By.XPATH, '//div[@data-testid="qrcode"]').get_attribute("data-ref")
            except:
                self.quit()
                break
            if(previous_qr_id != qr_id):
                if(self.spawn_qrwindow):
                    qr = self.__qrcode__.QRCode()
                    qr.add_data(qr_id)
                    qr.make_image().save(self.filename)

                if(self.terminal_qr):
                    self.print_terminal_qr(qr_id,True)

                previous_qr_id = qr_id
            time.sleep(0.5)
        return

    def start(self, qr_id):
        if(self.spawn_qrwindow == True and self.terminal_qr == True):
            qr = self.__qrcode__.QRCode()
            qr.add_data(qr_id)
            qr.make_image().save(self.filename)
            self.create_qr_image()
            logging.info('Starting qr_manager')
            threading.Thread(target = self.print_terminal_qr, args=(qr_id,False)).start()
            threading.Thread(target=self.update_qr, args=(qr_id,)).start()
            self.qrwindow_root.mainloop()

        elif(self.terminal_qr == True and self.spawn_qrwindow == False):
            threading.Thread(target = self.print_terminal_qr, args=(qr_id,False)).start()
            self.update_qr(qr_id)

        elif(self.spawn_qrwindow == True and self.terminal_qr == False):
            qr = self.__qrcode__.QRCode()
            qr.add_data(qr_id)
            qr.make_image().save(self.filename)
            logging.info('Starting qr_manager')
            threading.Thread(target=self.update_qr, args=(qr_id,)).start()
            self.qrwindow_root.mainloop()
    
    def quit(self):
        self.stop = True
        if(self.terminal_qr):
            sys.stdout.write("\033[27A")
            for _ in range(27):
                print(" " * 55)
            sys.stdout.write("\033[27A\n")
        print("Cleaning UP")
        if(self.spawn_qrwindow):
            logging.info('Quitting qr_manager')
            self.qrwindow_root.withdraw()
            self.qrwindow_root.quit()

__on_ready_callbacks__ = []
def on_ready(callBack):
    global __on_ready_callbacks__
    __on_ready_callbacks__.append(callBack)

def get_link(link : str):
    try:
        driver.get(link)
    except WebDriverException:
        logging.critical("DNS ERROR, Webpage Down")
        raise Exception("DNS ERROR, Webpage Down")

def quit():
    logging.info("Quitting!")
    driver.quit()

class openChat:
    def __init__(self, contact : str, new: bool = False) -> None:
        self.__contact = contact
        if(new):
            self.openNew()
        else:
            self.open()

    def open(self):
        searchBox = driver.find_element(By.XPATH, xpathData.get('searchBox'))
        searchBox.click()
        searchBox.send_keys(self.__contact)
        time.sleep(1)
        try:
            # driver.find_element(By.XPATH, xpathData.get("searchResult")).click()
            actions = ActionChains(driver=driver) 
            actions.send_keys(Keys.TAB * 2)
            actions.perform()
            WebDriverWait(driver,1).until(EC.presence_of_element_located((By.XPATH, xpathData.get('chatBox'))))
        except NoSuchElementException:
            raise Exception(f"No chat found for {self.__contact}, If you never sent message to this contact use new=True (Use phone number insted of contact name)")
    
    def openNew(self):
        get_link(f'https://web.whatsapp.com/send?phone={self.__contact}')
        startup_checks(spawn_qrwindow=False,terminal_qr=False).wait_to_load(waitTime=0)
        try:
            WebDriverWait(driver,3).until(EC.presence_of_element_located((By.XPATH, xpathData.get('chatBox'))))
        except:
            if(driver.find_element(By.XPATH, xpathData.get("invalidPhoneNumber")).text == "Phone number shared via url is invalid."):
                raise Exception("Invalid PhoneNumber")


class send:
    def __init__(self, message : str, waitTillDelivered : bool = False, waitTime : int = 0) -> None:
        '''
        Parameters:
        - message : Message to be sent
        - waitTillDelivered : Waits till message is delivered
        - waitTime : Time in Seconds to wait till message is deliverd, 0 to wait forever (default)
        '''
        self.__message = message
        self.__waitTillDelivered = waitTillDelivered
        self.__waitTime = waitTime
        self.id = None
        self.__send()
    
    def __send(self):
        global _LsentID
        global _pause
        _pause = True
        chatBox = driver.find_element(By.XPATH, xpathData.get('chatBox'))
        chatBox.click()
        message = self.__message.splitlines()
        for i in message:
            if(i == ""):
                chatBox.send_keys(Keys.SHIFT + Keys.RETURN) #If \n is at start
            else:
                chatBox.send_keys(i)
                chatBox.send_keys(Keys.SHIFT + Keys.RETURN)
        chatBox.send_keys(Keys.RETURN)
        self.id = driver.find_element(By.XPATH, f"({xpathData.get('sentMSG')})[last()]").get_attribute("data-id")
        _LsentID = self.id
        _pause = False
        if(self.__waitTillDelivered):
            self.__wait()

    def __wait(self):
        while time.time() < time.time() + self.__waitTime or self.__waitTime == 0:
            try:
                driver.find_element(By.XPATH, f'{xpathData.get("sentMSG").replace("true",self.id)}{xpathData.get("msgStatus").replace("PLACEHOLDER", " Pending ")}')
                time.sleep(0.1)
                continue
            except:
                try:
                    driver.find_element(By.XPATH, f'{xpathData.get("sentMSG").replace("true",self.id)}{xpathData.get("msgStatus").replace("PLACEHOLDER", " Sent ")}')
                except NoSuchElementException:
                    try:
                        driver.find_element(By.XPATH, f'{xpathData.get("sentMSG").replace("true",self.id)}{xpathData.get("msgStatus").replace("PLACEHOLDER", " Read ")}')
                    except NoSuchElementException:
                        driver.find_element(By.XPATH, f'{xpathData.get("sentMSG").replace("true",self.id)}{xpathData.get("msgStatus").replace("PLACEHOLDER", " Delivered ")}')
                break

    def __repr__(self) -> str:
        return self.id
    
class getSent:
    def __init__(self) -> None:
        self.id = None
        self.body = None
        self.__getSent()
        pass

    def __getSent(self):
        try:
            sentID = driver.find_element(By.XPATH, f"({xpathData.get('sentMSG')})[last()]").get_attribute("data-id")
        except (NoSuchElementException, StaleElementReferenceException, AttributeError):
            raise Exception(f"Maybe no chat opend ?! Error!")
            
        if(sentID != self.id):
            self.id = sentID
            try:
                self.body = driver.find_element(By.XPATH, f'{xpathData.get("textByID").replace("PLACEHOLDER",sentID)}').text
            except (NoSuchElementException, StaleElementReferenceException):
                raise Exception(f"Not a text, Maybe video or sticker or files Error!")
            
    def __repr__(self) -> str:
        return self
    
class waitToSend:
    def __init__(self, waitTime : int = 0) -> None:
        '''
        Parameters:
        - waitTime : Time in Seconds to wait till message is recived, 0 to wait forever (default)
        '''
        self.id = None
        self.body = None
        self.__waitTime = waitTime
        self.__wait()
        pass
    
    def __wait(self):
        while time.time() < time.time() + self.__waitTime or self.__waitTime == 0:
            try:
                sentID = driver.find_element(By.XPATH, f"({xpathData.get('sentMSG')})[last()]").get_attribute("data-id")
            except (NoSuchElementException, StaleElementReferenceException, AttributeError):
                time.sleep(0.1)
                continue
            if(sentID != self.id):
                if(self.id == None):
                    self.id = sentID
                    continue
                self.id = sentID
                try:
                    self.body = driver.find_element(By.XPATH, f'{xpathData.get("textByID").replace("PLACEHOLDER",sentID)}').text
                    break
                except (NoSuchElementException, StaleElementReferenceException):
                    time.sleep(0.1)
                    continue
            time.sleep(0.1)

    def __repr__(self) -> str:
        return self

_LsentID = None
_pause = False

class __onSend:
    def __init__(self) -> None:
        self.id = None
        self.body = None
        self.__sentMsg()
        pass

    def __sentMsg(self):
        global _LsentID
        global _pause
        while True:
            if(_pause):
                time.sleep(0.1)
                continue
            try:
                sentID = driver.find_element(By.XPATH, f"({xpathData.get('sentMSG')})[last()]").get_attribute("data-id")
            except (NoSuchElementException, StaleElementReferenceException, AttributeError):
                time.sleep(0.1)
                continue
            if(sentID != self.id and _LsentID != sentID):
                if(self.id == None):
                    self.id = sentID
                    continue
                self.id = sentID
                try:
                    self.body = driver.find_element(By.XPATH, f'{xpathData.get("textByID").replace("PLACEHOLDER",sentID)}').text
                    threading.Thread(target=__on_send_callback_fn__, args=(self,)).start()
                except (NoSuchElementException, StaleElementReferenceException):
                    time.sleep(0.1)
                    continue
            time.sleep(0.1)

def __on_send_callback_fn__(self):
    global __on_send_callbacks__
    for i in __on_send_callbacks__:
        threading.Thread(target=i, args=(self,)).start()

__on_send_thread__ = None
__on_send_callbacks__ = []
def on_send(callBack):
    """
    The function `on_send` adds a callback function to a list of callbacks.
    
    :param callBack: The `callBack` parameter is a function that will be executed when the `on_send`
    function is called
    """
    global __on_send_callbacks__
    __on_send_callbacks__.append(callBack)

class getRecived:
    def __init__(self) -> None:
        self.id = None
        self.body = None
        self.__getRecived()
        pass

    def __getRecived(self):
        try:
            recivedID = driver.find_element(By.XPATH, f"({xpathData.get('recivedMSG')})[last()]").get_attribute("data-id")
        except (NoSuchElementException, StaleElementReferenceException, AttributeError):
            raise Exception(f"Maybe no chat opend ?! Error!")
            
        if(recivedID != self.id):
            self.id = recivedID
            try:
                self.body = driver.find_element(By.XPATH, f'{xpathData.get("textByID").replace("PLACEHOLDER",recivedID)}').text
            except (NoSuchElementException, StaleElementReferenceException):
                raise Exception(f"Not a text, Maybe video or sticker or files Error!")
            
    def __repr__(self) -> str:
        return self
    
class waitToRecive:
    def __init__(self, waitTime : int = 0) -> None:
        '''
        Parameters:
        - waitTime : Time in Seconds to wait till message is recived, 0 to wait forever (default)
        '''
        self.id = None
        self.body = None
        self.__waitTime = waitTime
        self.__wait()
        pass
    
    def __wait(self):
        while time.time() < time.time() + self.__waitTime or self.__waitTime == 0:
            try:
                recivedID = driver.find_element(By.XPATH, f"({xpathData.get('recivedMSG')})[last()]").get_attribute("data-id")
            except (NoSuchElementException, StaleElementReferenceException, AttributeError):
                time.sleep(0.1)
                continue
            if(recivedID != self.id):
                if(self.id == None):
                    self.id = recivedID
                    continue
                self.id = recivedID
                try:
                    self.body = driver.find_element(By.XPATH, f'{xpathData.get("textByID").replace("PLACEHOLDER",recivedID)}').text
                    break
                except (NoSuchElementException, StaleElementReferenceException):
                    time.sleep(0.1)
                    continue
            time.sleep(0.1)

    def __repr__(self) -> str:
        return self

class __onRecive:
    def __init__(self) -> None:
        self.id = None
        self.body = None
        self.__reciveMsg()
        pass
    
    def __reciveMsg(self):
        while True:
            try:
                recivedID = driver.find_element(By.XPATH, f"({xpathData.get('recivedMSG')})[last()]").get_attribute("data-id")
            except (NoSuchElementException, StaleElementReferenceException, AttributeError):
                time.sleep(0.1)
                continue
            if(recivedID != self.id):
                if(self.id == None):
                    self.id = recivedID
                    continue
                self.id = recivedID
                try:
                    self.body = driver.find_element(By.XPATH, f'{xpathData.get("textByID").replace("PLACEHOLDER",recivedID)}').text
                    threading.Thread(target=__on_recive_callback_fn__, args=(self,)).start()
                except (NoSuchElementException, StaleElementReferenceException):
                    time.sleep(0.1)
                    continue
            time.sleep(0.1)

def __on_recive_callback_fn__(self):
    global __on_recive_callbacks__
    for i in __on_recive_callbacks__:
        threading.Thread(target=i, args=(self,)).start()

__on_recive_callbacks__ = []
__recive_thread__ = None
def on_recive(callBack):
    """
    The function `on_recive` adds a callback function to a list of callbacks.
    
    :param callBack: The `callBack` parameter is a function that will be called when a receive event
    occurs.
    """
    global __on_recive_callbacks__
    global __recive_thread__
    __on_recive_callbacks__.append(callBack)

class getMessage:
    def __init__(self) -> None:
        self.id = None
        self.body = None
        self.__getMessage()
        pass

    def __getMessage(self):
        try:
            msgID = driver.find_element(By.XPATH, f"({xpathData.get('msg')})[last()]").get_attribute("data-id")
        except (NoSuchElementException, StaleElementReferenceException, AttributeError):
            raise Exception(f"Maybe no chat opend ?! Error!")
            
        if(msgID != self.id):
            self.id = msgID
            try:
                self.body = driver.find_element(By.XPATH, f'{xpathData.get("textByID").replace("PLACEHOLDER",msgID)}').text
            except (NoSuchElementException, StaleElementReferenceException):
                raise Exception(f"Not a text, Maybe video or sticker or files Error!")
            
    def __repr__(self) -> str:
        return self

class wait_for_message:
    def __init__(self, waitTime : int = 0) -> None:
        '''
        Parameters:
        - waitTime : Time in Seconds to wait till message is recived, 0 to wait forever (default)
        '''
        self.id = None
        self.body = None
        self.__waitTime = waitTime
        self.__wait()
        pass
    
    def __wait(self):
        while time.time() < time.time() + self.__waitTime or self.__waitTime == 0:
            try:
                msgID = driver.find_element(By.XPATH, f"({xpathData.get('msg')})[last()]").get_attribute("data-id")
            except (NoSuchElementException, StaleElementReferenceException, AttributeError):
                time.sleep(0.1)
                continue
            if(msgID != self.id):
                if(self.id == None):
                    self.id = msgID
                    continue
                self.id = msgID
                try:
                    self.body = driver.find_element(By.XPATH, f'{xpathData.get("textByID").replace("PLACEHOLDER",msgID)}').text
                    break
                except (NoSuchElementException, StaleElementReferenceException):
                    time.sleep(0.1)
                    continue
            time.sleep(0.1)

    def __repr__(self) -> str:
        return self

class __onMessage:
    def __init__(self) -> None:
        self.id = None
        self.body = None
        self.__getMsg()
        pass
    
    def __getMsg(self):
        while True:
            try:
                msgID = driver.find_element(By.XPATH, f"({xpathData.get('msg')})[last()]").get_attribute("data-id")
            except (NoSuchElementException, StaleElementReferenceException, AttributeError):
                time.sleep(0.1)
                continue
            if(msgID != self.id):
                if(self.id == None):
                    self.id = msgID
                    continue
                self.id = msgID
                try:
                    self.body = driver.find_element(By.XPATH, f'{xpathData.get("textByID").replace("PLACEHOLDER",msgID)}').text
                    threading.Thread(target=__on_message__callback_fn__, args=(self,)).start()
                except (NoSuchElementException, StaleElementReferenceException):
                    time.sleep(0.1)
                    continue
            time.sleep(0.1)

def __on_message__callback_fn__(self):
    global __on_message__callbacks__
    for i in __on_message__callbacks__:
        threading.Thread(target=i, args=(self,)).start()

__on_message__callbacks__ = []
__on_message__thread__ = None
def on_message(callBack):
    """
    The function `on_message` adds a callback function to a list of callbacks.
    
    :param callBack: The `callBack` parameter is a function that will be called whenever a new message
    is received
    """
    global __on_message__callbacks__
    global __on_message__thread__
    __on_message__callbacks__.append(callBack)

@on_message
def __command_manager__(ctx):
    built_commands = commands.get_commands()
    cmd = ctx.body.split()[0]
    if cmd in built_commands:
        if(isinstance(built_commands[cmd], tuple)): 
            built_commands[cmd][0](built_commands[cmd][1],ctx)
        else:
            built_commands[cmd](ctx)

@on_ready
def __setup__():
    global __on_message__thread__, __on_send_thread__, __recive_thread__

    if(__on_send_callbacks__ != []):
        __on_send_thread__ = threading.Thread(target=__onSend)
        __on_send_thread__.start()

    if(__on_recive_callbacks__ != []):
        __recive_thread__ = threading.Thread(target=__onRecive)
        __recive_thread__.start()

    if(__on_message__callbacks__ != []):
        __on_message__thread__ = threading.Thread(target=__onMessage)
        __on_message__thread__.start()
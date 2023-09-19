from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.remote_connection import LOGGER as selenium_logger
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from typing import Optional, Union, Any
from bs4 import BeautifulSoup
from . import commands
import threading
import platform
import urllib3
import getpass
import logging
import shutil
import emoji
import html
import time
import json
import re
import sys
import os

dir = __file__.replace(f'{os.path.basename(__file__)}','').replace('\\','/')
sys.path.append(dir)

with open(f'{dir}/xpath.json', 'r') as openfile:
    xpath_data = json.load(openfile)

system = platform.uname()
sysinfo = {
"system"    : system.system,
"Node Name" : system.node,
"Release"   : system.release,
"Version"   : system.version,
"Machine"   : system.machine,
"Processor" : system.processor
}

#Public Var
driver : Union[ChromeWebDriver,FirefoxWebDriver]
exit_flag : bool = True

#Private Var
_on_ready_callbacks_ : list = []
_on_send_callbacks_ : list = []
_on_recive_callbacks_ : list = []
_on_message_callbacks_ : list = []
_last_sent_id_ : Union[str,None] = None
_pause_while_sending_ : bool = False
_on_send_thread_ : Union[threading.Thread, None] = None
_on_recive_thread_ : Union[threading.Thread, None] = None
_on_message_thread_ : Union[threading.Thread, None] = None

class run:
    '''
    An unofficial Python wrapper for Whatsapp kindoff
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
        customDriver : Optional[Union[ChromeWebDriver, FirefoxWebDriver]] = None,
        profileDir : str = "Default",
        clean_start : bool = False,
        log : bool = True,
        logFile : bool = False,
        logLevel : int = logging.CRITICAL
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
        if(customDriver != None):
            driver = customDriver

        self.browser = browser
        self.driver = customDriver
        self.headless = headless
        self.profile = profile
        self.profileDir = profileDir
        self.log = log
        self.logFile = logFile
        self.logLevel = logLevel
        self.user = getpass.getuser()
        self.os = sysinfo["system"]
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
            self._clean_start_()

        threading.Thread(target=commands.setup_extension, args=(self.command_classes,), daemon=True).start() #Sets up all the commands inside classes
        self._setup_driver_preference_()
        self._on_ready_()

    def _setup_driver_preference_(self):
        self.browser = self.browser.lower()
        if(self.browser == None and self.driver == None):
            logging.warning("No Browser Defined!")
            raise Exception("No Browser Defined!")

        if(self.browser != "chrome" and self.browser != "firefox" and self.browser != "brave" and self.driver == None):
            logging.warning("UnSupported Browser!")
            raise Exception("Supported Browsers Are Chrome And Firefox")

        if(self.driver == None):
            if(sysinfo["system"] == "Windows"):
                self._initialize_driver_()
                get_link("https://web.whatsapp.com/")
                
            elif(sysinfo["system"] == "Linux"):
                self._initialize_driver_()
                get_link("https://web.whatsapp.com/")

            else:
                raise Exception("UnSupported OS")

        elif(str(type(self.driver)) == "<class 'selenium.webdriver.chrome.webdriver.WebDriver'>"):
            logging.info("Using Custom Driver!")
            self._initialize_driver_()
            get_link("https://web.whatsapp.com/")

        else:
            logging.warning("Invalid Driver!")
            raise Exception("Driver Error! / Invalid Driver!")
        
        _startup_checks_(spawn_qrwindow=self.spawn_qrwindow, terminal_qr=self.terminal_qr).wait_to_load(waitTime=self.waitTime)

    def _initialize_driver_(self):
        global driver

        logging.info(f"Initializing Driver for {self.os},{self.browser},Headless={self.headless}")

        #Driver setup for Windows
        if(self.driver == None and self.os == "Windows" and self.browser == "chrome"):
            chrome_options = Options()
            chrome_options.add_argument(f"user-agent={xpath_data.get('userAgent_Chrome')}")

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
            chrome_options.add_argument(f"user-agent={xpath_data.get('userAgent_Chrome')}")

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
        elif(self.driver == None and self.os == "Windows" and self.browser == "brave"):
            brave_options = Options()
            brave_options.add_argument(f"user-agent={xpath_data.get('userAgent_Chrome')}")

            if(self.profileDir == "Default" and self.profile != "Default"):
                brave_options.add_argument(f"user-data-dir=C:\\Users\\{self.user}\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data")
                brave_options.add_argument(f"profile-directory={self.profile}")

            elif(self.profileDir != "Default"):
                brave_options.add_argument(f"user-data-dir={self.profileDir}")
                brave_options.add_argument(f"profile-directory={self.profile}")

            elif(self.profileDir == "Default" and self.profile == "Default"):
                brave_options.add_argument(f"user-data-dir={dir}/dependences/BraveProfile")
                brave_options.add_argument(f"profile-directory={self.profile}")

            if(self.headless):
                brave_options.add_argument("--start-maximized")
                brave_options.add_argument("--window-size=1920,1080")
                brave_options.add_argument("--headless")
                brave_options.add_argument("--no-sandbox")
                brave_options.add_argument("--disable-gpu")
            brave_options.binary_location = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
            brave_options.add_argument("--disable-extensions")
            brave_options.add_argument("disable-infobars")
            brave_options.add_argument("--log-level=3")
            brave_options.add_argument("--disable-dev-shm-usage")
            brave_options.add_argument("--max-connections=5")
            brave_options.add_argument('--disable-blink-features=AutomationControlled')

            brave_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            brave_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            brave_options.add_experimental_option('useAutomationExtension', False)

            driver = webdriver.Chrome(options=brave_options)
            self.driver = driver

            logging.info("Driver Initialized!")
        else:
            logging.critical("Unsupported Operating system")
            raise Exception("Unsupported Operating system")

    def _clean_start_(self):
        logging.info("Clean Start")
        if(os.path.exists(f"{dir}/dependences/ChromeProfile/Default")):
            try:
                shutil.rmtree(rf"{dir}/dependences/ChromeProfile/Default")
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))

    def _on_ready_(self):
        global _on_ready_callbacks_
        if(self.driver != None):
            for i in _on_ready_callbacks_:
                threading.Thread(target=i).start()

class _startup_checks_:
    def __init__(self, spawn_qrwindow : bool, terminal_qr : bool) -> None:
        self.stop_threads = False
        self.login_check_thread = None
        self.is_loggedin = False
        self.was_loggedout = False
        self._qr_manager_ = None
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
                    if(self._qr_manager_ != None and not self._qr_manager_.stop):
                        self._qr_manager_.quit()

                    self._qr_manager_ = None
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
                    #         driver.find_element(By.XPATH, xpath_data.get('searchBox'))
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
                driver.find_element(By.XPATH, xpath_data.get('searchBox'))
                self.stop_threads = True
                self.is_loggedin = True
                logging.info("Stopping Startup Thread")
                logging.info(f"Is LoggedIn = {self.is_loggedin}")
                break
            except NoSuchElementException:
                try:
                    qr_id = driver.find_element(By.XPATH, '//div[@class="_19vUU"]').get_attribute("data-ref")
                    logging.warning("Not Loggedin!")
                    print("Not Loggedin, Waiting for Whatsapp.web to generate QRCODE")
                    self._qr_manager_ = _qr_manager_(self.spawn_qrwindow, self.terminal_qr)
                    self.is_loggedin = False
                    self.was_loggedout = True
                    self._qr_manager_.start(qr_id=qr_id)
                except NoSuchElementException:
                    time.sleep(0.1)
                    continue

class _qr_manager_:
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
                qr_id = driver.find_element(By.XPATH, '//div[@class="_19vUU"]').get_attribute("data-ref")
            except:
                try:
                    driver.find_element(By.XPATH, '//span[@data-icon="refresh-large"]').click()
                    logging.critical("QR TIMEOUT!")
                    continue
                except:
                    pass
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
            logging.info('Starting _qr_manager_')
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
            logging.info('Starting _qr_manager_')
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
            logging.info('Quitting _qr_manager_')
            self.qrwindow_root.withdraw()
            self.qrwindow_root.quit()

def on_ready(callBack):
    """
    The function `on_ready` adds a callback function to a list of callbacks that will be executed when
    the program is ready.
    
    :param callBack: The `callBack` parameter is a function that will be executed when the `on_ready`
    event occurs
    """
    global _on_ready_callbacks_
    _on_ready_callbacks_.append(callBack)

def get_link(link : str):
    try:
        driver.get(link)
    except WebDriverException:
        logging.critical("DNS ERROR, Webpage Down")
        raise Exception("DNS ERROR, Webpage Down")

def quit():
    global exit_flag
    logging.info("Quitting!")
    exit_flag = False
    driver.quit()

class open_message:
    def __init__(self, contact : str, new: bool = False) -> None:
        """
        This function opens message by phone number/saved name/group name 
        
        :param contact: The `contact` parameter is a string. It could be phone number, saved name or group name
        :type contact: str
        :param new: A boolean parameter that indicates whether the contact is new or not. If you have never sent
        a message to this contact then set new = True, defaults to False
        :type new: bool (optional)
        """
        self.contact = contact
        if(new):
            self._open_new_()
        else:
            self._open_()

    def _open_(self):
        searchBox = driver.find_element(By.XPATH, xpath_data.get('searchBox'))
        searchBox.click()
        searchBox.send_keys(self.contact)
        time.sleep(1)
        try:
            # driver.find_element(By.XPATH, xpath_data.get("searchResult")).click()
            actions = ActionChains(driver=driver) 
            actions.send_keys(Keys.TAB * 2)
            actions.perform()
            WebDriverWait(driver,1).until(EC.presence_of_element_located((By.XPATH, xpath_data.get('chatBox'))))
        except NoSuchElementException:
            raise Exception(f"No chat found for {self.contact}, If you never sent message to this contact use new=True (Use phone number insted of contact name)")
    
    def _open_new_(self):
        get_link(f'https://web.whatsapp.com/send?phone={self.contact}')
        _startup_checks_(spawn_qrwindow=False,terminal_qr=False).wait_to_load(waitTime=0)
        try:
            WebDriverWait(driver,3).until(EC.presence_of_element_located((By.XPATH, xpath_data.get('chatBox'))))
        except:
            if(driver.find_element(By.XPATH, xpath_data.get("invalidPhoneNumber")).text == "Phone number shared via url is invalid."):
                raise Exception("Invalid PhoneNumber")


class send:
    def __init__(self, message : str, waitTillDelivered : bool = False, waitTime : int = 0) -> None:
        '''
        Parameters:
        - message : Message to be sent
        - waitTillDelivered : Waits till message is delivered
        - waitTime : Time in Seconds to wait till message is deliverd, 0 to wait forever (default)
        '''
        self.message = message
        self.waitTillDelivered = waitTillDelivered
        self.waitTime = waitTime
        self.id = None
        self._send_()
    
    def _send_(self):
        global _last_sent_id_
        global _pause_while_sending_
        _pause_while_sending_ = True
        chatBox = driver.find_element(By.XPATH, xpath_data.get('chatBox'))
        chatBox.click()
        message = self.message.splitlines()
        for i in message:
            if(i == ""):
                chatBox.send_keys(Keys.SHIFT + Keys.RETURN) #If \n is at start
            else:
                chatBox.send_keys(i)
                chatBox.send_keys(Keys.SHIFT + Keys.RETURN)
        chatBox.send_keys(Keys.RETURN)
        self.id = driver.find_element(By.XPATH, f"({xpath_data.get('sentMSG')})[last()]").get_attribute("data-id")
        _last_sent_id_ = self.id
        _pause_while_sending_ = False
        if(self.waitTillDelivered):
            self._wait_()

    def _wait_(self):
        while time.time() < time.time() + self.waitTime or self.waitTime == 0:
            try:
                driver.find_element(By.XPATH, f'{xpath_data.get("sentMSG").replace("true",self.id)}{xpath_data.get("msgStatus").replace("PLACEHOLDER", " Pending ")}')
                time.sleep(0.1)
                continue
            except:
                try:
                    driver.find_element(By.XPATH, f'{xpath_data.get("sentMSG").replace("true",self.id)}{xpath_data.get("msgStatus").replace("PLACEHOLDER", " Sent ")}')
                except NoSuchElementException:
                    try:
                        driver.find_element(By.XPATH, f'{xpath_data.get("sentMSG").replace("true",self.id)}{xpath_data.get("msgStatus").replace("PLACEHOLDER", " Read ")}')
                    except NoSuchElementException:
                        driver.find_element(By.XPATH, f'{xpath_data.get("sentMSG").replace("true",self.id)}{xpath_data.get("msgStatus").replace("PLACEHOLDER", " Delivered ")}')
                break

    def __repr__(self) -> str | None:
        return self.id
    
class get_sent:
    def __init__(self) -> None:
        """
        The function gets last sent message and returns `context` id(Message id) and body(Message text).
        """
        self.id = None
        self.body = None
        self._get_sent_()
        pass

    def _get_sent_(self):
        try:
            sent_id = driver.find_element(By.XPATH, f"({xpath_data.get('sentMSG')})[last()]").get_attribute("data-id")
        except (NoSuchElementException, StaleElementReferenceException, AttributeError):
            raise Exception(f"Maybe no chat opend ?! Error!")
            
        if(sent_id != self.id):
            self.id = sent_id
            try:
                self.body = driver.find_element(By.XPATH, f'{xpath_data.get("textByID").replace("PLACEHOLDER",sent_id)}').text
            except (NoSuchElementException, StaleElementReferenceException):
                raise Exception(f"Not a text, Maybe video or sticker or files Error!")
            
    def __repr__(self) -> 'get_sent':
        return self

class wait_to_send:
    def __init__(self, waitTime : int = 0) -> None:
        '''
        Parameters:
        - waitTime : Time in Seconds to wait till message is recived, 0 to wait forever (default)
        '''
        self.id = None
        self.body = None
        self.waitTime = waitTime
        self._wait_()
        pass
    
    def _wait_(self):
        while time.time() < time.time() + self.waitTime or self.waitTime == 0:
            try:
                sent_id = driver.find_element(By.XPATH, f"({xpath_data.get('sentMSG')})[last()]").get_attribute("data-id")
            except (NoSuchElementException, StaleElementReferenceException, AttributeError):
                time.sleep(0.1)
                continue
            if(sent_id != self.id):
                if(self.id == None):
                    self.id = sent_id
                    continue
                self.id = sent_id
                try:
                    self.body = driver.find_element(By.XPATH, f'{xpath_data.get("textByID").replace("PLACEHOLDER",sent_id)}').text
                    break
                except (NoSuchElementException, StaleElementReferenceException):
                    time.sleep(0.1)
                    continue
            time.sleep(0.1)

    def __repr__(self) -> 'wait_to_send':
        return self

class _on_send_:
    def __init__(self) -> None:
        class _repr:
            def __init__(self) -> None:
                self.id : Union[str,None] = None
                self.body : Union[str,None]= None
                pass
        self._repr = _repr
        self._reprRef = _repr()
        self._sent_message_()
        pass

    def _sent_message_(self):
        global _last_sent_id_
        global _pause_while_sending_
        while exit_flag:
            if(_pause_while_sending_): #To ensure message sent by bot is not captured
                time.sleep(0.1)
                continue
            try:
                sent_id = driver.find_element(By.XPATH, f"({xpath_data.get('sentMSG')})[last()]").get_attribute("data-id")
            except (NoSuchElementException, StaleElementReferenceException, AttributeError):
                time.sleep(0.1)
                continue
            if(sent_id != self._reprRef.id and _last_sent_id_ != sent_id):
                if(self._reprRef.id == None):
                    self._reprRef.id = sent_id
                    continue
                self._reprRef.id = sent_id
                try:
                    self._reprRef.body = driver.find_element(By.XPATH, f'{xpath_data.get("textByID").replace("PLACEHOLDER",sent_id)}').text
                    threading.Thread(target=_on_send_callback_fn_, args=(self._reprRef,)).start()
                    self._reprRef = self._repr() #reset _repr to default
                    self._reprRef.id = sent_id
                except (NoSuchElementException, StaleElementReferenceException):
                    time.sleep(0.1)
                    continue
            time.sleep(0.1)

def _on_send_callback_fn_(self):
    global _on_send_callbacks_
    for i in _on_send_callbacks_:
        threading.Thread(target=i, args=(self,)).start()

def on_send(callBack):
    """
    The function `on_send` adds a callback function to a list of callbacks.
    
    :param callBack: The `callBack` parameter is a function that will be executed when the `on_send`
    function is called
    """
    global _on_send_callbacks_
    _on_send_callbacks_.append(callBack)

class get_recived:
    def __init__(self) -> None:
        """
        The function gets last recived message and returns `context` id(Message id) and body(Message text).
        """
        self.id = None
        self.body = None
        self._get_recived_()
        pass

    def _get_recived_(self):
        try:
            recived_id = driver.find_element(By.XPATH, f"({xpath_data.get('recivedMSG')})[last()]").get_attribute("data-id")
        except (NoSuchElementException, StaleElementReferenceException, AttributeError):
            raise Exception(f"Maybe no chat opend ?! Error!")
            
        if(recived_id != self.id):
            self.id = recived_id
            try:
                self.body = driver.find_element(By.XPATH, f'{xpath_data.get("textByID").replace("PLACEHOLDER",recived_id)}').text
            except (NoSuchElementException, StaleElementReferenceException):
                raise Exception(f"Not a text, Maybe video or sticker or files Error!")
            
    def __repr__(self) -> 'get_recived':
        return self
    
class wait_to_recive:
    def __init__(self, waitTime : int = 0) -> None:
        '''
        Parameters:
        - waitTime : Time in Seconds to wait till message is recived, 0 to wait forever (default)
        '''
        self.id = None
        self.body = None
        self.waitTime = waitTime
        self._wait_()
        pass
    
    def _wait_(self):
        while time.time() < time.time() + self.waitTime or self.waitTime == 0:
            try:
                recived_id = driver.find_element(By.XPATH, f"({xpath_data.get('recivedMSG')})[last()]").get_attribute("data-id")
            except (NoSuchElementException, StaleElementReferenceException, AttributeError):
                time.sleep(0.1)
                continue
            if(recived_id != self.id):
                if(self.id == None):
                    self.id = recived_id
                    continue
                self.id = recived_id
                try:
                    self.body = driver.find_element(By.XPATH, f'{xpath_data.get("textByID").replace("PLACEHOLDER",recived_id)}').text
                    break
                except (NoSuchElementException, StaleElementReferenceException):
                    time.sleep(0.1)
                    continue
            time.sleep(0.1)

    def __repr__(self) -> 'wait_to_recive':
        return self

class _on_recive_:
    def __init__(self) -> None:
        class _repr:
            def __init__(self) -> None:
                self.id : Union[str,None] = None
                self.body : Union[str,None] = None
                pass
        self._repr = _repr
        self._reprRef = _repr()
        self._recive_message_()
        pass
    
    def _recive_message_(self):
        while exit_flag:
            try:
                recived_id = driver.find_element(By.XPATH, f"({xpath_data.get('recivedMSG')})[last()]").get_attribute("data-id")
            except (NoSuchElementException, StaleElementReferenceException, AttributeError):
                time.sleep(0.1)
                continue
            if(recived_id != self._reprRef.id):
                if(self._reprRef.id == None):
                    self._reprRef.id = recived_id
                    continue
                self._reprRef.id = recived_id
                try:
                    self._reprRef.body = driver.find_element(By.XPATH, f'{xpath_data.get("textByID").replace("PLACEHOLDER",recived_id)}').text
                    threading.Thread(target=_on_recive_callback_fn_, args=(self._reprRef,)).start()
                    self._reprRef = self._repr() #reset _repr to default
                except (NoSuchElementException, StaleElementReferenceException):
                    time.sleep(0.1)
                    continue
            time.sleep(0.1)

def _on_recive_callback_fn_(self):
    global _on_recive_callbacks_
    for i in _on_recive_callbacks_:
        threading.Thread(target=i, args=(self,)).start()

def on_recive(callBack):
    """
    The function `on_recive` adds a callback function to a list of callbacks.
    
    :param callBack: The `callBack` parameter is a function that will be called when a receive event
    occurs.
    """
    global _on_recive_callbacks_
    global _on_recive_thread_
    _on_recive_callbacks_.append(callBack)

class get_message:
    def __init__(self) -> None:
        """
        The function gets last message (could be sent or recived) and returns `context` id(Message id) and body(Message text).
        """
        self.id = None
        self.body = None
        self._get_message_()
        pass

    def _get_message_(self):
        try:
            message_id = driver.find_element(By.XPATH, f"({xpath_data.get('msg')})[last()]").get_attribute("data-id")
        except (NoSuchElementException, StaleElementReferenceException, AttributeError):
            raise Exception(f"Maybe no chat opend ?! Error!")
            
        if(message_id != self.id):
            self.id = message_id
            try:
                self.body = driver.find_element(By.XPATH, f'{xpath_data.get("textByID").replace("PLACEHOLDER",message_id)}').text
            except (NoSuchElementException, StaleElementReferenceException):
                raise Exception(f"Not a text, Maybe video or sticker or files Error!")
            
    def __repr__(self) -> 'get_message':
        return self

class wait_for_message:
    def __init__(self, waitTime : int = 0) -> None:
        '''
        Parameters:
        - waitTime : Time in Seconds to wait till message is recived, 0 to wait forever (default)
        '''
        self.id = None
        self.body = None
        self.waitTime = waitTime
        self._wait_()
        pass
    
    def _wait_(self):
        while time.time() < time.time() + self.waitTime or self.waitTime == 0:
            try:
                message_id = driver.find_element(By.XPATH, f"({xpath_data.get('msg')})[last()]").get_attribute("data-id")
            except (NoSuchElementException, StaleElementReferenceException, AttributeError):
                time.sleep(0.1)
                continue
            if(message_id != self.id):
                if(self.id == None):
                    self.id = message_id
                    continue
                self.id = message_id
                try:
                    self.body = driver.find_element(By.XPATH, f'{xpath_data.get("textByID").replace("PLACEHOLDER",message_id)}').text
                    break
                except (NoSuchElementException, StaleElementReferenceException):
                    time.sleep(0.1)
                    continue
            time.sleep(0.1)

    def __repr__(self) -> 'wait_for_message':
        return self

class _on_message_:
    def __init__(self) -> None:
        class _repr:
            def __init__(self) -> None:
                self.id : Union[str,None] = None
                self.body : Union[str,None] = None
                pass
        self._repr = _repr
        self._reprRef = _repr()
        self._get_message_()
        pass
    
    def _get_message_(self):
        while exit_flag:
            try:
                message_id = driver.find_element(By.XPATH, f"({xpath_data.get('msg')})[last()]").get_attribute("data-id")
            except (NoSuchElementException, StaleElementReferenceException, AttributeError):
                time.sleep(0.1)
                continue
            if(message_id != self._reprRef.id):
                if(self._reprRef.id == None):
                    self._reprRef.id = message_id
                    continue
                self._reprRef.id = message_id
                try:
                    try:
                        self._reprRef.body = driver.find_element(By.XPATH, f'{xpath_data.get("textByID").replace("PLACEHOLDER",message_id)}')
                        inner_attribute : Any = self._reprRef.body.get_attribute("innerHTML")
                        text = self._reprRef.body.text
                    except:
                        self._reprRef.body = driver.find_elements(By.XPATH, f'{xpath_data.get("emojiTextByID").replace("PLACEHOLDER",message_id)}')
                        inner_attribute = ''
                        if(len(self._reprRef.body) > 1):
                            for elm in self._reprRef.body:
                                print(elm.get_attribute("innerHTML"))
                                inner_attribute += elm.get_attribute("innerHTML")
                            text = ''
                        else:
                            text = self._reprRef.body.text
                    inner_attribute = html.unescape(inner_attribute)
                    print("inner = ", inner_attribute)
                    print("text = ", text)
                    char = ""
                    def is_emoji(s):
                        return emoji.emoji_count(s) > 0
                    index = 0
                    while True:
                        try:
                            str = text[index]
                        except:
                            try:
                                if(inner_attribute[len(text):][0] == "<"):
                                    str = ""
                                else:
                                    break
                            except:
                                break
                        if(inner_attribute[index] != str):
                            emoji_found = False
                            inner_attribute = inner_attribute[index:]
                            for i in range(len(inner_attribute)):
                                if(is_emoji(inner_attribute[i]) and not emoji_found):
                                    char+=inner_attribute[i]
                                    emoji_found = True
                                elif(emoji_found and inner_attribute[i] == ">"):
                                    inner_attribute = text[:index]+inner_attribute[i+1:]
                                    if(index != 0):
                                        char+=str
                                    break
                        else:
                            char += str
                            index += 1
                    self._reprRef.body = char
                    threading.Thread(target=_on_message_callback_fn_, args=(self._reprRef,)).start()
                    self._reprRef = self._repr() #reset _repr to default
                except (NoSuchElementException, StaleElementReferenceException):
                    time.sleep(0.1)
                    continue
            time.sleep(0.1)

def _on_message_callback_fn_(self):
    global _on_message_callbacks_
    for i in _on_message_callbacks_:
        threading.Thread(target=i, args=(self,)).start()

def on_message(callBack):
    """
    The function `on_message` adds a callback function to a list of callbacks.
    
    :param callBack: The `callBack` parameter is a function that will be called whenever a new message
    is received
    """
    global _on_message_callbacks_
    global _on_message_thread_
    _on_message_callbacks_.append(callBack)

def load_extension(extension_path):
    """
    The function `load_extension` loads a Python extension from a specified path.
    
    :param extension_path: The `extension_path` parameter is the path to the file or module that
    contains the code for the extension you want to load. It can be a relative or absolute path
    """
    load_status = commands.load_extension(extension_path=extension_path)
    if(load_status): #To start setup threads which were used in extension
        _setup_threads_()

def unload_extension(extension_name):
    """
    The function unloads a specified extension in Python.
    
    :param extension_name: The parameter "extension_name" is a string that represents the name of the
    extension that you want to unload
    """
    unload_status = commands.unload_extension(extension_name=extension_name)
    if(unload_status): #TODO check and close setup threads which are not in use
        pass

@on_message
def _command_manager_(ctx):
    built_commands = commands.get_commands()
    cmd = ctx.body.split()[0]
    if cmd in built_commands:
        if(isinstance(built_commands[cmd], tuple)): 
            built_commands[cmd][0](built_commands[cmd][1],ctx)
        else:
            built_commands[cmd](ctx)

def _setup_threads_():
    global _on_message_thread_
    global _on_send_thread_
    global _on_recive_thread_

    if(_on_send_callbacks_ != [] and _on_send_thread_ == None):
        _on_send_thread_ = threading.Thread(target=_on_send_)
        _on_send_thread_.start()

    if(_on_recive_callbacks_ != [] and _on_recive_thread_):
        _on_recive_thread_ = threading.Thread(target=_on_recive_)
        _on_recive_thread_.start()

    if(_on_message_callbacks_ != [] and _on_message_thread_ == None):
        _on_message_thread_ = threading.Thread(target=_on_message_)
        _on_message_thread_.start()

@on_ready
def _setup_():
    _setup_threads_()
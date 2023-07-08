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
        spawnQrWindow : bool = True,
        terminalQR : bool = True,
        profile : str = "Default",
        waitTime : int = 0,
        command_classes : list = [],
        customDriver = None,
        profileDir : str = "Default",
        freshStart : bool = False,
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
        :param spawnQrWindow: A boolean value indicating whether to spawn a separate window to display
        the QR code for logging in, defaults to True
        :type spawnQrWindow: bool (optional)
        :param terminalQR: A boolean value indicating whether to display the QR code in the terminal or
        not. If set to True, the QR code will be displayed in the terminal, defaults to True
        :type terminalQR: bool (optional)
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
        :param freshStart: The `freshStart` parameter is a boolean flag that determines whether the
        browser should start with a fresh profile or not. If `freshStart` is set to `True`, the browser
        will start with a new profile, discarding any existing user data, defaults to False
        :type freshStart: bool (optional)
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
        self.spawnQrWindow = spawnQrWindow
        self.terminalQR = terminalQR
        self.waitTime = waitTime
        self.command_classes = command_classes

        if(self.os == "Linux"):
            self.spawnQrWindow = False

        if(log):
            if(logFile):
                logging.basicConfig(filename='Debug.log', format="%(levelno)s:%(asctime)s:%(levelname)s:%(message)s", filemode="w", encoding='utf-8', level=logLevel)
            else:
                logging.basicConfig(format="%(levelno)s:%(asctime)s:%(levelname)s:%(message)s", level=logLevel)

            selenium_logger.setLevel(logging.CRITICAL)
            urllib3_logger = logging.getLogger("urllib3")
            urllib3_logger.setLevel(logging.CRITICAL)

        if(freshStart):
            self.clean()

        threading.Thread(target=commands.setup_extension, args=(self.command_classes,), daemon=True).start()
        self._initializeDriverPreference()
        self.onReady()

    def _initializeDriverPreference(self):
        self.browser = self.browser.lower()
        if(self.browser == None and self.driver == None):
            logging.warning("No Browser Defined!")
            raise Exception("No Browser Defined!")

        if(self.browser != "chrome" and self.browser != "firefox" and self.driver == None):
            logging.warning("UnSupported Browser!")
            raise Exception("Supported Browsers Are Chrome And Firefox")

        if(self.driver == None):
            if(sysinfo["System"] == "Windows"):
                self._initializeDriver()
                getLink("https://web.whatsapp.com/")
                
            elif(sysinfo["System"] == "Linux"):
                self._initializeDriver()
                getLink("https://web.whatsapp.com/")

            else:
                raise Exception("UnSupported OS")

        elif(str(type(self.driver)) == "<class 'selenium.webdriver.chrome.webdriver.WebDriver'>"):
            logging.info("Using Custom Driver!")
            self._initializeDriver()
            getLink("https://web.whatsapp.com/")

        else:
            logging.warning("Invalid Driver!")
            raise Exception("Driver Error! / Invalid Driver!")
        
        startup(spawnQrWindow=self.spawnQrWindow, terminalQR=self.terminalQR).waitToLoad(waitTime=self.waitTime)

    def _initializeDriver(self):
        if(self.driver == None and self.os != None and self.browser != None):
            logging.info(f"Initializing Driver for {self.os},{self.browser},Headless={self.headless}")
            self._defaultDriver()

    def _defaultDriver(self):
        global driver

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
            # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
            self.driver = driver

            logging.info("Driver Initialized!")
        
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

    def clean(self):
        logging.info("Fresh start!")
        if(os.path.exists(f"{dir}/dependences/ChromeProfile/Default")):
            try:
                shutil.rmtree(rf"{dir}/dependences/ChromeProfile/Default")
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))

    def onReady(self):
        global _onReadyCallBackFN
        if(self.driver != None):
            _onReadyCallBackFN()

class startup:
    def __init__(self, spawnQrWindow : bool, terminalQR : bool) -> None:
        self.stopThreads = False
        self.checkLoginThread = None
        self.isLoggedin = False
        self.wasLoggedOut = False
        self.QRWindow = None
        self.spawnQrWindow = spawnQrWindow
        self.terminalQR = terminalQR
        pass

    def waitToLoad(self, waitTime : int):

        self.checkLoginThread = threading.Thread(target=self.checkLogin, daemon=True)
        self.checkLoginThread.start()
        logging.info(f"CheckLogin Thread Started!, is_Alive? = {self.checkLoginThread.is_alive()}")

        t = time.time() + waitTime
        while time.time() < t or waitTime == 0:
            if(self.stopThreads):
                if(self.wasLoggedOut):
                    if(self.QRWindow != None and not self.QRWindow.stop):
                        self.QRWindow.quit()

                    self.QRWindow = None
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
                    #         logging.info(f"Is LoggedIn = {self.isLoggedin}")
                    #         break
                    #     except NoSuchElementException:
                    #         time.sleep(0.1)
                    #         continue
                    # break
                else:
                    break
            time.sleep(0.5)
        else:
            self.stopThreads = True
            logging.info("Stopping Startup Threads")
            logging.warning("Session Time Expired!,(Login Error ?)")
            quit()
            raise Exception("Session Time Expired!,(Login Error ?)")


    def checkLogin(self):
        while True:
            if(self.stopThreads == True):
                logging.info("CheckLogin Thread Stopped!")
                break

            try:
                driver.find_element(By.XPATH, xpathData.get('searchBox'))
                self.stopThreads = True
                self.isLoggedin = True
                logging.info("Stopping Startup Thread")
                logging.info(f"Is LoggedIn = {self.isLoggedin}")
                break
            except NoSuchElementException:
                try:
                    qrID = driver.find_element(By.XPATH, '//div[@data-testid="qrcode"]').get_attribute("data-ref")
                    logging.warning("Not Loggedin!")
                    print("Not Loggedin, Waiting for Whatsapp.web to generate QRCODE")
                    self.QRWindow = QRWindow(self.spawnQrWindow, self.terminalQR)
                    self.isLoggedin = False
                    self.wasLoggedOut = True
                    self.QRWindow.start(qrID=qrID)
                except NoSuchElementException:
                    time.sleep(0.1)
                    continue

class QRWindow:
    def __init__(self, spawnQrWindow : bool, terminalQR : bool):
        self.__qrcode = __import__("qrcode")
        self.stop = False
        self.spawnQrWindow = spawnQrWindow
        self.terminalQR = terminalQR
        if(spawnQrWindow):
            from PIL import Image, ImageTk
            self.__tk = __import__("tkinter")
            self.__Image = Image
            self.__ImageTK = ImageTk
            self.qrWindowREF = self.__tk.Tk()

            if sys.platform.startswith("win"):
                self.qrWindowREF.wm_attributes("-topmost", 1)
            elif sys.platform.startswith("darwin"):
                self.qrWindowREF.createcommand('tk::mac::ReopenApplication',
                                lambda: self.qrWindowREF.event_generate('<<ReopenApplication>>'))
                self.qrWindowREF.createcommand('tk::mac::Preferences',
                                lambda: self.qrWindowREF.event_generate('<<Preferences>>'))
                self.qrWindowREF.createcommand('tk::mac::Quit',
                                lambda: self.qrWindowREF.event_generate('<<Quit>>'))
                self.qrWindowREF.createcommand('::tk::mac::ShowPreferences',
                                lambda: self.qrWindowREF.event_generate('<<ShowPreferences>>'))
                self.qrWindowREF.createcommand('::tk::mac::ShowHelp',
                                lambda: self.qrWindowREF.event_generate('<<ShowHelp>>'))
                self.qrWindowREF.createcommand('::tk::mac::Hide',
                                lambda: self.qrWindowREF.event_generate('<<Hide>>'))
            else:
                # Linux (requires external libraries like python-xlib)
                self.qrWindowREF.wm_attributes("-topmost", 1)

            self.qrWindowREF.overrideredirect(True)
            self.qrWindowREF.attributes("-toolwindow", 1)
            self.qrWindowREF.protocol("WM_DELETE_WINDOW", lambda: None)

            self.filename = "qrcode.png"
            self.label = None

    def create_qr_image(self):
        try:
            image = self.__Image.open(self.filename)
            image = image.resize((300, 300))
            photo = self.__ImageTK.PhotoImage(image)

            if self.label is not None:
                self.label.configure(image=photo)
                self.label.image = photo  # Keep a reference to avoid garbage collection
            else:
                self.label = self.__tk.Label(self.qrWindowREF, image=photo)
                self.label.image = photo  # Keep a reference to avoid garbage collection
                self.label.pack()
        except:
            pass

        if(not self.stop):
            self.qrWindowREF.after(1000, self.create_qr_image)

    def createTerminalQR(self,data, update:bool):
        qr = self.__qrcode.QRCode(
            version=1,
            error_correction=self.__qrcode.constants.ERROR_CORRECT_L,
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

    def updateQR(self, qrID):
        lqrID = qrID
        if(self.spawnQrWindow == False and self.terminalQR == False):
            return
        while not self.stop:
            try:
                qrID = driver.find_element(By.XPATH, '//div[@data-testid="qrcode"]').get_attribute("data-ref")
            except:
                self.quit()
                break
            if(lqrID != qrID):
                if(self.spawnQrWindow):
                    qr = self.__qrcode.QRCode()
                    qr.add_data(qrID)
                    qr.make_image().save(self.filename)

                if(self.terminalQR):
                    self.createTerminalQR(qrID,True)

                lqrID = qrID
            time.sleep(0.5)
        return

    def start(self, qrID):
        if(self.spawnQrWindow == True and self.terminalQR == True):
            qr = self.__qrcode.QRCode()
            qr.add_data(qrID)
            qr.make_image().save(self.filename)
            self.create_qr_image()
            logging.info('Starting QRWindow')
            threading.Thread(target = self.createTerminalQR, args=(qrID,False)).start()
            threading.Thread(target=self.updateQR, args=(qrID,)).start()
            self.qrWindowREF.mainloop()

        elif(self.terminalQR == True and self.spawnQrWindow == False):
            threading.Thread(target = self.createTerminalQR, args=(qrID,False)).start()
            self.updateQR(qrID)

        elif(self.spawnQrWindow == True and self.terminalQR == False):
            qr = self.__qrcode.QRCode()
            qr.add_data(qrID)
            qr.make_image().save(self.filename)
            logging.info('Starting QRWindow')
            threading.Thread(target=self.updateQR, args=(qrID,)).start()
            self.qrWindowREF.mainloop()
    
    def quit(self):
        self.stop = True
        if(self.terminalQR):
            sys.stdout.write("\033[27A")
            for _ in range(27):
                print(" " * 55)
            sys.stdout.write("\033[27A\n")
        print("Cleaning UP")
        if(self.spawnQrWindow):
            logging.info('Quitting QRWindow')
            self.qrWindowREF.withdraw()
            self.qrWindowREF.quit()

__onReadyCallBacks = []
def onReady(callBack):
    global __onReadyCallBacks
    __onReadyCallBacks.append(callBack)

def _onReadyCallBackFN():
    global __onReadyCallBacks
    for i in __onReadyCallBacks:
        threading.Thread(target=i).start()

def getLink(link : str):
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
        getLink(f'https://web.whatsapp.com/send?phone={self.__contact}')
        startup(spawnQrWindow=False,terminalQR=False).waitToLoad(waitTime=0)
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

__onSendCallBacks = []
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
                    threading.Thread(target=_onSendCallBackFN, args=(self,)).start()
                except (NoSuchElementException, StaleElementReferenceException):
                    time.sleep(0.1)
                    continue
            time.sleep(0.1)

def _onSendCallBackFN(self):
    global __onSendCallBacks
    for i in __onSendCallBacks:
        threading.Thread(target=i, args=(self,)).start()

__onSendThread = None
def onSend(callBack):
    global __onSendCallBacks
    global __onSendThread
    __onSendCallBacks.append(callBack)

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
                    threading.Thread(target=_onReciveCallBackFN, args=(self,)).start()
                except (NoSuchElementException, StaleElementReferenceException):
                    time.sleep(0.1)
                    continue
            time.sleep(0.1)

def _onReciveCallBackFN(self):
    global __onReciveCallBacks
    for i in __onReciveCallBacks:
        threading.Thread(target=i, args=(self,)).start()

__onReciveCallBacks = []
__reciveThread = None
def onRecive(callBack):
    global __onReciveCallBacks
    global __reciveThread
    __onReciveCallBacks.append(callBack)

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
                    threading.Thread(target=_onMsgCallBackFN, args=(self,)).start()
                except (NoSuchElementException, StaleElementReferenceException):
                    time.sleep(0.1)
                    continue
            time.sleep(0.1)

def _onMsgCallBackFN(self):
    global __onMsgCallBacks
    for i in __onMsgCallBacks:
        threading.Thread(target=i, args=(self,)).start()

__onMsgCallBacks = []
__msgThread = None
def onMessage(callBack):
    global __onMsgCallBacks
    global __msgThread
    __onMsgCallBacks.append(callBack)

@onMessage
def __command_manager__(ctx):
    built_commands = commands.get_commands()
    cmd = ctx.body.split()[0]
    if cmd in built_commands:
        if(isinstance(built_commands[cmd], tuple)): 
            built_commands[cmd][0](built_commands[cmd][1],ctx)
        else:
            built_commands[cmd](ctx)

@onReady
def __setup__():
    global __msgThread, __onSendThread, __reciveThread

    if(__onSendCallBacks != []):
        __onSendThread = threading.Thread(target=__onSend)
        __onSendThread.start()

    if(__onReciveCallBacks != []):
        __reciveThread = threading.Thread(target=__onRecive)
        __reciveThread.start()

    if(__onMsgCallBacks != []):
        __msgThread = threading.Thread(target=__onMessage)
        __msgThread.start()
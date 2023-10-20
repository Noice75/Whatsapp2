import json
import os

data = {
    "chatBox" : '//div[@role="textbox" and @title="Type a message"]',
    "searchBox" : '//div[@role="textbox" and @title="Search input textbox"]',
    "userAgent_Chrome" : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    "sentMSG" : '//div[contains(@data-id, "true")]',
    "recivedMSG" : '//div[contains(@data-id, "false")]',
    "msg" : '//div[contains(@data-id, "e_")]',
    "textByID" : '(//div[@data-id="PLACEHOLDER"]//span//span)[1]',
    "getMention" : '//div[@data-id="PLACEHOLDER"]//span[@role="button"]//span[@class="ajgl1lbb o0rubyzf _11JPr selectable-text select-all copyable-text"]',
    "emojiTextByID" : '(//div[@data-id="PLACEHOLDER"]//span[@class="Ov-s3"])',
    "msgStatus" : '//span[@aria-label="PLACEHOLDER"]',
    "searchResult" : '//div[@style[contains(.,"height: 72px; transform: translateY(72px);")]]',
    "cancelsearch" : '//button[@aria-label="Cancel search"]',
    "invalidPhoneNumber" : '//div[@data-testid="popup-contents"]'
}
dir = __file__.replace(f'{os.path.basename(__file__)}','').replace('\\','/')
json_object = json.dumps(data, indent = 4)
with open(f"{dir}/xpath.json", "w") as outfile:
    outfile.write(json_object)
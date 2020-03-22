import discord
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime

hw_dic = {}

def crawling() :
    path = '/Users/woung/Downloads/chromedriver.exe'
    homepage = 'http://www.gsm.hs.kr/xboard/board.php?&tbnum=14&sCat=0&page=5&keyset=&searchword=&page=1'

    #드라이버 옵션 설정 - headless
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument('disable-gpu')
    options.add_argument('lang=ko_KR')
    driver = webdriver.Chrome(r'C:\Users\woung\Downloads\chromedriver.exe',chrome_options=options)

    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})") # 드라이버 언어설정
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})") #플러그인 개수 변경



    #과제 이름, 일자 크롤링   -> 전문교과, 과제 내용까지
    
    for major in range(2):
        if major == 1:
            homepage = "http://www.gsm.hs.kr/xboard/board.php?tbnum=15"
        #홈페이지 이동
        driver.get(homepage)
        driver.implicitly_wait(3)
        for pageCnt in range(3):

            req = driver.page_source
            soup = BeautifulSoup(req,'html.parser')
            

            
            hwlist = soup.select('.left')
            content = []
            for i in hwlist:
                content.append(i.text.replace(u"\xa0",u" "))

            #날짜 
            hwdate = soup.select('tr > td')
            date = []
            del hwdate[0:3]
            cnt = 0
            for j in hwdate:
                if cnt == 0:
                    cnt = 5
                    date.append(j.text) 
                else:
                    cnt-=1

            for key,value in zip(content,date):
                hw_dic[key] = value
            driver.find_elements_by_xpath("//a[@class='page_num']")[pageCnt].click()
    driver.quit()

crawling()

#브라우저 닫기
#driver.close() -> 단순 웹브라우저 닫기
#driver.quit() -> web session까지 삭제
# 요소 return - 단수 : find_element_*(),    복수 : find_elements_*()   ex) find_element_by_id()
#                                                                         find_element_by_class_name()


#discord bot
client = discord.Client()
token = 'Njg1MDEzMTQzOTQ4MDk5NTkz.XmCwhQ.RuXlqYuS7_nZ8u9aCaQNrhTsaIY'

@client.event
async def on_ready():
    print(client.user.id)
    print("ready")
    game = discord.Game("오늘 완성 가능?")
    await client.change_presence(status=discord.Status.online, activity=game)

@client.event
async def on_message(message):
    if message.author == client.user:  # 여기서 client.user은 봇 자신
        return

    if "homework" in message.content:
        #학년별로 나누기
        msg = (message.content).split()
        grade = msg[1]
        grade = grade+"학년"

        resultDic = {}
            
        for text,day in hw_dic.items():
            if grade in text:
                resultDic[text] = day
        
        #일자별로 나누기
        keyword = int(msg[2])

        today = datetime.now()
        result = []
        for content, day in resultDic.items():
            day = datetime.strptime(day,'%Y/%m/%d')
            if (today-day).days <= keyword:
                result.append(content)
        outcome = '```'
        for i in result:
            outcome = outcome + '-' + i+'\n'
        outcome = outcome + '```'
        try :
            await message.channel.send("Your Homework is......\n"+outcome)
        except discord.errors.HTTPException :
            print(result)
        return

    if message.content == "!help":
        await message.channel.send("homework [학년] [몇일전까지의 데이터를 뽑기위한 일 수]")
    

client.run(token)
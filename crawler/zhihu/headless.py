from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# 设置Chrome选项
chrome_options = Options()
# chrome_options.add_argument("--headless")  # 无头模式
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")

# 初始化WebDriver
driver = webdriver.Chrome(options=chrome_options)

# 打开网页
url = "https://www.zhihu.com/question/663061453"
driver.get(url)

# 等待并点击"查看全部"链接
try:
    view_all_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a.QuestionMainAction.ViewAll-QuestionMainAction"))
    )
    view_all_link.click()
except TimeoutException:
    print("未找到'查看全部'链接或等待超时")

# 函数：获取新出现的文本
def get_new_text(last_height):
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height != last_height:
        # 获取页面文本
        text = driver.find_element(By.CSS_SELECTOR, ".Question-mainColumn").text
        print(text)  # 或者将文本保存到文件
    return new_height

# 持续下拉页面并获取新文本
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    # 滚动到页面底部
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    # 等待页面加载
    time.sleep(2)
    
    # 获取新文本
    new_height = get_new_text(last_height)
    
    # 如果页面高度没有变化，说明已经到达底部，退出循环
    if new_height == last_height:
        break
    last_height = new_height

# 关闭浏览器
driver.quit()
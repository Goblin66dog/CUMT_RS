# parse_poem.py
import requests
from bs4 import BeautifulSoup
import time

#函数1：请求网页
def page_request(url, ua):
    response = requests.get(url, headers=ua)
    html = response.content.decode("utf-8")
    return html

# 函数2：解析网页
def page_parse(html):
    soup = BeautifulSoup(html, "lxml")
    title = soup("title")
    sentence = soup.select("div.left > div.sons > div.cont > a:nth-of-type(1)")
    poet = soup.select("div.left > div.sons > div.cont > a:nth-of-type(2)")
    sentence_list = []
    href_list = []
    for i in range(len(sentence)):
        temp = sentence[i].get_text() + "---" + poet[i].get_text()
        sentence_list.append(temp)
        href = sentence[i].get("href")
        href_list.append("https://so.gushiwen.org" + href)
    return [href_list, sentence_list] # 注意这里的缩进


#函数3：写入文本文件
def save_txt(info_list):
    import json
    with open(r'Python_Programming&RS_Image_Processing_2\sentence.txt', 'a', encoding='utf-8') as txt_file:
        for element in info_list[1]:
            txt_file.write(json.dumps(element, ensure_ascii=False) + "\n\n")

# 子网页处理函数：进入并解析子网页/请求子网页
def sub_page_request(info_list):
    subpage_urls = info_list[0]
    ua = {'User-Agent':'Mozilla/5.0(Windows NT 6.1;WOW64)AppleWebKit/537.36(KHTML, like Gecko) Chrome/46.0.2490.86Safari/537.36'}
    sub_html = []
    for url in subpage_urls:
        html = page_request(url, ua)
        sub_html.append(html)
    return sub_html # 注意这里的缩进

# 子网页处理函数：解析子网页，爬取诗句内容
def sub_page_parse(sub_html):
    poem_list = []
    for html in sub_html:
        soup = BeautifulSoup(html, 'lxml')
        # poem = soup.select('div.left > div.sons > div.cont > div.contson')
        poem = soup.select('div.contson')
        poem = poem[1].get_text()
        poem_list.append(poem.strip())
    return poem_list

# 子网页处理函数：保存诗句到txt
def sub_page_save(poem_list):
    import json
    with open(r"Python_Programming&RS_Image_Processing_2\poems.txt", "a", encoding='utf-8') as txt_file:
        for elements in poem_list:
            txt_file.write(json.dumps(elements, ensure_ascii=False) + '\n\n')

if __name__ == '__main__':
    print("**********************start**********************")
    ua = {'User-Agent':'Mozilla/5.0(Windows NT 6.1;WOW64)AppleWebKit/537.36(KHTML, like Gecko) Chrome/46.0.2490.86Safari/537.36'}
    for i in range(1,4):
        url = 'https://so.gushiwen.cn/mingjus/default.aspx?page='+str(i)+'&tstr=%e6%98%a5%e5%a4%a9&astr=&cstr=&xstr='
        time.sleep(1)
        html = page_request(url, ua)
        info_list = page_parse(html)
        save_txt(info_list)
        # 处理子网页
        print("开始解析第%d"%(i) + "页")
        # 开始解析名句子网页
        sub_html = sub_page_request(info_list)
        poem_list = sub_page_parse(sub_html)
        sub_page_save(poem_list)
    print("**********************finished**********************")
    print("共爬取%d"%(i*50) + "个古诗词名句，保存在如下路径：Python_Programming&RS_Image_Processing_2\sentence.txt")
    print("共爬取%d" % (i * 50) + "个古诗词，保存在如下路径：Python_Programming&RS_Image_Processing_2\poem.txt")
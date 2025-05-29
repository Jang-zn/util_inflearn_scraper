import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# .env 파일에서 환경 변수 로드
load_dotenv()

# --- 설정 변수 ( .env 파일에서 불러오기) --- #
INFLEARN_EMAIL = os.getenv("INFLEARN_EMAIL")
INFLEARN_PASSWORD = os.getenv("INFLEARN_PASSWORD")
DEFAULT_OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_lecture_scripts") # 기본값 설정
DEFAULT_BASE_FILENAME = os.getenv("BASE_FILENAME", "lecture_script") # 기본값 설정

def get_chrome_driver():
    """Chrome WebDriver 인스턴스를 생성하고 반환합니다."""
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # 필요 시 주석 해제
    chrome_options.add_argument("--start-maximized")
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        return driver
    except Exception as e:
        print(f"WebDriver 생성 중 오류 발생: {e}")
        return None

if __name__ == '__main__':
    # 테스트용 코드
    if not INFLEARN_EMAIL or not INFLEARN_PASSWORD:
        print("오류: .env 파일에 INFLEARN_EMAIL 또는 INFLEARN_PASSWORD가 설정되지 않았습니다.")
        print(".env.sample 파일을 참고하여 .env 파일을 설정해주세요.")
    else:
        print("환경 변수 로드 성공:")
        print(f"  INFLEARN_EMAIL: {INFLEARN_EMAIL[:3]}***") # 민감 정보 일부 마스킹
        print(f"  DEFAULT_OUTPUT_DIR: {DEFAULT_OUTPUT_DIR}")
        print(f"  DEFAULT_BASE_FILENAME: {DEFAULT_BASE_FILENAME}")

    # driver = get_chrome_driver()
    # if driver:
    #     print("WebDriver 생성 성공")
    #     driver.get("https://www.google.com")
    #     time.sleep(2)
    #     driver.quit()
    # else:
    #     print("WebDriver 생성 실패") 
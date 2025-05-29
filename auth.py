from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def login_to_inflearn(driver, email, password):
    """인프런에 로그인합니다."""
    print("\n인프런 메인 페이지로 이동 중...")
    driver.get("https://www.inflearn.com/")
    print(f"현재 URL: {driver.current_url}")

    print("로그인 버튼 대기 중...")
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.mantine-UnstyledButton-root.mantine-Button-root.css-1uibevq.mantine-193n4qw"))
    )
    print("로그인 버튼 클릭.")
    login_button.click()
    print("로그인 모달창 로딩 대기 중...")
    time.sleep(1) # 모달창이 나타나는 시간 대기

    print("로그인 폼 필드 대기 중 (이메일)...")
    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "email"))
    )
    password_field = driver.find_element(By.ID, "password")

    print("이메일 및 비밀번호 입력.")
    email_field.send_keys(email)
    password_field.send_keys(password)

    print("로그인 제출 버튼 대기 중...")
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.mantine-UnstyledButton-root.mantine-Button-root.mantine-1bt2sfd"))
    )
    print("로그인 제출 버튼 클릭.")
    submit_button.click()

    print("로그인 처리 후 4초 대기 중...")
    time.sleep(4)
    print(f"로그인 후 현재 URL: {driver.current_url}")
    
    # 로그인 성공 여부 확인 (예: 특정 요소가 나타나는지 확인)
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img[alt='profile']")) # 프로필 이미지가 보이면 로그인 성공으로 간주
        )
        print("로그인 성공 확인.")
        return True
    except:
        print("오류: 로그인 실패 또는 프로필 이미지를 찾을 수 없습니다.")
        # 현재 URL이 로그인 페이지거나 에러 메시지가 있는지 등으로 더 정확한 확인 가능
        if "login" in driver.current_url or "signin" in driver.current_url:
             print("로그인 페이지에 머물러 있습니다. 아이디/비밀번호를 확인하세요.")
        return False

if __name__ == '__main__':
    # 이 모듈을 직접 실행할 때 테스트하는 방법:
    # 1. config.py에서 get_chrome_driver와 환경 변수를 가져옵니다.
    # 2. get_chrome_driver를 호출하여 driver 인스턴스를 얻습니다.
    # 3. login_to_inflearn 함수를 테스트합니다.
    
    # 주의: 아래 코드는 config.py가 동일 폴더에 있고 .env 파일이 올바르게 설정되어 있다고 가정합니다.
    import sys
    import os
    # 현재 파일의 디렉토리를 sys.path에 추가하여 config 모듈을 찾을 수 있도록 함
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    try:
        from config import get_chrome_driver, INFLEARN_EMAIL, INFLEARN_PASSWORD
    except ImportError:
        print("Error: config.py를 찾을 수 없거나 필요한 변수를 임포트할 수 없습니다.")
        print("auth.py와 동일한 디렉토리에 config.py가 있는지, .env 파일이 설정되었는지 확인하세요.")
        sys.exit(1)

    if not INFLEARN_EMAIL or not INFLEARN_PASSWORD:
        print("오류: .env 파일에 INFLEARN_EMAIL 또는 INFLEARN_PASSWORD가 설정되지 않았습니다.")
    else:
        print("테스트: 인프런 로그인")
        test_driver = get_chrome_driver()
        if test_driver:
            success = login_to_inflearn(test_driver, INFLEARN_EMAIL, INFLEARN_PASSWORD)
            if success:
                print("테스트 로그인 성공!")
                # 여기서 추가적인 작업 (예: 스크린샷 찍기, 특정 페이지 이동 등) 가능
                time.sleep(3)
            else:
                print("테스트 로그인 실패.")
            test_driver.quit()
            print("테스트 드라이버 종료.")
        else:
            print("테스트 드라이버 생성 실패.") 
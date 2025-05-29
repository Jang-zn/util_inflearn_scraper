from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def navigate_to_my_courses(driver):
    """내 강의 페이지로 이동합니다."""
    print("내 강의 페이지로 이동 중...")
    driver.get("https://www.inflearn.com/my/courses")
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body")) # 페이지 로딩의 기본 확인
        )
        # 여기에 '내 학습'과 같은 특정 텍스트나 요소가 나타나는지 확인하는 로직 추가 권장
        # 예: WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(text(),'내 학습')]")))
        print("내 강의 페이지 로딩 완료.")
        print(f"내 강의 페이지 URL: {driver.current_url}")
        return True
    except Exception as e:
        print(f"내 강의 페이지 이동 또는 로딩 실패: {e}")
        return False

def select_course(driver, course_name):
    """강의 목록에서 특정 강의를 선택합니다. (구현 필요)
    강의 이름(course_name)을 받아, 해당 강의 페이지로 이동해야 합니다.
    """
    print(f"'{course_name}' 강의 선택 로직 구현 필요...")
    # TODO: 내 강의 페이지에서 course_name을 포함하는 링크나 버튼을 찾아 클릭
    # 예시:
    # course_link_xpath = f"//a[contains(., '{course_name}')]" # 강의 제목을 포함하는 a 태그
    # course_card_xpath = f"//div[contains(@class, 'course_card_title') and contains(text(), '{course_name}')]/ancestor::a"
    # try:
    #     course_element = WebDriverWait(driver, 10).until(
    #         EC.element_to_be_clickable((By.XPATH, course_card_xpath))
    #     )
    #     print(f"'{course_name}' 강의를 찾았습니다. 클릭합니다.")
    #     course_element.click()
    #     time.sleep(3) # 페이지 이동 대기
    #     print(f"'{course_name}' 강의 페이지로 이동 완료. 현재 URL: {driver.current_url}")
    #     return True
    # except Exception as e:
    #     print(f"'{course_name}' 강의를 찾거나 클릭하는 중 오류: {e}")
    #     return False
    pass

def select_chapter(driver, chapter_name=None):
    """강의 내에서 특정 챕터(섹션의 첫 번째 강의)를 선택합니다. (구현 필요)
    chapter_name이 주어지면 해당 챕터로, None이면 첫 번째 챕터로 이동합니다.
    """
    print(f"챕터 선택 로직 구현 필요 (선택된 챕터: {chapter_name if chapter_name else '첫 번째 챕터'})...")
    # TODO: 현재 강의 페이지의 목차에서 챕터(또는 첫 번째 강의)를 찾아 클릭
    # 예시 (첫번째 챕터의 첫번째 강의 클릭):
    # first_lesson_in_toc_xpath = "//ul[contains(@class, 'toc-container')]//li[contains(@class, 'toc-item')][1]//a"
    # try:
    #     chapter_element = WebDriverWait(driver, 10).until(
    #         EC.element_to_be_clickable((By.XPATH, first_lesson_in_toc_xpath))
    #     )
    #     print(f"{'첫 번째' if not chapter_name else chapter_name} 챕터(의 첫 강의)를 클릭합니다.")
    #     chapter_element.click()
    #     time.sleep(3) # 강의 로딩 대기
    #     return True
    # except Exception as e:
    #     print(f"챕터 선택 중 오류: {e}")
    #     return False
    pass

def open_script_tab(driver):
    """현재 강의 화면에서 스크립트 탭을 엽니다. (구현 필요)"""
    print("스크립트 탭 열기 로직 구현 필요...")
    # TODO: 스크립트 탭으로 전환하는 버튼 클릭
    # 예시: (스크립트 탭 버튼의 CSS 선택자나 XPATH를 찾아야 함)
    # script_tab_button_selector = "button[data-gtm-id='lecture-tab-script']" # 실제 선택자는 다를 수 있음
    # try:
    #     script_button = WebDriverWait(driver, 10).until(
    #         EC.element_to_be_clickable((By.CSS_SELECTOR, script_tab_button_selector))
    #     )
    #     print("스크립트 탭 버튼을 클릭합니다.")
    #     script_button.click()
    #     time.sleep(2) # 스크립트 내용 로드 대기
    #     print("스크립트 탭이 열렸습니다.")
    #     return True
    # except Exception as e:
    #     print(f"스크립트 탭을 여는 중 오류: {e}")
    #     return False
    pass

def go_to_next_chapter(driver):
    """다음 챕터(섹션의 다음 강의)로 이동합니다. (구현 필요)
    모든 챕터를 순회한 경우 False를 반환해야 합니다.
    """
    print("다음 챕터로 이동 로직 구현 필요...")
    # TODO: 현재 활성화된 챕터/강의를 기준으로 다음 항목을 찾아 클릭
    # 또는 '다음 강의' 버튼이 있다면 그것을 활용
    # 예시:
    # next_button_selector = ".next-button-selector" # 실제 '다음 강의' 버튼 선택자
    # try:
    #     next_button = driver.find_element(By.CSS_SELECTOR, next_button_selector)
    #     if next_button.is_displayed() and next_button.is_enabled():
    #         print("다음 강의 버튼을 클릭합니다.")
    #         next_button.click()
    #         time.sleep(3) # 다음 강의 로드 대기
    #         return True # 다음 챕터(강의)로 성공적으로 이동
    #     else:
    #         print("다음 강의 버튼을 찾았으나 비활성화 또는 숨겨져 있습니다. 마지막 챕터일 수 있습니다.")
    #         return False # 더 이상 다음 챕터(강의) 없음
    # except NoSuchElementException:
    #     print("다음 강의 버튼을 찾을 수 없습니다. 마지막 챕터일 수 있습니다.")
    #     return False # 버튼 없음, 마지막 챕터로 간주
    # except Exception as e:
    #     print(f"다음 챕터로 이동 중 오류: {e}")
    #     return False # 오류 발생 시
    return False # 임시로 항상 False 반환 (모든 챕터 완료된 것으로 처리)

if __name__ == '__main__':
    # 이 모듈을 테스트하려면 config.py, auth.py 등이 필요합니다.
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    try:
        from config import get_chrome_driver, INFLEARN_EMAIL, INFLEARN_PASSWORD
        from auth import login_to_inflearn
    except ImportError:
        print("Error: config.py 또는 auth.py를 찾을 수 없습니다.")
        sys.exit(1)

    if not INFLEARN_EMAIL or not INFLEARN_PASSWORD:
        print("오류: .env 파일의 환경 변수가 설정되지 않았습니다.")
    else:
        test_driver = get_chrome_driver()
        if test_driver:
            if login_to_inflearn(test_driver, INFLEARN_EMAIL, INFLEARN_PASSWORD):
                print("\n--- 내비게이션 테스트 시작 ---")
                
                # 1. 내 강의실 이동 테스트
                if navigate_to_my_courses(test_driver):
                    print("내 강의실 이동 성공.")
                    time.sleep(2)

                    # 여기에 아래 함수들의 테스트 호출을 추가할 수 있습니다.
                    # 실제 테스트를 위해서는 course_name 등을 알아야 합니다.
                    # select_course(test_driver, "여기에_실제_강의명_입력")
                    # select_chapter(test_driver) 
                    # open_script_tab(test_driver)
                    # go_to_next_chapter(test_driver)
                else:
                    print("내 강의실 이동 실패.")

            else:
                print("로그인 실패로 내비게이션 테스트를 진행할 수 없습니다.")
            test_driver.quit()
            print("\n테스트 드라이버 종료.")
        else:
            print("테스트 드라이버 생성 실패.") 
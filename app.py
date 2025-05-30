import time
import traceback

# 모듈 임포트
from config import get_chrome_driver, DEFAULT_OUTPUT_DIR # .env에서 기본 출력 폴더 가져오기
from ui import launch_ui 
from auth import login_to_inflearn
from navigation import (
    navigate_to_my_courses, 
    select_course, 
    open_curriculum_tab, 
    select_first_available_lesson,
    open_script_tab, 
    go_to_next_chapter
)
from scraper import extract_scripts_from_current_page
# file_utils에서 필요한 함수들 명시적으로 임포트
from file_utils import (
    sanitize_filename, 
    setup_lecture_directory, 
    get_section_filepath,
    get_total_filepath, 
    save_markdown_file
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def execute_scraping_workflow(user_configs):
    """UI로부터 설정값을 받아 스크래핑 전체 과정을 수행합니다."""
    print("\n--- 스크래핑 워크플로우 시작 ---")
    
    email = user_configs.get("email")
    password = user_configs.get("password")
    # output_dir_ui = user_configs.get("output_dir") # UI에서 제거됨
    # base_filename_ui = user_configs.get("base_filename") # UI에서 제거됨
    course_name_ui = user_configs.get("course_name")

    # 필수값 확인
    if not all([email, password, course_name_ui]):
        print("오류: 필수 설정값이 누락되었습니다. (이메일, 비밀번호, 강의명)")
        return

    # 기본 최상위 출력 디렉토리 사용
    base_output_dir = DEFAULT_OUTPUT_DIR 

    print("\n--- 실행 설정 정보 ---")
    print(f"이메일: {email[:3]}***")
    print(f"타겟 강의명: {course_name_ui}")
    print(f"기본 저장 경로: {base_output_dir}")

    # 강의명 정제 (폴더 및 파일명용)
    sanitized_course_name = sanitize_filename(course_name_ui)

    driver = None
    try:
        # 강의별 저장 폴더 생성 (최상위 폴더/강의명)
        lecture_save_dir = setup_lecture_directory(base_output_dir, sanitized_course_name)
        if not lecture_save_dir:
            print("강의 저장 폴더를 생성할 수 없습니다. 작업을 중단합니다.")
            return

        driver = get_chrome_driver()
        if not driver:
            print("WebDriver를 시작할 수 없습니다. 작업을 중단합니다.")
            return

        if not login_to_inflearn(driver, email, password):
            print("로그인 실패. 작업을 중단합니다.")
            return
        
        if not navigate_to_my_courses(driver):
            print("내 강의실 이동 실패. 작업을 중단합니다.")
            return
        
        # UI에서 받은 실제 강의명으로 강의 선택 시도
        if not select_course(driver, course_name_ui): 
            print(f"'{course_name_ui}' 강의 선택 실패. 작업을 중단합니다.")
            return
        
        print(f"'{course_name_ui}' 강의 페이지로 성공적으로 이동했습니다.")

        if not open_curriculum_tab(driver): # 커리큘럼이 닫혀있을 수 있으므로 항상 호출
            print("커리큘럼 탭 열기 실패. 첫 강의로 이동할 수 없습니다.")
            return

        if not select_first_available_lesson(driver): # 첫 번째 강의로 이동
            print("첫 번째 유효한 강의 선택 실패. 작업을 중단합니다.")
            return
        
        # 첫 번째 강의가 성공적으로 선택되었으므로, 이제 루프를 시작합니다.
        
        total_lecture_markdown_content = f"# 강의: {course_name_ui}\n\n"
        lesson_number = 0 # 강의(챕터) 번호

        while True:
            lesson_number += 1
            current_lesson_name_raw = ""
            sanitized_lesson_name = ""

            # 현재 강의(챕터) 이름 가져오기 (TODO 5 관련)
            try:
                # video_title_area h1, lecture-title h1, title h1 등 다양한 가능성 고려
                title_xpath = "//div[contains(@class,'video_title_area')]//h1 | //div[contains(@class, 'lecture-title')]//h1 | //h1[contains(@class, 'title') and not(ancestor::header)]"
                # 헤더의 h1은 사이트 전체 제목일 수 있으므로 제외 (좀 더 구체적인 상황에 따라 조정 필요)
                lesson_title_element = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, title_xpath))
                )
                current_lesson_name_raw = lesson_title_element.text.strip()
                if not current_lesson_name_raw: # 안전장치
                    current_lesson_name_raw = f"강의_{lesson_number}"
                print(f"\n--- 현재 강의(챕터) {lesson_number}: '{current_lesson_name_raw}' 처리 시작 ---")
            except TimeoutException:
                print(f"오류: 현재 강의(챕터) {lesson_number}의 제목을 가져올 수 없습니다 (시간 초과). 기본 이름을 사용합니다.")
                current_lesson_name_raw = f"알수없는_강의_{lesson_number}"
            except Exception as e_title:
                print(f"오류: 현재 강의(챕터) {lesson_number}의 제목 가져오기 중 예외 발생: {e_title}. 기본 이름을 사용합니다.")
                current_lesson_name_raw = f"오류발생_강의_{lesson_number}"
            
            sanitized_lesson_name = sanitize_filename(current_lesson_name_raw if current_lesson_name_raw else f"강의_{lesson_number}")

            if not open_script_tab(driver): 
                print(f"'{current_lesson_name_raw}' 강의의 스크립트 탭 열기 실패. 이 강의는 건너뜁니다.")
                total_lecture_markdown_content += f"## {lesson_number}. {current_lesson_name_raw} (스크립트 추출 실패 - 탭 열기 오류)\n\n"
            else:
                # 스크립트 내용 로드 최종 대기 (open_script_tab 내부에도 대기가 있지만, 추가적인 안정성 확보)
                try:
                    WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located((By.XPATH, "//aside[contains(@class, 'tab-aside')]//div[contains(@class, 'html_content_area_attr_pc')] | //aside[contains(@class, 'tab-aside')]//div[contains(@class, 'dashboard_aside_scroll_area_hidden')]//div[contains(@class, 'dashboard_aside_content__text')]"))
                    )
                except TimeoutException:
                    print(f"'{current_lesson_name_raw}' 강의의 스크립트 내용 컨테이너 표시 시간 초과. 스크래핑을 시도합니다.")

                script_data = extract_scripts_from_current_page(driver)
                
                current_lesson_markdown = f"## {lesson_number}. {current_lesson_name_raw}\n\n"
                if script_data:
                    for index in sorted(script_data.keys()):
                        timestamp, script_text = script_data[index]
                        current_lesson_markdown += f"**{timestamp}**  \n{script_text}  \n\n"
                    print(f"'{current_lesson_name_raw}' 스크립트 {len(script_data)}개 추출 완료.")
                    
                    # 개별 강의(챕터) 스크립트 파일 저장
                    lesson_filepath = get_section_filepath(lecture_save_dir, sanitized_lesson_name, lesson_number) # 기존 함수 재활용 (이름은 lesson으로)
                    save_markdown_file(lesson_filepath, current_lesson_markdown)
                else:
                    current_lesson_markdown += "(스크립트 내용 없음)\n\n"
                    print(f"'{current_lesson_name_raw}' 스크립트 추출 실패 또는 내용 없음.")
                
                total_lecture_markdown_content += current_lesson_markdown
            
            # 다음 강의(챕터)로 이동
            print(f"'{current_lesson_name_raw}' 강의 처리 완료. 다음 강의로 이동을 시도합니다.")
            if not go_to_next_chapter(driver):
                print("모든 강의(챕터) 완료 또는 다음으로 이동 불가. 스크래핑을 종료합니다.")
                break 
            else:
                print("다음 강의(챕터)로 성공적으로 이동했습니다. 계속 진행합니다.")
                time.sleep(2) # 새 페이지/콘텐츠 로드 대기

        print("\n--- 모든 강의(챕터) 스크래핑 완료 ---")
        
        # 전체 강의 내용을 담은 _total.md 파일 저장
        if total_lecture_markdown_content.strip() != f"# 강의: {course_name_ui}": 
            total_filepath = get_total_filepath(lecture_save_dir, sanitize_filename(course_name_ui)) # 강의명도 sanitize
            if save_markdown_file(total_filepath, total_lecture_markdown_content):
                print(f"전체 강의 스크립트가 {total_filepath} 파일로 저장되었습니다.")
            else:
                print(f"전체 강의 스크립트 파일 저장 실패 ({total_filepath})")
        else:
            print("추출된 전체 스크립트 내용이 없어 _total.md 파일을 생성하지 않습니다.")

    except Exception as e:
        print(f"\n!!! 워크플로우 실행 중 치명적 오류: {e.__class__.__name__}: {e}")
        traceback.print_exc()
    finally:
        if driver:
            print("\n--- 브라우저 닫기 ---")
            driver.quit()
        print("--- 스크래핑 워크플로우 종료 ---")

def main():
    print("--- 인프런 스크립트 추출 프로그램 UI 시작 ---")
    launch_ui()
    print("--- 프로그램 UI 종료됨 ---")

if __name__ == "__main__":
    main() 
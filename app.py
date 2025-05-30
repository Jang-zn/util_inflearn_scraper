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
    go_to_next_chapter,
    click_script_to_top
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
    """UI로부터 설정값을 받아 섹션/강의별로 스크래핑 전체 과정을 수행한다."""
    print("\n--- 스크래핑 워크플로우 시작 ---")
    email = user_configs.get("email")
    password = user_configs.get("password")
    course_name_ui = user_configs.get("course_name")
    if not all([email, password, course_name_ui]):
        print("오류: 필수 설정값이 누락되었습니다. (이메일, 비밀번호, 강의명)")
        return
    base_output_dir = DEFAULT_OUTPUT_DIR
    print("\n--- 실행 설정 정보 ---")
    print(f"이메일: {email[:3]}***")
    print(f"타겟 강의명: {course_name_ui}")
    print(f"기본 저장 경로: {base_output_dir}")
    sanitized_course_name = sanitize_filename(course_name_ui)
    driver = None
    try:
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
        if not select_course(driver, course_name_ui):
            print(f"'{course_name_ui}' 강의 선택 실패. 작업을 중단합니다.")
            return
        print(f"'{course_name_ui}' 강의 페이지로 성공적으로 이동했습니다.")
        total_lecture_markdown_content = f"# 강의: {course_name_ui}\n\n"
        section_xpath = "//div[@data-accordion='true']/div[contains(@class, 'mantine-Accordion-item')]"
        lesson_xpath = ".//li[.//p[contains(@class, 'unit-title')]]"
        lesson_count = 0
        # 섹션/강의 인덱스 기반 순회
        section_idx = 0
        while True:
            if not open_curriculum_tab(driver):
                print("커리큘럼 탭 열기 실패. 작업을 중단합니다.")
                break
            sections = driver.find_elements(By.XPATH, section_xpath)
            if section_idx >= len(sections):
                break
            section = sections[section_idx]
            try:
                section_name_elem = section.find_element(By.XPATH, ".//p[contains(@class, 'light-eahl1g')]")
                section_name = section_name_elem.text.strip()
            except Exception:
                section_name = f"섹션{section_idx+1}"
            lessons = section.find_elements(By.XPATH, lesson_xpath)
            lesson_idx = 0
            while True:
                # 커리큘럼 탭/섹션/강의 fresh하게 다시 가져옴
                if not open_curriculum_tab(driver):
                    print("커리큘럼 탭 열기 실패. 작업을 중단합니다.")
                    break
                sections = driver.find_elements(By.XPATH, section_xpath)
                if section_idx >= len(sections):
                    break
                section = sections[section_idx]
                lessons = section.find_elements(By.XPATH, lesson_xpath)
                if lesson_idx >= len(lessons):
                    break
                lesson = lessons[lesson_idx]
                try:
                    playtime_elem = lesson.find_elements(By.XPATH, ".//p[contains(@class, 'light-1wsq971') and contains(@class, 'mantine-1am8mhw')]")
                    if not playtime_elem or ':' not in playtime_elem[0].text:
                        lesson_idx += 1
                        continue
                    lesson_title_elem = lesson.find_element(By.XPATH, ".//p[contains(@class, 'unit-title')]")
                    lesson_title = lesson_title_elem.text.strip()
                    clickable = lesson.find_element(By.XPATH, ".//div[contains(@class, 'mantine-17wp1xg') and contains(@class, 'mantine-Accordion-content')]")
                    clickable.click()
                    time.sleep(1)
                    if not open_script_tab(driver):
                        print(f"'{section_name} - {lesson_title}' 스크립트 탭 열기 실패. 건너뜀.")
                        lesson_idx += 1
                        continue
                    click_script_to_top(driver)
                    script_data = extract_scripts_from_current_page(driver)
                    lesson_count += 1
                    sanitized_section = sanitize_filename(section_name)
                    sanitized_lesson = sanitize_filename(lesson_title)
                    current_lesson_markdown = f"## {section_name} - {lesson_title}\n\n"
                    if script_data:
                        for index in sorted(script_data.keys()):
                            timestamp, script_text = script_data[index]
                            current_lesson_markdown += f"**{timestamp}**  \n{script_text}  \n\n"
                        print(f"'{section_name} - {lesson_title}' 스크립트 {len(script_data)}개 추출 완료.")
                        lesson_filepath = get_section_filepath(lecture_save_dir, f"{sanitized_section}_{sanitized_lesson}", lesson_count)
                        save_markdown_file(lesson_filepath, current_lesson_markdown)
                    else:
                        current_lesson_markdown += "(스크립트 내용 없음)\n\n"
                        print(f"'{section_name} - {lesson_title}' 스크립트 추출 실패 또는 내용 없음.")
                    total_lecture_markdown_content += current_lesson_markdown
                except Exception as e:
                    print(f"'{section_name}' 섹션 내 강의 처리 중 오류: {e}")
                lesson_idx += 1
            section_idx += 1
        print("\n--- 모든 강의(챕터) 스크래핑 완료 ---")
        if total_lecture_markdown_content.strip() != f"# 강의: {course_name_ui}":
            total_filepath = get_total_filepath(lecture_save_dir, sanitize_filename(course_name_ui))
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
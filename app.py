import time
import traceback
import os
import glob

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
        # 전체 섹션/강의 개수 카운트
        if not open_curriculum_tab(driver):
            print("커리큘럼 탭 열기 실패. 작업을 중단합니다.")
            return
        sections_all = driver.find_elements(By.XPATH, section_xpath)
        total_sections = len(sections_all)
        total_lessons = 0
        for section in sections_all:
            lessons_in_section = section.find_elements(By.XPATH, lesson_xpath)
            for lesson in lessons_in_section:
                playtime_elem = lesson.find_elements(By.XPATH, ".//p[contains(@class, 'light-1wsq971') and contains(@class, 'mantine-1am8mhw')]")
                if playtime_elem and ':' in playtime_elem[0].text:
                    total_lessons += 1
        print(f"전체 섹션: {total_sections}, 전체 영상(강의): {total_lessons}")
        lesson_count = 0
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
            # 섹션별 영상 개수 카운트
            lessons_with_video = [lesson for lesson in lessons if lesson.find_elements(By.XPATH, ".//p[contains(@class, 'light-1wsq971') and contains(@class, 'mantine-1am8mhw')]" ) and ':' in lesson.find_elements(By.XPATH, ".//p[contains(@class, 'light-1wsq971') and contains(@class, 'mantine-1am8mhw')]")[0].text]
            total_lessons_in_section = len(lessons_with_video)
            # 섹션별 폴더 생성
            sanitized_section = sanitize_filename(section_name)
            section_dir = os.path.join(lecture_save_dir, sanitized_section)
            os.makedirs(section_dir, exist_ok=True)
            while True:
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
                    # 진행상태 로그
                    print(f"[섹션 {section_idx+1}/{total_sections}] '{section_name}' | [강의 {lesson_count+1}/{total_lessons}] '{lesson_title}' 스크래핑 시작...")
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
                    sanitized_lesson = sanitize_filename(lesson_title)
                    current_lesson_markdown = f"## {section_name} - {lesson_title}\n\n"
                    if script_data:
                        for index in sorted(script_data.keys()):
                            timestamp, script_text = script_data[index]
                            current_lesson_markdown += f"**{timestamp}**  \n{script_text}  \n\n"
                        print(f"'{section_name} - {lesson_title}' 스크립트 {len(script_data)}개 추출 완료.")
                        lesson_filename = f"{lesson_idx+1}_{sanitized_lesson}.md"
                        lesson_filepath = os.path.join(section_dir, lesson_filename)
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
        # 섹션별 total.md 생성
        for section in set([sanitize_filename(section_name) for section_name in [
            section.find_element(By.XPATH, ".//p[contains(@class, 'light-eahl1g')]").text.strip() if section.find_elements(By.XPATH, ".//p[contains(@class, 'light-eahl1g')]") else f"섹션{idx+1}"
            for idx, section in enumerate(driver.find_elements(By.XPATH, section_xpath))
        ]]):
            section_dir = os.path.join(lecture_save_dir, section)
            section_total_path = os.path.join(lecture_save_dir, f"{section}_total.md")
            md_files = sorted(glob.glob(os.path.join(section_dir, "*.md")))
            section_total_content = ""
            for md_file in md_files:
                with open(md_file, "r", encoding="utf-8") as f:
                    section_total_content += f.read() + "\n\n"
            with open(section_total_path, "w", encoding="utf-8") as f:
                f.write(section_total_content)
            print(f"섹션별 total 저장: {section_total_path}")
        # 전체 total.md는 더 이상 생성하지 않음
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
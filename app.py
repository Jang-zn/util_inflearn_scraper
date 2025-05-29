import time
import traceback

# 모듈 임포트
from config import get_chrome_driver, DEFAULT_OUTPUT_DIR # .env에서 기본 출력 폴더 가져오기
from ui import launch_ui 
from auth import login_to_inflearn
from navigation import (
    navigate_to_my_courses, 
    select_course, 
    select_chapter, 
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
        
        # 모든 섹션의 내용을 통합 저장할 변수
        total_lecture_markdown_content = f"# 강의: {course_name_ui}\n\n"
        section_number = 0 # 섹션 번호 (파일 이름용)

        # 첫 번째 "섹션"(또는 챕터리스트의 첫 항목) 선택
        if not select_chapter(driver): # select_chapter가 첫번째 항목을 선택하도록 되어있다고 가정
            print("첫 섹션(챕터) 선택 실패. 작업을 중단합니다.")
            return

        while True:
            section_number += 1
            # 현재 "섹션"의 이름 가져오기 (실제로는 더 정확한 방법 필요)
            # 예: 목차에서 현재 활성화된 섹션의 텍스트를 가져오거나, 페이지 내 h2/h3 태그 등
            current_section_name_raw = driver.title # 임시로 페이지 타이틀 사용
            sanitized_section_name = sanitize_filename(current_section_name_raw)
            print(f"\n--- 섹션 {section_number}: '{current_section_name_raw}' (정제됨: '{sanitized_section_name}') 처리 시작 ---")

            if not open_script_tab(driver):
                print("스크립트 탭 열기 실패. 다음 섹션으로 이동합니다.")
                total_lecture_markdown_content += f"## 섹션 {section_number}: {current_section_name_raw} (스크립트 추출 실패)\n\n"
                if not go_to_next_chapter(driver): # 다음 섹션(챕터)으로 이동 시도
                    print("다음 섹션(챕터) 이동 불가. 스크래핑 종료.")
                    break
                else:
                    time.sleep(2) # 페이지 로드 대기
                    continue
            
            time.sleep(1) # 스크립트 내용 로드 대기
            
            script_data = extract_scripts_from_current_page(driver)
            
            current_section_markdown = f"## 섹션 {section_number}: {current_section_name_raw}\n\n"
            if script_data:
                for index in sorted(script_data.keys()):
                    timestamp, script_text = script_data[index]
                    current_section_markdown += f"**{timestamp}**  \n{script_text}  \n\n"
                print(f"'{current_section_name_raw}' 섹션 스크립트 {len(script_data)}개 추출 완료.")
                
                # 현재 섹션 스크립트를 개별 파일로 저장 (강의명폴더/섹션명_번호.md)
                section_filepath = get_section_filepath(lecture_save_dir, sanitized_section_name, section_number)
                save_markdown_file(section_filepath, current_section_markdown)
            else:
                current_section_markdown += "(스크립트 내용 없음)\n\n"
                print(f"'{current_section_name_raw}' 섹션 스크립트 추출 실패 또는 내용 없음.")
            
            total_lecture_markdown_content += current_section_markdown # 통합본에 현재 섹션 내용 추가

            if not go_to_next_chapter(driver): # 다음 섹션(챕터)으로 이동
                print("모든 섹션(챕터) 완료 또는 다음으로 이동 불가.")
                break
            else:
                print("다음 섹션(챕터)으로 이동합니다.")
                time.sleep(3) # 페이지 로드 대기
        
        print("\n--- 모든 섹션 스크래핑 완료 ---")
        
        # 전체 강의 내용을 담은 _total.md 파일 저장
        if total_lecture_markdown_content.strip() != f"# 강의: {course_name_ui}": # 내용이 있는지 확인
            total_filepath = get_total_filepath(lecture_save_dir, sanitized_course_name)
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
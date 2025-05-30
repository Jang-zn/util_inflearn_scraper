from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def navigate_to_my_courses(driver):
    """내 강의 페이지로 이동합니다."""
    print("내 강의 페이지로 이동 중...")
    my_courses_url = "https://www.inflearn.com/my/courses"
    driver.get(my_courses_url)
    try:
        # '내 학습'과 같은 특정 텍스트를 가진 H1 태그 또는 페이지의 고유한 컨테이너가 나타나는지 확인
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, "//h2[contains(text(),'내 학습') or contains(text(),'수강중인 강의')]"))
        )
        print("내 강의 페이지 로딩 완료.")
        print(f"내 강의 페이지 URL: {driver.current_url}")
        # 현재 URL이 정말로 my_courses_url인지 한 번 더 확인
        if my_courses_url not in driver.current_url:
            print(f"경고: 내 강의 페이지로 이동했으나 URL이 다릅니다. 현재 URL: {driver.current_url}")
            # 다른 페이지로 리디렉션되었을 가능성 고려
        return True
    except TimeoutException:
        print(f"내 강의 페이지 로딩 시간 초과. (URL: {my_courses_url})")
        print(f"현재 URL: {driver.current_url}")
        return False
    except Exception as e:
        print(f"내 강의 페이지 이동 또는 로딩 실패: {e}")
        print(f"현재 URL: {driver.current_url}")
        return False

def select_course(driver, course_title):
    """
    Navigates to the course dashboard page by selecting a course from the "My Courses" page.

    Args:
        driver: The Selenium WebDriver instance.
        course_title: The title of the course to select.

    Returns:
        True if the course was successfully selected and navigated to, False otherwise.
    """
    try:
        print(f"'{course_title}' 강의를 선택합니다...")
        # aria-label에 course_title이 포함된 강의 중 첫 번째를 선택
        course_link_xpath = f"//a[contains(@aria-label, '{course_title}') and contains(@aria-label, '학습하러 가기')]"
        course_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, course_link_xpath))
        )
        # 클릭 전에 href 미리 추출
        href = course_element.get_attribute('href')
        course_element.click()
        time.sleep(0.5)
        # 클릭 후에는 element에 접근하지 않는다 (stale 방지)
        if href and "courseId=" in href:
            course_id = href.split("courseId=")[1].split("&")[0]
            WebDriverWait(driver, 10).until(
                EC.url_contains(course_id)
            )
            print(f"'{course_title}' 강의 페이지로 이동했습니다.")
            return True
        else:
            # fallback: URL이 바뀌었는지 wait
            WebDriverWait(driver, 10).until(
                lambda d: d.current_url != "https://www.inflearn.com/my/courses"
            )
            print(f"'{course_title}' 강의를 클릭했습니다. URL 변경을 확인해주세요.")
            return True
    except TimeoutException:
        print(f"오류: '{course_title}' 강의를 찾거나 클릭할 수 없습니다 (시간 초과).")
        return False
    except NoSuchElementException:
        print(f"오류: '{course_title}' 강의를 찾을 수 없습니다.")
        return False
    except Exception as e:
        print(f"'{course_title}' 강의 선택 중 예기치 않은 오류 발생: {e}")
        return False

def scroll_curriculum_to_top(driver):
    """
    커리큘럼 리스트를 맨 위로 스크롤한다 (data-index=0인 div가 보이도록).
    """
    try:
        # 커리큘럼 컨테이너 찾기 (스크롤 가능한 div)
        container = driver.find_element(By.XPATH, "//div[@data-accordion='true']")
        driver.execute_script("arguments[0].scrollTop = 0;", container)
        print("커리큘럼을 맨 위로 스크롤함.")
        return True
    except Exception as e:
        print(f"커리큘럼 맨 위 스크롤 실패: {e}")
        return False

def select_first_available_lesson(driver):
    """
    Selects the first available lesson (video with playtime) from the first section in the curriculum.
    """
    try:
        print("첫 번째 유효한 강의(영상)를 선택합니다...")
        scroll_curriculum_to_top(driver)
        sections_xpath = "//div[@data-accordion='true']/div[contains(@class, 'mantine-Accordion-item')]"
        sections = driver.find_elements(By.XPATH, sections_xpath)
        if not sections:
            print("오류: 강의 섹션을 찾을 수 없습니다.")
            return False
        first_section = sections[0]
        lesson_items_xpath = ".//li[.//p[contains(@class, 'unit-title')]]"
        lessons = first_section.find_elements(By.XPATH, lesson_items_xpath)
        if not lessons:
            print("오류: 첫 번째 섹션에서 강의 항목을 찾을 수 없습니다.")
            return False
        for lesson in lessons:
            try:
                playtime_element_xpath = ".//p[contains(@class, 'light-1wsq971') and contains(@class, 'mantine-1am8mhw')]"
                playtime_elements = lesson.find_elements(By.XPATH, playtime_element_xpath)
                if playtime_elements:
                    playtime_text = playtime_elements[0].text.strip()
                    if ":" in playtime_text:
                        lesson_title_element = lesson.find_element(By.XPATH, ".//p[contains(@class, 'unit-title')]")
                        lesson_title = lesson_title_element.text.strip()
                        print(f"선택 가능한 강의 찾음: '{lesson_title}' (재생 시간: {playtime_text})")
                        element_to_click = lesson.find_element(By.XPATH, ".//div[contains(@class, 'mantine-17wp1xg') and contains(@class, 'mantine-Accordion-content')]")
                        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(element_to_click))
                        element_to_click.click()
                        time.sleep(0.5)
                        print(f"'{lesson_title}' 강의를 클릭했습니다.")
                        return True
            except NoSuchElementException:
                continue
        print("오류: 첫 번째 섹션에서 재생 시간이 있는 유효한 강의를 찾지 못했습니다.")
        return False
    except TimeoutException:
        print("오류: 강의 커리큘럼을 찾는 중 시간 초과.")
        return False
    except Exception as e:
        print(f"첫 번째 강의 선택 중 예기치 않은 오류 발생: {e}")
        return False

def open_script_tab(driver):
    """
    URL 파라미터로 스크립트 탭을 직접 연다 + '확인했어요' 모달 처리.
    """
    try:
        url = driver.current_url
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        qs['tab'] = ['script']
        new_query = urlencode(qs, doseq=True)
        new_url = urlunparse(parsed._replace(query=new_query))
        if driver.current_url != new_url:
            driver.get(new_url)
        # 모달이 있으면 먼저 닫는다
        try:
            confirm_button_xpath = "//button[.//span[text()='확인했어요']]"
            confirm_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, confirm_button_xpath))
            )
            print("'확인했어요' 모달 버튼을 클릭합니다.")
            confirm_button.click()
            time.sleep(0.5)
        except TimeoutException:
            print("'확인했어요' 모달이 없거나 시간 내에 나타나지 않았습니다. 계속 진행합니다.")
        # 스크립트 탭이 열렸는지 h2[text()='스크립트']로 확인
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//h2[contains(text(), '스크립트')]"))
        )
        print("스크립트 탭이 열렸습니다 (URL 파라미터 + 모달 처리).")
        return True
    except Exception as e:
        print(f"스크립트 탭 URL 이동/모달 처리 중 오류: {e}")
        return False

def open_curriculum_tab(driver):
    """
    URL 파라미터로 커리큘럼 탭을 직접 연다.
    """
    try:
        url = driver.current_url
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        qs['tab'] = ['curriculum']
        new_query = urlencode(qs, doseq=True)
        new_url = urlunparse(parsed._replace(query=new_query))
        if driver.current_url != new_url:
            driver.get(new_url)
        # 커리큘럼 탭의 주요 요소가 뜰 때까지 대기 (예: 커리큘럼 리스트)
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//h2[contains(text(), '커리큘럼')]"))
        )
        print("커리큘럼 탭이 열렸습니다 (URL 파라미터 방식).")
        return True
    except Exception as e:
        print(f"커리큘럼 탭 URL 이동 중 오류: {e}")
        return False

def go_to_next_chapter(driver):
    """
    Navigates to the next chapter (lesson/video) in the course.
    If the current lesson is the last in a section, it moves to the first lesson of the next section.
    Returns True if successfully navigated to the next lesson, False otherwise (e.g., end of course or error).
    """
    print("다음 챕터(강의)로 이동을 시도합니다...")
    try:
        if not open_curriculum_tab(driver):
            print("다음 챕터 이동 실패: 커리큘럼 탭을 열 수 없습니다.")
            return False
        all_lessons_info = []
        sections_xpath = "//div[@data-accordion='true']/div[contains(@class, 'mantine-Accordion-item')]"
        sections = driver.find_elements(By.XPATH, sections_xpath)
        if not sections:
            print("오류: 커리큘럼에서 강의 섹션을 찾을 수 없습니다.")
            return False
        for section_idx, section in enumerate(sections):
            lesson_items_xpath = ".//li[.//p[contains(@class, 'unit-title')]]"
            lessons_in_section = section.find_elements(By.XPATH, lesson_items_xpath)
            for lesson_item_idx, lesson_item in enumerate(lessons_in_section):
                try:
                    playtime_element_xpath = ".//p[contains(@class, 'light-1wsq971') and contains(@class, 'mantine-1am8mhw')]"
                    playtime_elements = lesson_item.find_elements(By.XPATH, playtime_element_xpath)
                    if playtime_elements and ":" in playtime_elements[0].text.strip():
                        title_element = lesson_item.find_element(By.XPATH, ".//p[contains(@class, 'unit-title')]")
                        clickable_element = lesson_item.find_element(By.XPATH, ".//div[contains(@class, 'mantine-17wp1xg') and contains(@class, 'mantine-Accordion-content')]")
                        all_lessons_info.append((title_element.text.strip(), clickable_element))
                except NoSuchElementException:
                    continue
        if not all_lessons_info:
            print("오류: 커리큘럼에서 재생 가능한 강의를 찾을 수 없습니다.")
            return False
        # 커리큘럼 내에서 활성화된(현재 재생중) 강의 제목 찾기
        current_title_xpath = (
            "//div[@data-accordion='true']//p[contains(@class, 'unit-title') and (ancestor::*[contains(@class, 'active')] or ancestor::*[@aria-current='true'])]"
        )
        try:
            current_title_element = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, current_title_xpath))
            )
            current_lesson_title = current_title_element.text.strip()
            print(f"현재 재생 중인 강의 제목: '{current_lesson_title}'")
        except TimeoutException:
            print("오류: 현재 재생 중인 강의의 제목을 커리큘럼에서 찾을 수 없습니다.")
            return False
        except Exception as e_title:
            print(f"현재 강의 제목 가져오기 중 오류: {e_title}")
            return False
        current_lesson_index = -1
        for i, (title, _) in enumerate(all_lessons_info):
            if title == current_lesson_title:
                current_lesson_index = i
                break
        if current_lesson_index == -1:
            print(f"오류: 현재 강의 '{current_lesson_title}'를 커리큘럼 목록에서 찾을 수 없습니다.")
            return False
        if current_lesson_index < len(all_lessons_info) - 1:
            next_lesson_title, next_lesson_element_to_click = all_lessons_info[current_lesson_index + 1]
            print(f"다음 강의로 이동합니다: '{next_lesson_title}'")
            driver.execute_script("arguments[0].scrollIntoView(true);", next_lesson_element_to_click)
            time.sleep(0.5)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(next_lesson_element_to_click))
            next_lesson_element_to_click.click()
            time.sleep(0.5)
            try:
                WebDriverWait(driver, 15).until(
                    lambda d: d.find_element(By.XPATH, current_title_xpath).text.strip() == next_lesson_title and \
                              d.find_element(By.XPATH, current_title_xpath).text.strip() != current_lesson_title
                )
                print(f"'{next_lesson_title}' 강의 페이지로 성공적으로 이동했습니다.")
                return True
            except TimeoutException:
                print(f"다음 강의 ('{next_lesson_title}')로 이동 후, 페이지 업데이트 확인 시간 초과.")
                print("클릭은 성공했으므로, 페이지가 로드된 것으로 간주하고 진행합니다.")
                time.sleep(3)
                return True
        else:
            print("현재 강의가 마지막 강의입니다. 더 이상 진행할 강의가 없습니다.")
            return False
    except Exception as e:
        print(f"다음 챕터(강의)로 이동 중 예기치 않은 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

def click_script_to_top(driver):
    """
    스크립트 탭에서 data-index=0이 보일 때까지, 현재 보이는 가장 위(가장 작은 index) 스크립트 블록을 클릭해서 위로 이동.
    """
    try:
        for _ in range(30):  # 무한루프 방지
            zero_elem = driver.find_elements(By.XPATH, "//div[@data-index='0']")
            if zero_elem:
                print("data-index=0 스크립트 블록이 보임. 맨 위 도달.")
                return True
            # 현재 보이는 data-index 중 가장 작은 값의 div를 찾음
            all_elems = driver.find_elements(By.XPATH, "//div[@data-index]")
            if not all_elems:
                print("스크립트 data-index div를 찾을 수 없음.")
                return False
            min_index = min(int(e.get_attribute("data-index")) for e in all_elems)
            min_elem = [e for e in all_elems if int(e.get_attribute("data-index")) == min_index][0]
            min_elem.click()
            print(f"data-index={min_index} 스크립트 블록 클릭 (위로 이동)")
            time.sleep(0.3)  # 페이지 갱신 대기
        print("data-index=0이 30번 시도에도 안 보임.")
        return False
    except Exception as e:
        print(f"스크립트 맨 위 클릭 이동 실패: {e}")
        return False

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
                    # select_first_available_lesson(test_driver)
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
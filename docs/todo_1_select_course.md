# TODO 1: 강의 선택 기능 구현 (`navigation.py: select_course`) - 완료

**목표:** 사용자가 `.env` 또는 UI를 통해 입력한 강의명으로 "내 학습" 페이지에서 해당 강의를 찾아 클릭하고, 강의 대시보드 페이지로 성공적으로 이동하는 기능을 구현합니다.

**현재 상태:** 완료

**구현된 내용:**

*   `navigation.py`에 `select_course(driver, course_title)` 함수가 구현되었습니다.
*   이 함수는 "내 학습" 페이지(`https://www.inflearn.com/my/courses`)에 이미 접속해 있다고 가정합니다.
*   `course_title`을 인자로 받아, 해당 제목을 가진 강의를 찾습니다.
    *   강의 링크(`<a>` 태그)의 `aria-label` 속성 값이 `"{course_title} 학습하러 가기"`와 일치하는 요소를 찾습니다.
    *   요소를 찾으면 클릭하여 강의 상세 페이지로 이동합니다.
*   성공 시 `True`, 실패 또는 오류 발생 시 `False`를 반환합니다.
*   `WebDriverWait`와 `EC.element_to_be_clickable`을 사용하여 요소가 클릭 가능할 때까지 대기합니다.
*   `TimeoutException`, `NoSuchElementException` 등 발생 가능한 예외를 처리합니다.

**`select_course` 함수 예시:**
```python
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
        # 강의 링크의 aria-label을 사용하여 특정 강의 찾기
        # 예: aria-label="[코드캠프] 부트캠프에서 만든 고농축 백엔드 코스 학습하러 가기"
        # course_link_xpath = f"//a[contains(@aria-label, "{course_title}") and contains(@aria-label, '학습하러 가기')]"
        
        # 더 구체적인 선택자 (클래스명은 변경될 수 있으므로, 구조와 aria-label에 더 의존)
        # 제공된 HTML 구조를 보면, 강의 카드는 <a> 태그 내부에 복잡한 구조를 가집니다.
        # 핵심은 course_title이 포함된 aria-label을 가진 <a> 태그를 찾는 것입니다.
        course_link_xpath = f"//a[.//div[contains(@class, 'css-1a3d945')] and contains(@aria-label, '{course_title}') and contains(@aria-label, '학습하러 가기')]"


        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'courses_container__')]"))
        )
        
        course_element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, course_link_xpath))
        )
        
        # 클릭 전 요소가 화면에 보이도록 스크롤 (필요한 경우)
        driver.execute_script("arguments[0].scrollIntoView(true);", course_element)
        time.sleep(0.5) # 스크롤 후 잠시 대기

        course_element.click()
        
        # 강의 페이지로 이동했는지 간단히 확인 (예: URL 변경 또는 특정 요소 확인)
        # WebDriverWait(driver, 10).until(EC.url_contains("dashboard")) # 또는 강의 페이지의 특정 요소
        print(f"'{course_title}' 강의 페이지로 이동했습니다.")
        return True
    except TimeoutException:
        print(f"오류: '{course_title}'에 해당하는 강의를 찾거나 클릭하는 데 시간이 초과되었습니다.")
        return False
    except NoSuchElementException:
        print(f"오류: '{course_title}'에 해당하는 강의를 찾을 수 없습니다. 강의 제목을 정확히 확인해주세요.")
        return False
    except Exception as e:
        print(f"'{course_title}' 강의 선택 중 예기치 않은 오류 발생: {e}")
        return False

```

**`app.py`에서의 사용:**
```python
# ... (이전 코드 생략) ...
from navigation import login_to_inflearn, navigate_to_my_courses, select_course
# ...

def execute_scraping_workflow():
    user_configs = load_user_configs()
    driver = init_driver()
    if not driver:
        return

    try:
        if not login_to_inflearn(driver, user_configs['email'], user_configs['password']):
            return

        if not navigate_to_my_courses(driver):
            return

        course_name_ui = user_configs.get("course_name") # UI 또는 .env에서 가져온 강의명
        if not course_name_ui:
            print("오류: 스크래핑할 강의명이 설정되지 않았습니다.")
            return

        if not select_course(driver, course_name_ui):
            print(f"'{course_name_ui}' 강의 선택 실패. 작업을 중단합니다.")
            return
        
        print(f"'{course_name_ui}' 강의 페이지로 성공적으로 이동했습니다.")
        # 다음 단계 (커리큘럼 열기, 첫 강의 선택 등) 진행
        # ...

    finally:
        if driver:
            driver.quit()
```

**다음 단계:**
*   [x] ~~`navigation.py`에 `select_course` 함수 정의 및 테스트~~
*   [x] ~~`app.py`에서 `select_course` 호출하여 강의 선택 로직 통합~~

## 필요한 작업
1.  **강의 목록 페이지 분석:**
    *   "내 학습" (https://www.inflearn.com/my/courses) 페이지의 HTML 구조를 분석한다.
    *   개별 강의를 나타내는 HTML 요소(예: `<div>`, `<a>` 태그)와 그 특징(클래스명, ID, 속성 등)을 파악한다.
    *   강의 제목 텍스트를 포함하는 요소를 특정할 수 있는 방법을 찾는다.
    *   클릭 가능한 요소(보통 `<a>` 태그 또는 상위의 클릭 가능한 카드 요소)를 식별한다.

2.  **강의명 매칭 전략 수립:**
    *   사용자가 입력한 `course_name`과 페이지 내의 강의 제목들을 비교하는 방법을 결정한다.
        *   **정확히 일치:** 가장 간단하지만, 사용자가 약간의 오타를 내거나 강의명이 변경되면 실패할 수 있다.
        *   **부분 일치 (contains):** `course_name` 문자열이 페이지의 강의 제목에 포함되는지 확인한다. 여러 강의가 매칭될 수 있으므로, 첫 번째 매칭 항목을 선택하거나 사용자에게 선택지를 제공하는 등의 추가 로직이 필요할 수 있다. (우선은 첫 번째 매칭 항목 선택으로 단순화)
        *   **유사도 기반 매칭 (선택적 고급 기능):** Levenshtein 거리, Jaro-Winkler 유사도 등을 사용하여 가장 유사한 강의를 찾는다. (초기 구현에서는 제외 가능)

3.  **Selenium을 이용한 요소 탐색 및 클릭:**
    *   `WebDriverWait`와 `EC.element_to_be_clickable` 또는 `EC.presence_of_element_located`를 사용하여 강의 요소를 안정적으로 찾는다.
    *   XPath 또는 CSS Selector를 사용하여 요소를 지정한다.
        *   예시 XPath (부분 일치): `//div[contains(@class, 'course_card_title') and contains(text(), '{course_name}')]/ancestor::a`
        *   예시 CSS Selector (부분 일치, 클래스명은 실제 사이트에 맞게 수정 필요): `a.course-card:has(div.course-title:contains('{course_name}'))`
    *   찾은 요소를 `.click()` 메서드로 클릭한다.

4.  **페이지 이동 확인 및 대기:**
    *   클릭 후, 강의 대시보드 페이지로 정상적으로 이동했는지 확인한다.
        *   URL 변경 확인 (`driver.current_url`)
        *   강의 대시보드 페이지에만 존재하는 특정 요소의 등장 확인
    *   `time.sleep()` 또는 `WebDriverWait`를 사용하여 페이지 로딩을 충분히 기다린다.

5.  **예외 처리:**
    *   강의를 찾지 못한 경우 (예: `TimeoutException`)
    *   클릭 과정에서 오류가 발생한 경우
    *   이 경우 `False`를 반환하거나 적절한 예외를 발생시켜 `app.py`에서 처리할 수 있도록 한다.

6.  **반환 값:**
    *   성공적으로 강의 페이지로 이동하면 `True`를 반환한다.
    *   실패하면 `False`를 반환한다.

## 진행 상태
- [ ] 미시작
- [ ] 진행 중
- [ ] 완료
- [ ] 보류

## 참고 사항/고려 사항
- 인프런의 HTML 구조는 변경될 수 있으므로, 선택자는 유연하게 작성하거나 주기적인 확인이 필요할 수 있다.
- 동적으로 로드되는 강의 목록의 경우, 스크롤을 통해 모든 강의가 화면에 표시되도록 하는 로직이 추가로 필요할 수 있다. (현재는 보이는 화면 내에서만 찾는다고 가정)
- 여러 강의가 매칭될 경우의 처리 방안을 명확히 해야 한다. (현재는 첫 번째 매칭 항목 선택) 
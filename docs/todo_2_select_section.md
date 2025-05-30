# TODO 2: 커리큘럼에서 첫 강의 선택 및 다음 강의 이동 기능 구현 (`navigation.py`) - 완료

**목표:**
1.  강의 상세 페이지에서 "커리큘럼" 탭을 열고, 해당 커리큘럼의 첫 번째 섹션에 있는 첫 번째 강의 (재생 시간이 명시된, 즉 실제 영상 강의)를 선택하여 재생 페이지로 이동합니다.
2.  한 강의의 스크립트 스크래핑이 완료된 후, "커리큘럼" 탭으로 돌아와 현재 재생된 강의의 다음 강의를 선택합니다. 다음 강의가 다른 섹션에 있을 수도 있습니다. 모든 강의를 순차적으로 처리할 수 있어야 합니다.

**현재 상태:** 완료

**구현된 내용:**

*   **`navigation.py`에 `open_curriculum_tab(driver)` 함수 구현:**
    *   강의 페이지에서 "커리큘럼" 탭 버튼 (`title="커리큘럼"`)을 찾아 클릭합니다.
    *   탭이 이미 열려있는 경우 추가 동작을 하지 않습니다.
    *   커리큘럼 섹션 (`<aside>`)이 나타날 때까지 대기합니다.
*   **`navigation.py`에 `select_first_available_lesson(driver)` 함수 구현:**
    *   `open_curriculum_tab`을 먼저 호출하여 커리큘럼이 열려있도록 보장합니다.
    *   커리큘럼 내의 모든 섹션(`div[data-accordion='true']/div.mantine-Accordion-item`)을 찾습니다.
    *   첫 번째 섹션부터 시작하여, 재생 시간(`p.mantine-Text-root.light-1wsq971.mantine-1am8mhw` 또는 유사 패턴)이 표시된 첫 번째 강의(`div.mantine-Group-root.unit-icon ~ div.mantine-Stack-root p.unit-title`)를 찾아 클릭합니다.
    *   클릭 후, 페이지 URL이나 특정 요소 변경을 통해 다음 페이지 로드를 감지할 수 있습니다. (현재는 클릭 후 즉시 반환)
*   **`navigation.py`에 `go_to_next_chapter(driver)` 함수 구현:**
    *   `open_curriculum_tab`을 먼저 호출합니다.
    *   모든 섹션과 그 안의 모든 강의(재생 시간 유무와 관계없이 제목과 클릭 가능한 요소)를 수집합니다.
    *   현재 URL, 페이지 타이틀, 또는 선택된 강의의 활성화 상태(`aria-current="true"` 또는 유사 속성/클래스)를 기준으로 현재 재생 중인 강의를 식별합니다. (현재 구현은 현재 URL의 `unitId`를 사용합니다.)
    *   수집된 전체 강의 목록에서 현재 강의의 다음 강의를 찾아 클릭합니다.
    *   다음 강의가 없으면 (마지막 강의였으면) `False`를 반환하고, 성공적으로 다음 강의로 이동하면 `True`를 반환합니다.
    *   다음 강의 클릭 후, 페이지 변경을 기다립니다 (예: URL의 `unitId` 변경).

**`select_first_available_lesson` XPath 핵심 로직 (예시):**
```python
# 섹션들: //div[@data-accordion='true']/div[contains(@class, 'mantine-Accordion-item')]
# 섹션 내 강의들: .//div[contains(@class, 'mantine-Accordion-content')]//div[contains(@class, 'mantine-1h371dd') or contains(@class, 'mantine-Group-root') and .//p[contains(@class, 'unit-title')]]
# 강의 제목: .//p[contains(@class, 'unit-title')]
# 강의 시간: .//p[contains(@class, 'mantine-1am8mhw')]
```

**`go_to_next_chapter` 핵심 로직 (예시):**
```python
# 모든 강의 요소 (클릭 가능) 및 제목 수집
all_lessons_elements = [] # (element, title, unit_id)
# 현재 unitId = driver.current_url.split('unitId=')[-1].split('&')[0]
# current_index 찾기
# if current_index + 1 < len(all_lessons_elements):
#   next_lesson_element.click()
#   WebDriverWait(driver, 10).until(EC.url_changes(current_url))
```

**`app.py`에서의 사용 흐름:**
```python
# ... (select_course 이후) ...
if not open_curriculum_tab(driver):
    # 오류 처리
    return

if not select_first_available_lesson(driver):
    # 오류 처리
    return

# 첫 강의 스크립트 스크래핑
# ... scraper.extract_scripts_from_current_page(driver) ...

while go_to_next_chapter(driver):
    # 다음 강의로 이동 성공
    if not open_script_tab(driver): # 스크립트 탭 다시 열기 (필요시)
        # 오류 처리 또는 다음 챕터로 시도
        continue 
    # ... scraper.extract_scripts_from_current_page(driver) ...
else:
    print("모든 강의의 스크립트 수집 완료 또는 다음 강의 없음.")

# 전체 내용 파일로 저장
```

**다음 단계:**
*   [x] ~~`open_curriculum_tab` 함수 구현 및 테스트~~
*   [x] ~~`select_first_available_lesson` 함수 구현 및 테스트~~
*   [x] ~~`go_to_next_chapter` 함수 구현 및 테스트~~
*   [x] ~~`app.py`에서 위 함수들을 순서대로 호출하여 첫 강의 재생 및 다음 강의로 넘어가는 로직 통합~~

## 진행 상태
- [x] 완료
- [ ] 보류

## 참고 사항/고려 사항
- `select_chapter`라는 함수명이 약간 혼란을 줄 수 있다. "섹션의 첫 챕터 선택"이 더 명확하지만, 기존 함수명을 유지한다면 주석으로 역할을 명확히 한다.
- `app.py`의 루프와 `go_to_next_chapter` 함수와의 연계를 고려하여, 이 함수는 항상 **새로운 섹션 탐색의 시작점** 역할을 하도록 구현되어야 한다.
- 만약 첫 번째 섹션/챕터가 이미 선택/활성화된 상태로 페이지가 로드된다면, 별도의 클릭 없이 `True`를 반환할 수도 있다. (페이지 초기 상태 확인 필요) 
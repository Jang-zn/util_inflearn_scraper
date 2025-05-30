# TODO 4: 다음 강의(챕터)로 이동 기능 구현 (`navigation.py: go_to_next_chapter`) - 완료

**목표:** 현재 챕터(강의 영상)의 스크립트 스크래핑이 완료된 후, 강의 목차(커리큘럼)에서 다음 챕터(강의 영상)를 찾아 클릭하여 해당 영상 재생 페이지로 이동합니다. 만약 현재 챕터가 섹션의 마지막이라면, 다음 섹션의 첫 번째 챕터로 이동해야 합니다. 모든 챕터/강의를 순회할 수 있어야 합니다.

**현재 상태:** 완료 (기능은 `go_to_next_chapter`로 통합됨)

**구현된 내용:**

*   **`navigation.py`의 `go_to_next_chapter(driver)` 함수에 통합 구현:**
    *   **커리큘럼 탭 열기:** `open_curriculum_tab(driver)`를 호출하여 커리큘럼이 보이도록 합니다.
    *   **모든 강의 목록 수집:**
        *   커리큘럼 내 모든 섹션과 각 섹션의 모든 강의(레슨) 아이템을 찾습니다.
        *   각 강의 아이템에 대해 다음 정보를 수집합니다:
            *   클릭 가능한 `WebElement`
            *   강의 제목 (예: `p.unit-title`)
            *   고유 식별자 (예: `unitId` - URL에서 파싱하거나, 요소의 `data-unit-id` 속성 등 활용 가능)
        *   수집된 강의들을 순서대로 리스트에 저장합니다. (`all_lessons_info = [(element, title, unit_id), ...]`) 
    *   **현재 재생 중인 강의 식별:**
        *   현재 브라우저의 URL에서 `unitId`를 추출하여 현재 재생 중인 강의를 식별합니다.
        *   `all_lessons_info` 리스트에서 현재 `unitId`와 일치하는 강의를 찾아 현재 인덱스를 결정합니다.
    *   **다음 강의로 이동:**
        *   현재 인덱스 + 1 위치에 다음 강의가 있는지 확인합니다.
        *   다음 강의가 존재하면 해당 `WebElement`를 클릭합니다.
        *   클릭 후, URL이 변경될 때까지 (새로운 `unitId`로) 또는 특정 페이지 요소가 나타날 때까지 대기합니다.
        *   성공적으로 다음 강의 페이지로 이동하면 `True`를 반환합니다.
    *   **마지막 강의 처리:**
        *   다음 강의가 없으면 (즉, 현재 강의가 전체 코스의 마지막 강의였으면) `False`를 반환합니다.
    *   **예외 처리:** 요소 탐색 실패, 클릭 실패 등의 예외를 처리하고 `False`를 반환합니다.

**핵심 로직 (의사코드):**
```python
def go_to_next_chapter(driver):
    open_curriculum_tab(driver) # 커리큘럼 열기

    sections = driver.find_elements(By.XPATH, "//div[@data-accordion='true']/div[contains(@class, 'mantine-Accordion-item')]")
    all_lessons_info = [] # (element, title, unit_id)

    for section in sections:
        lesson_elements = section.find_elements(By.XPATH, ".//div[contains(@class, 'mantine-1h371dd') or (contains(@class, 'mantine-Group-root') and .//p[contains(@class, 'unit-title')])]")
        for lesson_element in lesson_elements:
            try:
                title_element = lesson_element.find_element(By.XPATH, ".//p[contains(@class, 'unit-title')]")
                title = title_element.text.strip()
                
                # unit_id는 lesson_element 또는 그 상위/하위에서 찾아야 함 (예: data-unit-id, 또는 링크의 href에서 파싱)
                # 여기서는 lesson_element를 직접 클릭 대상으로 가정하고, unit_id는 URL 비교용으로 사용
                # unit_id를 가져오는 더 안정적인 방법은 각 lesson_element의 링크(<a> 태그)에서 href를 파싱하는 것일 수 있음.
                # 또는 클릭 가능한 div 자체가 unitId를 data 속성으로 가질 수 있음.
                # 지금은 임시로 해당 element 자체를 저장. 실제 클릭 및 ID 추출은 더 정교해야함.
                clickable_part = lesson_element # 실제 클릭할 부분. 더 구체적일 수 있음 (예: title_element)
                # unitId를 요소에서 직접 가져올 수 있다면 더 좋음. 여기서는 예시로 None.
                # unit_id = lesson_element.get_attribute('data-unit-id') # 이런 형태가 있다면
                all_lessons_info.append({'element': clickable_part, 'title': title, 'id_for_match': None}) # id_for_match는 URL의 unitId와 비교할 값
            except NoSuchElementException:
                continue # 제목 없는 항목 등은 건너뜀

    if not all_lessons_info:
        print("커리큘럼에서 강의 목록을 찾을 수 없습니다.")
        return False

    current_url = driver.current_url
    current_unit_id = None
    if "unitId=" in current_url:
        current_unit_id = current_url.split("unitId=")[-1].split("&")[0]
    
    # all_lessons_info를 만들 때 각 항목의 unit_id를 정확히 추출/저장했다면, 그것과 current_unit_id를 비교
    # 여기서는 임시로 순서 기반으로 다음 것을 찾지만, 실제로는 unit_id 매칭이 필요
    current_lesson_index = -1
    # (이 부분은 실제 unit_id를 all_lessons_info에 저장하고 매칭하는 로직으로 개선 필요)
    # 지금은 unit_id를 수집하지 못했으므로, 현재 선택된 요소를 찾아야 함. (예: aria-current="true" 등)
    # 또는, 각 lesson_info에 URL의 unitId와 매칭될 수 있는 식별자를 저장해야 함.

    # 현재 강의의 정확한 식별 및 다음 강의 선택 로직은 navigation.py의 실제 구현을 참고해야 합니다.
    # 아래는 개념적인 흐름입니다.

    # found_current = False
    # for i, lesson in enumerate(all_lessons_info):
    #     if lesson['id_for_match'] == current_unit_id: # id_for_match가 실제 unitId라고 가정
    #         current_lesson_index = i
    #         break
    
    # if current_lesson_index == -1 and current_unit_id:
        # Fallback: 만약 unit_id로 못찾았지만, 현재 URL에 unit_id가 있다면, 
        # 커리큘럼에서 현재 선택된 것으로 표시된 항목을 찾으려고 시도할 수 있음.
        # 예: current_lesson_element = driver.find_element(By.XPATH, "//div[contains(@class, 'active_lesson_class_indicator')]")
        # 그리고 이 element를 all_lessons_info와 매칭.
    
    # 이 로직은 navigation.py의 go_to_next_chapter에 있는 실제 구현과 동기화되어야 합니다.
    # (현재 로직은 모든 강의를 찾고, 현재 URL의 unitId를 기반으로 다음 강의를 찾아 클릭합니다.)

    # 실제 navigation.py의 `go_to_next_chapter`는 모든 클릭 가능한 강의 요소와 해당 강의의 `unitId`를 추출합니다.
    # 그 다음 현재 URL의 `unitId`와 비교하여 현재 강의의 인덱스를 찾고 다음 강의를 클릭합니다.

    print("go_to_next_chapter의 상세 로직은 navigation.py를 직접 참조하세요.")
    print("이 문서는 개념을 설명하며, 실제 구현은 이미 완료되었습니다.")
    # 실제 구현은 이미 navigation.py에 있으므로, 이 부분은 설명용으로 남김
    return False # 이 함수는 실제 실행 로직보다는 문서용으로 남김

```

**`app.py`에서의 사용:**
```python
# ... (첫 강의 스크래핑 완료 후) ...
current_files_info = [] # 파일명과 내용을 저장할 리스트

while True:
    # 현재 페이지 스크립트 추출 및 저장 준비
    if open_script_tab(driver):
        current_lesson_title = get_current_lesson_title(driver) # TODO 5에서 구현될 함수
        if not current_lesson_title:
            current_lesson_title = f"Untitled_Lesson_{len(current_files_info) + 1}"
        
        # 파일명 생성 (os_utils.py에 함수로 분리 가능)
        # safe_title = re.sub(r'[\\/*?:""<>|]', '', current_lesson_title).strip()
        # filename = f"{safe_title}.md"

        print(f"강의 '{current_lesson_title}'의 스크립트를 추출합니다...")
        script_content = scraper.extract_scripts_from_current_page(driver)
        if script_content:
            # current_files_info.append({"name": filename, "content": script_content, "title": current_lesson_title})
            # 임시로 lesson_count와 함께 저장 (TODO 5와 파일 저장 로직 통합 시 변경)
            lecture_markdown_content = f"## {current_lesson_title}\n\n{script_content}\n\n"
            # total_lecture_markdown_content에 추가 (app.py 참조)
            print(f"'{current_lesson_title}' 스크립트 추출 완료.")
        else:
            print(f"'{current_lesson_title}'에서 스크립트를 추출하지 못했습니다.")
    else:
        print("스크립트 탭을 열지 못해 현재 강의 스크립트를 건너뜁니다.")

    # 다음 강의로 이동 시도
    if not go_to_next_chapter(driver):
        print("모든 강의를 처리했거나 다음 강의로 이동할 수 없습니다.")
        break # 루프 종료
    else:
        print("다음 강의로 성공적으로 이동했습니다. 계속 진행합니다.")
        # 페이지 로드 대기 (go_to_next_chapter 내부에 이미 포함되어 있을 수 있음)
        time.sleep(2) # 추가적인 안정성을 위해 짧은 대기

# 모든 스크립트 취합 후 파일 저장 (app.py의 save_total_markdown_file 함수 등 사용)
# ...

```

**다음 단계:**
*   [x] ~~`navigation.py`에 `go_to_next_chapter` 함수 정의, 구현 및 테스트.~~
    *   [x] ~~커리큘럼 열기 (또는 이미 열려있는지 확인)~~ 
    *   [x] ~~모든 강의 목록 (클릭 가능 요소, 제목, unitId) 수집~~ 
    *   [x] ~~현재 강의 식별 (URL의 unitId 또는 활성화된 요소 기반)~~ 
    *   [x] ~~다음 강의 클릭 및 페이지 이동 확인~~ 
    *   [x] ~~마지막 강의일 경우 False 반환~~ 
*   [x] ~~`app.py`의 메인 루프에서 `go_to_next_chapter`를 사용하여 다음 강의로 이동하고, 루프를 제어하는 로직 통합.~~

## 진행 상태
- [ ] 미시작
- [ ] 진행 중
- [ ] 완료
- [ ] 보류

## 참고 사항/고려 사항
- 목차 구조가 복잡하거나 섹션/챕터 구분이 명확하지 않은 경우, 방법 B의 구현 난이도가 높아질 수 있다.
- "다음" 버튼이 Ajax 호출로 내용을 변경하고 URL은 변경하지 않는 SPA(Single Page Application) 형태일 경우, 페이지 이동 확인 로직에 주의해야 한다. (영상 제목 변경, 스크립트 패널 내용 변경 등을 확인해야 할 수 있음)
- `app.py`에서는 이 함수가 `False`를 반환하면 모든 섹션/챕터의 스크래핑이 완료되었다고 판단한다. 
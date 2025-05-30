# TODO 5: 현재 강의(챕터)의 정확한 이름 추출 로직 구현 (`app.py` 또는 `navigation.py`) - 부분 완료 / 개선 가능

**목표:** 스크립트를 파일로 저장할 때, 현재 스크래핑 중인 강의(챕터)의 정확하고 완전한 이름을 가져와 파일명 또는 Markdown 내용의 헤더로 사용합니다. 인프런의 경우 "섹션 제목 - 강의 제목" 또는 그냥 "강의 제목" 형식이 될 수 있습니다.

**현재 상태:** 부분 완료 / 개선 가능

*   `app.py`의 `execute_scraping_workflow` 함수 내에서 `navigation.py`의 `go_to_next_chapter`가 반환하는 `current_lesson_info` (딕셔셔너리 형태, `{'title': lesson_title, 'unit_id': unit_id}`)를 사용하여 현재 강의의 제목(`lesson_title`)을 가져오고 있습니다. (`current_lesson_title = current_lesson_info.get('title')`)
*   이 제목은 개별 강의(비디오)의 제목이며, 상위 "섹션"의 제목은 현재 명시적으로 추출하여 결합하고 있지는 않습니다.
*   파일명 생성 시 이 `current_lesson_title`을 사용합니다.

**구현된 내용 (app.py):**
```python
# app.py 내 execute_scraping_workflow 함수 중 일부

# ... 첫 강의 선택 후 ...

current_lesson_info = get_current_lesson_info(driver) # 네비게이션에서 현재 강의 정보 가져오기
if not current_lesson_info:
    print("현재 강의 정보를 가져올 수 없습니다. 첫 번째 강의 스크래핑을 건너뜁니다.")
else:
    process_lesson(driver, current_lesson_info, user_configs) # 첫 강의 처리

while True:
    next_lesson_info = go_to_next_chapter(driver) # 다음 강의 정보 (또는 None)
    if next_lesson_info:
        print(f"다음 강의로 이동: {next_lesson_info.get('title')}")
        if not open_script_tab(driver):
            print(f"스크립트 탭을 열 수 없어 '{next_lesson_info.get('title')}' 강의를 건너뜁니다.")
            # 다음 챕터 시도 전에 현재 챕터 정보를 업데이트해야 함
            current_lesson_info = next_lesson_info # 다음 챕터가 현재 챕터가 됨
            continue
        
        # 페이지가 완전히 로드될 시간을 충분히 줌 (open_script_tab 이후)
        time.sleep(config.LOAD_WAIT_TIME) 

        # 스크립트 추출 전, 다시 한 번 현재 강의 정보(특히 제목)를 정확히 가져오는 것이 좋을 수 있음
        # (페이지 전환 후 DOM이 변경되었을 수 있으므로)
        # 하지만 go_to_next_chapter에서 반환된 정보가 다음 강의의 정보이므로 이를 사용.
        current_lesson_info = next_lesson_info # 현재 처리할 강의 정보 업데이트
        
        lesson_title_for_file = current_lesson_info.get('title', f"Untitled_Lesson_{time.time()}")
        print(f"강의 '{lesson_title_for_file}'의 스크립트를 추출합니다...")
        
        script_data = scraper.extract_scripts_from_current_page(driver)
        if script_data:
            # ... 파일 저장 로직 ... (lesson_title_for_file 사용)
            # total_lecture_markdown_content += f"## {lesson_title_for_file}\n\n{script_data}\n\n"
            # 파일명: make_safe_filename(f"{course_name_ui} - {lesson_count:03d} - {lesson_title_for_file}.md")
            pass # app.py의 실제 저장 로직 참조
        else:
            print(f"'{lesson_title_for_file}'에서 스크립트를 추출하지 못했습니다.")
    else:
        print("모든 강의를 처리했거나 다음 강의로 이동할 수 없습니다.")
        break
```

**`navigation.py`의 `get_current_lesson_info(driver)` (신규 추가 제안 또는 현재 로직):**
`go_to_next_chapter` 함수는 내부적으로 현재 강의를 식별하고 다음 강의로 넘어갑니다. `app.py`에서 첫 강의 처리 및 루프 내에서 현재 처리 중인 강의의 정보를 명확히 하기 위해, 현재 페이지에서 강의 제목과 ID를 가져오는 헬퍼 함수가 `navigation.py`에 있을 수 있습니다. `go_to_next_chapter`가 다음 강의 정보를 반환하므로, `app.py`는 이 정보를 사용합니다. 최초 실행 시에는 `select_first_available_lesson` 후 이 정보를 가져와야 합니다.

```python
# navigation.py 에 추가될 수 있는 함수 (또는 go_to_next_chapter, select_first_available_lesson의 반환 값 활용)
def get_current_lesson_info(driver):
    """ 현재 페이지에서 강의 제목과 unitId를 가져옵니다. """
    try:
        # 현재 선택/활성화된 강의의 제목을 커리큘럼에서 찾거나, 페이지의 메인 타이틀 영역에서 가져옴.
        # 예시1: 커리큘럼에서 활성화된 아이템 찾기
        # active_lesson_xpath = "//div[contains(@class, 'unit-item') and contains(@class, 'active')]//p[contains(@class, 'unit-title')]"
        # title = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, active_lesson_xpath))).text.strip()
        
        # 예시2: 강의 영상 제목 영역 (더 일반적일 수 있음)
        # 실제 해당 페이지의 영상 제목 XPath로 변경 필요
        # title_xpath = "//h1[contains(@class, 'lecture-title-class')]" 
        # title = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, title_xpath))).text.strip()
        
        # 현재는 navigation.py의 go_to_next_chapter나 select_first_available_lesson이 클릭 후
        # 다음/현재 강의 정보를 반환하므로 app.py에서 이 정보를 직접 사용.
        # 이 함수는 만약 해당 함수들의 반환값 외에, 임의의 시점에서 현재 강의 정보를 다시 가져와야 할 때 유용.
        # 지금은 go_to_next_chapter 가 lesson_info를 반환하므로, 중복된 로직을 피하기 위해
        # app.py에서 해당 반환값을 직접 사용하도록 함.
        # 이 함수를 구현한다면, 커리큘럼 내 현재 활성화된 강의의 unitId와 제목을 가져오도록 함.
        
        # 강의 제목 (실제 페이지 구조에 따라 XPath 수정 필요)
        # 일반적으로 커리큘럼에서 현재 활성화된 강의 아이템을 찾거나, 페이지 상단의 제목을 가져옵니다.
        # 여기서는 `go_to_next_chapter`가 반환하는 정보를 활용하므로, 이 함수는 app.py에서 직접 호출되지 않을 수 있습니다.
        # 다만, 첫 강의 선택 후에는 비슷한 로직으로 제목을 가져와야 합니다.
        title_xpath = "//div[contains(@class, 'classroom_header_title')]/h2"
        lesson_title = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, title_xpath))
        ).text.strip()

        current_url = driver.current_url
        unit_id = None
        if "unitId=" in current_url:
            unit_id = current_url.split("unitId=")[-1].split("&")[0]
        
        if lesson_title and unit_id:
            return {"title": lesson_title, "unit_id": unit_id}
        elif lesson_title: # ID는 없지만 제목이라도
            return {"title": lesson_title, "unit_id": None}
        else:
            # 제목을 못찾는 경우, 커리큘럼에서 active된 unit을 찾아볼 수 있음
            # active_unit_title_xpath = "//div[contains(@class, 'unit--active')]//p[contains(@class, 'unit-title') or contains(@class, 'unit__title')]" 
            # 위 XPath는 예시이며, 실제 인프런 구조에 맞게 수정 필요
            pass # 일단 실패 처리

    except TimeoutException:
        print("현재 강의 제목/ID를 가져오는 데 시간이 초과되었습니다.")
    except NoSuchElementException:
        print("현재 강의 제목/ID 요소를 찾을 수 없습니다.")
    except Exception as e:
        print(f"현재 강의 정보 가져오기 중 오류: {e}")
    return None
```

**개선 방향:**

1.  **섹션 제목 추출 (선택적):**
    *   현재 `go_to_next_chapter`는 개별 강의의 정보(`lesson_title`, `unit_id`)만 반환합니다.
    *   만약 파일명이나 마크다운 헤더에 "섹션명 - 강의명" 형태로 저장하고 싶다면, 현재 강의가 속한 섹션의 제목도 가져와야 합니다.
    *   `go_to_next_chapter` 또는 `get_current_lesson_info` 함수가 반환하는 딕셔너리에 `section_title`도 포함하도록 수정할 수 있습니다.
    *   섹션 제목은 커리큘럼 구조에서 현재 활성화된 강의의 상위 요소(예: `div.mantine-Accordion-control` 내부의 텍스트)에서 가져올 수 있습니다.
2.  **`navigation.py`로 로직 이전:**
    *   현재 `app.py`에서 `go_to_next_chapter`의 반환값을 받아 처리하고 있으나, "현재 강의 정보 가져오기" 자체를 `navigation.py`의 명시적인 함수 (예: `get_current_lesson_details`)로 만들어 `app.py`가 호출하게 하면 더 깔끔할 수 있습니다. 이 함수는 (섹션 제목), 강의 제목, unit ID 등을 반환합니다.
    *   `select_first_available_lesson`도 선택된 첫 강의의 정보를 유사한 형식으로 반환하도록 합니다.
3.  **안정성 강화:**
    *   강의 제목이나 섹션 제목을 가져오는 XPath가 웹사이트 구조 변경에 최대한 강인하도록 작성합니다.

**다음 단계:**
*   [x] ~~`app.py`에서 `go_to_next_chapter`가 반환하는 강의 제목을 파일 저장 로직에 활용~~ (현재 개별 강의 제목 사용 중)
*   [ ] (선택적) 섹션 제목까지 포함하여 파일명/헤더를 구성하고 싶다면, `navigation.py`의 관련 함수들이 섹션 제목도 함께 반환하도록 수정하고 `app.py`에서 이를 활용합니다.
*   [ ] (선택적) `get_current_lesson_info`와 같은 명시적인 함수를 `navigation.py`에 만들어 `app.py`의 정보 획득 로직을 더 명확하게 분리합니다. (현재는 `go_to_next_chapter` 등의 반환 값을 직접 활용)

## 목표
`app.py`의 `execute_scraping_workflow` 함수 내에서, 현재 보고 있는 섹션 또는 챕터의 실제 이름을 웹 페이지로부터 정확하게 추출하여 파일 저장 및 Markdown 내용에 사용한다.

## 현재 상태
- `app.py`에서 `current_section_name_raw = driver.title` 코드를 사용하여 임시로 현재 웹페이지의 `<title>` 태그 내용을 섹션명으로 사용하고 있다.
- 이 방식은 페이지 타이틀이 실제 목차의 섹션명/챕터명과 다를 수 있고, 너무 일반적이거나 불필요한 정보를 포함할 수 있다.

## 필요한 작업
1.  **섹션/챕터 이름 표시 위치 분석:**
    *   강의 수강 페이지의 HTML 구조를 다시 분석한다.
    *   현재 재생 중인 영상(챕터)의 이름 또는 해당 영상이 속한 섹션의 이름이 명확하게 표시되는 부분을 찾는다.
        *   예: 목차(TOC) 영역에서 현재 활성화된 항목의 텍스트.
        *   예: 영상 플레이어 상단 또는 주변에 표시되는 현재 강의 제목/소제목.
        *   예: 페이지 내의 `<h1>`, `<h2>` 태그 등.
    *   해당 요소의 HTML 태그, 클래스명, ID 등을 파악하여 선택자를 특정한다.

2.  **이름 추출 전략:**
    *   **목차(TOC)에서 현재 활성화된 항목의 이름 가져오기:**
        *   `navigation.py`의 `select_chapter` 또는 `go_to_next_chapter`에서 다음 항목으로 성공적으로 이동했을 때, 해당 항목의 텍스트를 가져와 `app.py`로 반환하거나, `app.py`에서 직접 목차의 활성 항목을 찾아 텍스트를 추출한다.
        *   예시 XPath: `//li[contains(@class, 'toc-item') and contains(@class, 'active')]//span[@class='item-title']` (구조에 따라 변경)
    *   **페이지 본문에서 현재 강의/섹션 제목 요소의 텍스트 가져오기:**
        *   페이지 상단이나 특정 위치에 현재 강의의 세부 제목(챕터명 또는 섹션명)이 표시되는지 확인한다.
        *   예시 XPath: `//div[@class='lecture-title-container']/h2` (구조에 따라 변경)

3.  **Selenium으로 텍스트 추출:**
    *   선택한 전략에 따라, `driver.find_element(By.XPATH, "...").text` 또는 `driver.find_element(By.CSS_SELECTOR, "...").text` 등을 사용하여 텍스트를 가져온다.
    *   가져온 텍스트에서 불필요한 공백은 `.strip()`으로 제거한다.

4.  **`app.py`에 적용:**
    *   `execute_scraping_workflow` 함수 내의 `current_section_name_raw = driver.title` 부분을 위에서 구현한 실제 이름 추출 로직으로 대체한다.
    *   추출된 이름은 `sanitize_filename`을 거쳐 파일명 생성에 사용되고, Markdown 내용에도 원본 이름이 포함되도록 한다.

5.  **예외 처리:**
    *   지정한 선택자로 섹션/챕터 이름을 찾지 못할 경우를 대비한다.
        *   이 경우, `driver.title`을 대체(fallback)로 사용하거나, "알 수 없는 섹션"과 같은 기본값을 사용할 수 있다.
        *   또는 오류를 로깅하고 해당 섹션 처리를 어떻게 할지 결정한다 (예: 건너뛰기).

## 진행 상태
- [ ] 미시작
- [ ] 진행 중
- [ ] 완료
- [ ] 보류

## 참고 사항/고려 사항
- 어떤 강의는 "섹션 제목"과 "개별 영상(챕터) 제목"이 모두 중요할 수 있다. 파일명에는 더 상위 레벨인 "섹션 제목"을 사용하고, Markdown 내용에는 둘 다 기록하는 것을 고려할 수 있다.
- 현재 `app.py`의 루프는 "섹션" 단위로 돌고 있다고 가정하고 `section_number`를 증가시키고 있다. 만약 추출하는 이름이 "챕터명"이라면, 파일 저장 구조나 이름 규칙을 다시 고려해야 할 수 있다. (요청사항은 섹션명 기준이었음)
- 이 작업은 `navigation.py`의 함수들과 연계될 수 있다. 예를 들어, `go_to_next_chapter`가 성공적으로 다음 항목으로 이동했을 때 그 항목의 이름을 반환 받아 사용하는 방식도 가능하다. 
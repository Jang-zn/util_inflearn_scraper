# TODO 3: 스크립트 탭 열기 및 확인 모달 처리 (`navigation.py: open_script_tab`) - 완료

**목표:** 강의 영상 재생 페이지에서 "스크립트" 탭 버튼을 클릭하고, 만약 "확인했어요" 모달이 나타나면 해당 버튼을 클릭하여 닫습니다. 최종적으로 스크립트 내용이 보이는 영역이 나타나도록 합니다.

**현재 상태:** 완료

**구현된 내용:**

*   **`navigation.py`에 `open_script_tab(driver)` 함수 구현:**
    *   스크립트 탭 버튼을 찾습니다. XPath는 `title="스크립트"` 속성을 가진 `button`과 내부의 `p` 태그 텍스트 "스크립트"를 조합하여 사용합니다.
        *   `script_tab_button_xpath = "//button[@title='스크립트' and .//p[text()='스크립트']]"`
    *   버튼을 클릭합니다.
    *   클릭 후, "확인했어요" 모달이 나타나는지 확인합니다.
        *   `confirm_button_xpath = "//button[.//span[text()='확인했어요']]"`
        *   `WebDriverWait`를 짧은 시간(예: 2초)으로 설정하여 해당 버튼을 찾습니다.
        *   버튼이 찾아지면 클릭하여 모달을 닫습니다.
        *   `TimeoutException` 발생 시 (모달이 없음) 정상 진행으로 간주하고 로그를 남깁니다.
    *   스크립트 내용이 실제로 로드되었는지 확인하기 위해 특정 스크립트 컨테이너 요소가 나타날 때까지 대기합니다.
        *   `script_content_area_xpath = "//div[contains(@class, 'TranscriptView_script_text_container') or contains(@class, 'VideoScript_script_container__')]"` (또는 더 구체적인 실제 클래스명)
    *   성공적으로 스크립트 탭이 열리고 내용이 보이면 `True`, 오류 발생 시 `False`를 반환합니다.

**`open_script_tab` 함수 핵심 로직:**
```python
def open_script_tab(driver):
    try:
        print("스크립트 탭을 엽니다...")
        script_tab_button_xpath = "//button[@title='스크립트' and .//p[text()='스크립트']]"
        script_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, script_tab_button_xpath))
        )
        script_button.click()
        print("스크립트 탭 버튼 클릭 완료.")

        # "확인했어요" 모달 처리
        confirm_button_xpath = "//button[.//span[text()='확인했어요']]"
        try:
            confirm_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, confirm_button_xpath))
            )
            print("'확인했어요' 모달 버튼을 클릭합니다.")
            confirm_button.click()
        except TimeoutException:
            print("'확인했어요' 모달이 없거나 시간 내에 나타나지 않았습니다. 계속 진행합니다.")
        
        # 스크립트 내용 영역이 실제로 로드될 때까지 대기
        # 실제 스크립트 컨테이너의 클래스나 ID로 교체해야 합니다.
        # 예시: transcript_container_xpath = "//div[@class='actual-script-container-class']"
        # 현재는 TranscriptView_transcript_wrapper__vRbK0 와 VideoScript_script_page__n5N5p 를 사용
        transcript_visible_xpath = (
            "//div[contains(@class, 'TranscriptView_transcript_wrapper') or "
            "contains(@class, 'VideoScript_script_page') or "
            "contains(@class, 'ScriptTabPanel_script_tab_panel')]"
        )
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, transcript_visible_xpath))
        )
        print("스크립트 내용 영역이 확인되었습니다.")
        return True

    except TimeoutException:
        print("스크립트 탭 또는 관련 요소를 찾는 데 시간이 초과되었습니다.")
        return False
    except NoSuchElementException:
        print("스크립트 탭 또는 관련 요소를 찾을 수 없습니다.")
        return False
    except Exception as e:
        print(f"스크립트 탭을 여는 중 예기치 않은 오류 발생: {e}")
        return False
```

**`app.py`에서의 사용:**
```python
# ... (select_first_available_lesson 또는 go_to_next_chapter 이후) ...

if not open_script_tab(driver):
    print("스크립트 탭 열기 실패. 해당 강의/챕터 스크래핑을 건너뜁니다.")
    # continue 또는 return 등의 로직 처리
else:
    # 스크립트 탭 열기 성공, 스크래핑 로직 진행
    script_content = scraper.extract_scripts_from_current_page(driver) 
    # ...
```

**다음 단계:**
*   [x] ~~`open_script_tab` 함수 구현 및 테스트 (스크립트 탭 클릭, 모달 처리, 스크립트 영역 확인)~~
*   [x] ~~`app.py`의 메인 스크래핑 루프에서 `open_script_tab` 호출 통합~~

## 진행 상태
- [ ] 미시작
- [ ] 진행 중
- [ ] 완료
- [ ] 보류

## 참고 사항/고려 사항
- 스크립트 탭의 이름이나 위치, HTML 구조는 강의 UI 버전에 따라 다를 수 있다.
- 스크립트가 없는 강의 또는 섹션의 경우, 스크립트 탭 자체가 없거나 비활성화되어 있을 수 있다. 이 경우를 정상적인 실패로 처리해야 한다. 
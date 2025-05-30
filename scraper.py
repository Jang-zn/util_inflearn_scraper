from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import traceback

def extract_scripts_from_current_page(driver):
    """현재 페이지에서 스크립트를 추출하여 딕셔너리 형태로 반환합니다."""
    print("--- 스크립트 스크래핑 시작 ---")
    script_data = {}
    last_max_index_seen = -1
    no_new_items_count = 0
    scroll_attempts = 0
    max_scroll_attempts = 300 # 기존 값 유지 또는 필요시 조정

    # 스크립트 패널 요소 (선택적)
    # script_panel_selector = "div[data-radix-scroll-area-viewport].mantine-ScrollArea-viewport"
    # script_panel_element = None
    # try:
    #     script_panel_element = WebDriverWait(driver, 5).until(
    #         EC.presence_of_element_located((By.CSS_SELECTOR, script_panel_selector))
    #     )
    # except Exception:
    #     print(f"경고: 스크롤 가능한 스크립트 패널({script_panel_selector})을 찾지 못했습니다.")

    while True:
        print(f"\n[스크래핑 주기] 시도: {scroll_attempts + 1}/{max_scroll_attempts}")
        
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")
        script_divs = soup.find_all("div", attrs={"data-index": True})
        print(f"현재 화면 스크립트 항목 수: {len(script_divs)}")

        if not script_divs:
            if len(script_data) == 0 and scroll_attempts == 0: # 첫 시도부터 항목이 없을 경우
                print("경고: 스크립트 항목이 전혀 없습니다. 현재 페이지에 스크립트가 없거나 로딩 문제입니다.")
                return {} # 빈 딕셔너리 반환
            no_new_items_count += 1
            print(f"현재 화면에 'data-index' 항목 없음. 연속 {no_new_items_count}회")
            if no_new_items_count >= 3:
                print("--- 3회 연속 스크립트 항목 없음. 현재 챕터 스크래핑 종료. ---")
                break
            time.sleep(1)
            scroll_attempts += 1
            if scroll_attempts >= max_scroll_attempts:
                print(f"--- 최대 시도 횟수 ({max_scroll_attempts}회) 도달. 강제 종료. ---")
                break
            continue

        current_max_index_on_page = -1
        new_items_found_this_cycle = False

        for div in script_divs:
            try:
                index = int(div["data-index"])
                current_max_index_on_page = max(current_max_index_on_page, index)

                if index not in script_data:
                    new_items_found_this_cycle = True
                    # print(f"-> 새 스크립트: data-index={index}") # 로그 간소화
                    time_span = div.find("span", class_="mantine-1jlwn9k mantine-Badge-inner")
                    timestamp = time_span.get_text(strip=True) if time_span else "N/A"
                    
                    script_p = div.find("p", class_=lambda x: x and "mantine-Text-root" in x and "script-item-text" in x)
                    if not script_p: # script-item-text 클래스가 없는 경우도 대비
                        script_p = div.find("p", recursive=False) # 직계 자식 p 태그
                    
                    script_text = script_p.get_text(strip=True) if script_p else "N/A"
                    if script_text == "N/A":
                         print(f"  경고: 스크립트 텍스트 (p 태그) 없음 (data-index={index})")
                    script_data[index] = (timestamp, script_text)
            except Exception as e:
                print(f"  오류: data-index 처리 중 예외 발생 - {e} (항목: {div.prettify()[:100]}...)")
                continue
        
        print(f"처리된 총 스크립트 항목: {len(script_data)}, 현재 페이지 최대 인덱스: {current_max_index_on_page}, 이전 최대 인덱스: {last_max_index_seen}")

        if current_max_index_on_page <= last_max_index_seen and not new_items_found_this_cycle:
            no_new_items_count += 1
            print(f"!!! 새 data-index 갱신 안됨 / 새 항목 없음. 연속 {no_new_items_count}회.")
            if no_new_items_count >= 3:
                print("--- 3회 연속 새 data-index 갱신 없음. 현재 챕터 스크래핑 종료. ---")
                break
        else:
            no_new_items_count = 0

        last_max_index_seen = max(last_max_index_seen, current_max_index_on_page)
        
        # 다음 콘텐츠 로드를 위해 가장 마지막 data-index 클릭
        target_click_index = current_max_index_on_page
        if target_click_index == -1: # 페이지에 아무 항목도 없었을 경우 (이미 위에서 처리되었어야 함)
            print("클릭할 대상 인덱스가 없음. 다음 시도.")
            scroll_attempts += 1
            if scroll_attempts >= max_scroll_attempts: break
            time.sleep(1)
            continue
            
        print(f"[클릭 시도] 다음 로드를 위해 data-index={target_click_index} 클릭 시도")
        try:
            # 우선순위 1: 'script-item-text' 클래스를 가진 p 태그 내부
            target_element_xpath = f"//div[@data-index='{target_click_index}']//p[contains(@class, 'script-item-text') or contains(@class, 'mantine-Text-root')]"
            # 우선순위 2: div[@data-index] 바로 밑의 p 태그 (클래스 무관)
            # target_element_xpath_fallback = f"//div[@data-index='{target_click_index}']/p"
            # 우선순위 3: div[@data-index] 자체 (p 태그가 없는 경우 대비)
            # target_element_xpath_div = f"//div[@data-index='{target_click_index}']"
            
            element_to_click = None
            try:
                element_to_click = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, target_element_xpath))
                )
                # print(f"  클릭 대상 찾음 (XPATH: {target_element_xpath})")
            except Exception:
                # print(f"  첫번째 XPATH ({target_element_xpath}) 실패. div 자체 클릭 시도.")
                try:
                    target_element_xpath_div = f"//div[@data-index='{target_click_index}']"
                    element_to_click = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, target_element_xpath_div))
                    )
                    # print(f"  클릭 대상 찾음 (XPATH: {target_element_xpath_div}) - div 직접")
                except Exception as e_div_click:
                    print(f"  오류: 클릭할 요소(data-index={target_click_index}) 찾기 최종 실패. {e_div_click.__class__.__name__}")
                    # 이 경우, 더 이상 클릭으로 로드할 수 없다고 판단하고 루프를 빠져나갈 수 있음
                    if no_new_items_count >= 1: # 이미 새 항목이 없었던 상태라면 더 신뢰성 있게 종료
                        print("!!! 클릭할 요소 찾기 실패 + 새 항목 없었음. 현재 챕터 스크래핑 종료.")
                        scroll_attempts = max_scroll_attempts # 루프 강제 종료용
                    else:
                        print("  클릭 요소를 못찾았지만, 다음 반복에서 다시 시도합니다.")
                    # 여기서 continue를 하면 아래 클릭 로직을 건너뛰고 다음 스크롤 시도로 넘어감
                    scroll_attempts += 1
                    if scroll_attempts >= max_scroll_attempts: break
                    time.sleep(0.2)
                    continue # 다음 while 루프 반복으로

            if element_to_click:
                # print(f"  data-index={target_click_index} 요소로 스크롤 및 JavaScript 클릭 시도")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", element_to_click)
                time.sleep(0.2) # 스크롤 후 안정화 시간
                driver.execute_script("arguments[0].click();", element_to_click)
                # print(f"  JavaScript 클릭 성공 (data-index={target_click_index}). 0.8초 대기.")
                time.sleep(0.8) # 콘텐츠 로드 대기 시간
            # else 부분은 위에서 처리됨 (continue 또는 scroll_attempts 증가)

        except Exception as e:
            print(f"!!! 클릭 로직 중 예외 발생: {e.__class__.__name__}: {e}")
            traceback.print_exc(limit=1)
            if no_new_items_count >= 1:
                print("!!! 예외 발생 + 새 항목 없었음. 현재 챕터 스크래핑 종료.")
                break 
            print("클릭 시도 중 오류 발생, 다음 반복에서 다시 시도합니다.")
            pass

        scroll_attempts += 1
        if scroll_attempts >= max_scroll_attempts:
            print(f"--- 최대 클릭/스크롤 시도 ({max_scroll_attempts}회) 도달. 강제 종료. ---")
            break
            
    print(f"--- 스크래핑 완료 (총 {len(script_data)}개 항목) ---")
    return script_data


if __name__ == '__main__':
    # 이 모듈을 직접 실행하여 테스트하려면 WebDriver 인스턴스를 설정하고
    # 스크립트가 있는 페이지로 이동한 후 이 함수를 호출해야 합니다.
    # 예시:
    # from config import get_chrome_driver, INFLEARN_EMAIL, INFLEARN_PASSWORD
    # from auth import login_to_inflearn
    # from navigation import navigate_to_my_courses # navigation.py에 만들어야 함

    print("scraper.py 직접 실행 테스트는 UI나 app.py를 통해 실행하는 것을 권장합니다.")
    print("단독 테스트를 위해서는 드라이버 설정, 로그인, 특정 강의 스크립트 페이지 이동이 선행되어야 합니다.")

    # # 가상 테스트 시나리오 (실제 실행을 위해서는 위 모듈들이 필요)
    # test_driver = get_chrome_driver()
    # if test_driver and INFLEARN_EMAIL and INFLEARN_PASSWORD:
    #     if login_to_inflearn(test_driver, INFLEARN_EMAIL, INFLEARN_PASSWORD):
    #         # 1. 내 강의 페이지로 이동
    #         # navigate_to_my_courses(test_driver)
    #         # time.sleep(2)
                
    #         # 2. 사용자가 수동으로 특정 강의의 스크립트 탭으로 이동했다고 가정
    #         #    또는 자동화 코드가 있다면 해당 코드로 이동
    #         target_lecture_url = input("스크립트를 추출할 강의의 스크립트 페이지 URL을 입력하세요: ")
    #         if not target_lecture_url:
    #             print("URL이 입력되지 않아 테스트를 종료합니다.")
    #         else:
    #             test_driver.get(target_lecture_url)
    #             print(f"페이지 이동: {target_lecture_url}")
    #             print("5초 후 스크립트 추출 시작...")
    #             time.sleep(5) # 페이지 로딩 대기

    #             extracted_data = extract_scripts_from_current_page(test_driver)
                
    #             if extracted_data:
    #                 print("\n추출된 스크립트 데이터:")
    #                 for index in sorted(extracted_data.keys()):
    #                     timestamp, script = extracted_data[index]
    #                     print(f"  {index}: [{timestamp}] - {script[:50]}...")
    #                 print(f"총 {len(extracted_data)}개 항목 추출 완료.")
    #             else:
    #                 print("추출된 스크립트 데이터가 없습니다.")
    #     else:
    #         print("로그인 실패로 테스트를 진행할 수 없습니다.")
    #     test_driver.quit()
    # else:
    #     print("WebDriver 생성 실패 또는 환경변수 미설정으로 테스트 불가") 
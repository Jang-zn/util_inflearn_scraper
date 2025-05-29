from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import time
import traceback
import os # os 모듈 추가
from dotenv import load_dotenv # dotenv 추가

# .env 파일에서 환경 변수 로드
load_dotenv()

# --- 설정 변수 ( .env 파일에서 불러오기) --- #
INFLEARN_EMAIL = os.getenv("INFLEARN_EMAIL")
INFLEARN_PASSWORD = os.getenv("INFLEARN_PASSWORD")
DEFAULT_OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_lecture_scripts") # 기본값 설정
DEFAULT_BASE_FILENAME = os.getenv("BASE_FILENAME", "lecture_script") # 기본값 설정
# --- 설정 변수 끝 --- #

# Chrome 옵션 설정
chrome_options = Options()
# chrome_options.add_argument("--headless")  # 브라우저 창 없이 실행 (필요 시 제거)
chrome_options.add_argument("--start-maximized") # 브라우저 창 최대화 (더 많은 콘텐츠 보이게)

# Selenium WebDriver 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    print("--- 인프런 웹 자동화 스크립트 시작 ---")

    # .env 파일 로드 확인
    if not INFLEARN_EMAIL or not INFLEARN_PASSWORD:
        print("오류: .env 파일에 INFLEARN_EMAIL 또는 INFLEARN_PASSWORD가 설정되지 않았습니다.")
        print(".env.sample 파일을 참고하여 .env 파일을 설정해주세요.")
        exit()

    # --- 파일 저장 설정 --- (환경 변수 또는 기본값 사용)
    output_dir = DEFAULT_OUTPUT_DIR
    base_filename = DEFAULT_BASE_FILENAME
    print(f"\n--- 파일 저장 정보 ---")
    print(f"기본 저장 디렉토리: {output_dir}")
    print(f"기본 파일명 (확장자 제외): {base_filename}")

    # 디렉토리 생성 (존재하지 않을 경우)
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"디렉토리 생성됨: {output_dir}")
        except OSError as e:
            print(f"오류: 디렉토리 '{output_dir}' 생성에 실패했습니다. {e}")
            print(f"기본값인 현재 디렉토리 '.'에 저장합니다.")
            output_dir = "." # 실패 시 현재 디렉토리에 저장

    # 최종 파일 경로 결정 (중복 처리 포함)
    file_counter = 0
    output_filename = f"{base_filename}.md"
    output_path = os.path.join(output_dir, output_filename)

    while os.path.exists(output_path):
        output_filename = f"{base_filename}_{file_counter}.md"
        output_path = os.path.join(output_dir, output_filename)
        file_counter += 1
    
    print(f"최종 저장될 파일 경로: {output_path}")

    print("\n인프런 메인 페이지로 이동 중...")
    driver.get("https://www.inflearn.com/")
    print(f"현재 URL: {driver.current_url}")

    print("로그인 버튼 대기 중...")
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.mantine-UnstyledButton-root.mantine-Button-root.css-1uibevq.mantine-193n4qw"))
    )
    print("로그인 버튼 클릭.")
    login_button.click()
    print("로그인 모달창 로딩 대기 중...")
    time.sleep(1) # 모달창이 나타나는 시간 대기

    print("로그인 폼 필드 대기 중 (이메일)...")
    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "email"))
    )
    password_field = driver.find_element(By.ID, "password")

    print("이메일 및 비밀번호 입력.")
    email_field.send_keys(INFLEARN_EMAIL) # .env 값 사용
    password_field.send_keys(INFLEARN_PASSWORD) # .env 값 사용

    print("로그인 제출 버튼 대기 중...")
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.mantine-UnstyledButton-root.mantine-Button-root.mantine-1bt2sfd"))
    )
    print("로그인 제출 버튼 클릭.")
    submit_button.click()

    print("로그인 처리 후 4초 대기 중...")
    time.sleep(4)
    print(f"로그인 후 현재 URL: {driver.current_url}")

    print("내 강의 페이지로 이동 중...")
    driver.get("https://www.inflearn.com/my/courses")

    print("내 강의 페이지 로딩 완료 대기 중 (body 태그 확인)...")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    print("내 강의 페이지 로딩 완료.")
    print(f"내 강의 페이지 URL: {driver.current_url}")

    print("\n--- 사용자 인터랙션 대기 ---")
    print("원하는 강의의 스크립트 탭으로 직접 이동해주세요.")
    while True:
        user_input = input("완료되면 터미널에서 'y'를 입력하고 Enter를 누르세요: ")
        if user_input.lower() == 'y':
            print("사용자 'y' 입력 확인. 스크립트 스크래핑을 시작합니다.")
            break
    print("--- 스크립트 스크래핑 시작 ---")

    # 스크립트 데이터를 저장할 딕셔너리
    script_data = {}
    last_max_index_seen = -1 # 마지막으로 확인된 최대 data-index
    no_new_items_count = 0 # 새 항목이 발견되지 않은 연속 횟수 (종료 조건용)
    scroll_attempts = 0 # 클릭/스크롤 시도 횟수
    max_scroll_attempts = 300 # 최대 클릭/스크롤 시도 횟수 (무한 루프 방지)

    # 스크립트 패널 요소를 찾기 (선택 사항: 클릭할 요소가 속한 스크롤 영역에 포커스 주거나 스크롤 직접 제어 시 사용)
    script_panel_selector = "div[data-radix-scroll-area-viewport].mantine-ScrollArea-viewport"
    script_panel_element = None
    try:
        script_panel_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, script_panel_selector))
        )
        print(f"스크롤 가능한 스크립트 패널 요소 찾음: {script_panel_selector}")
    except Exception as e:
        print(f"경고: 스크롤 가능한 스크립트 패널을 찾지 못했습니다. {e}")
        print("이 경우 스크립트 항목 클릭이 직접적인 스크롤을 유발해야 합니다.")
        # script_panel_element는 None으로 유지되어 스크롤 시도하지 않음

    while True:
        print(f"\n[새로운 스크래핑 주기 시작] 시도 횟수: {scroll_attempts}")
        
        # 1. 현재 화면의 HTML 가져오기
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")

        script_divs = soup.find_all("div", attrs={"data-index": True})
        print(f"현재 화면에서 찾은 스크립트 항목 수: {len(script_divs)}")

        if not script_divs and len(script_data) == 0:
            print("경고: 스크립트 항목이 전혀 없습니다. 스크래핑 종료합니다.")
            break
        elif not script_divs and scroll_attempts > 0: # 스크롤/클릭 시도했는데 새 항목이 없으면 종료 고려
            print("경고: 현재 화면에서 'data-index'를 가진 스크립트 항목을 찾을 수 없습니다. (더 이상 로드될 내용이 없는 것으로 추정)")
            no_new_items_count += 1
            if no_new_items_count >= 3: # 3번 연속으로 새 항목 없으면 종료
                print("--- 3회 연속 스크립트 항목 없음. 스크래핑 종료합니다. ---")
                break
            time.sleep(1) # 잠시 대기 후 재시도
            scroll_attempts += 1
            if scroll_attempts > max_scroll_attempts:
                print(f"--- 최대 시도 횟수 ({max_scroll_attempts}회) 도달. 스크래핑 강제 종료. ---")
                break
            continue

        current_max_index = -1
        new_items_collected_this_iteration = False

        # 2. 현재 화면의 항목 처리 및 데이터 저장
        for div in script_divs:
            index = int(div["data-index"])
            if index > current_max_index:
                current_max_index = index # 현재 스캔에서 가장 높은 인덱스 업데이트

            if index not in script_data:
                new_items_collected_this_iteration = True
                print(f"-> 새 스크립트 항목 발견 및 저장: data-index={index}")

                time_span = div.find("span", class_="mantine-1jlwn9k mantine-Badge-inner")
                timestamp = time_span.get_text(strip=True) if time_span else "N/A"
                script_p = div.find("p", class_=lambda x: x and "mantine-Text-root" in x and "script-item-text" in x)
                if not script_p:
                    script_p = div.find("p", recursive=False)

                if script_p:
                    script_text = script_p.get_text(strip=True)
                else:
                    script_text = "N/A"
                    print(f"  경고: 스크립트 텍스트 (p 태그)를 찾을 수 없음 (data-index={index})")

                script_data[index] = (timestamp, script_text)
        
        print(f"현재까지 처리된 총 스크립트 항목 수: {len(script_data)}")
        print(f"현재 화면의 최대 data-index: {current_max_index}")
        print(f"이전 반복의 마지막 확인된 최대 data-index: {last_max_index_seen}")

        # 3. 종료 조건 확인 (새로운 항목이 없거나, 더 이상 로드되지 않는 경우)
        if current_max_index == last_max_index_seen:
            no_new_items_count += 1
            print(f"!!! 새 data-index가 갱신되지 않았습니다. 연속 {no_new_items_count}회.")
            if no_new_items_count >= 3: # 3번 연속으로 새 항목이 없으면 종료 (충분히 시도했는데 새 항목이 없다는 뜻)
                print("--- 3회 연속 새 data-index 갱신 없음. 스크래핑 종료합니다. ---")
                break
        else:
            no_new_items_count = 0 # 새 항목이 발견되면 카운트 초기화
            print("새 항목 발견 또는 data-index 갱신됨. 클릭하여 계속 진행합니다.")

        last_max_index_seen = current_max_index # 마지막으로 확인된 최대 인덱스 업데이트

        # 4. 클릭을 통해 다음 콘텐츠 로드 시도
        # 가장 마지막 data-index를 클릭합니다.
        target_click_index = current_max_index
        print(f"\n[클릭 시도] 다음 항목 로드를 위해 가장 마지막 항목 (data-index={target_click_index}) 클릭 시도 중...")
        
        try:
            target_p_xpath = f"//div[@data-index='{target_click_index}']//p[contains(@class, 'script-item-text')]"
            p_element_to_click = None

            print(f"  XPATH '{target_p_xpath}'로 클릭 가능한 p 태그 찾기 시도 (최대 5초 대기)...")
            try:
                p_element_to_click = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, target_p_xpath))
                )
                print("  성공: 'script-item-text' 클래스를 가진 p 태그를 찾았습니다.")
            except Exception as e_script_p:
                print(f"  실패: 'script-item-text' 클래스를 가진 p 태그를 찾지 못했습니다. ({e_script_p.__class__.__name__}: {e_script_p})")
                print(f"  대신 XPATH '//div[@data-index='{target_click_index}']//p'로 일반 p 태그 찾기 시도 (최대 3초 대기)...")
                try:
                    p_element_to_click = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, f"//div[@data-index='{target_click_index}']//p"))
                    )
                    print("  성공: 일반 p 태그를 찾았습니다.")
                except Exception as e_general_p:
                    print(f"  실패: 일반 p 태그도 찾지 못했습니다. ({e_general_p.__class__.__name__}: {e_general_p})")
                    p_element_to_click = None # 최종적으로 요소를 찾지 못함

            if p_element_to_click:
                print(f"  요소 발견! data-index={target_click_index}의 요소로 스크롤 중...")
                # 요소가 화면에 보이도록 스크롤 (필수)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", p_element_to_click)
                time.sleep(0.1) # 스크롤 후 짧은 대기
                print("  스크롤 완료.")

                print(f"  클릭할 요소 확인: {p_element_to_click.tag_name}, 텍스트: '{p_element_to_click.text[:50]}...'")
                print(f"  data-index={target_click_index}의 항목 JavaScript 클릭 시도 중...")
                driver.execute_script("arguments[0].click();", p_element_to_click) # JavaScript 클릭
                print(f"  JavaScript 클릭 성공! data-index={target_click_index} 항목을 클릭했습니다.")
                print("  다음 콘텐츠 로딩을 위해 1.0초 대기 중...")
                time.sleep(1.0) # 클릭 후 콘텐츠 로딩 대기
                print("  대기 완료.")
            else:
                print(f"  오류: 클릭할 요소(data-index={target_click_index}에 해당하는 p 태그)를 최종적으로 찾지 못했습니다.")
                # 클릭할 요소를 찾지 못했으면 더 이상 진행하기 어려우므로 종료 고려
                if no_new_items_count >= 1: # 이미 새 항목이 없었던 상태라면 바로 종료
                    print("!!! 클릭할 요소를 찾지 못했고, 이미 새 항목이 없었으므로 스크래핑을 종료합니다.")
                    break
                else: # 일단 다음 반복 시도
                    print("  클릭할 요소를 찾지 못했지만 다음 반복에서 다시 시도합니다.")

        except Exception as e:
            print(f"!!! 클릭 로직 실행 중 예상치 못한 오류 발생: {e.__class__.__name__}: {e}")
            traceback.print_exc() # 오류 스택 트레이스 출력
            if no_new_items_count >= 1:
                print("!!! 오류가 발생했고 이미 새 항목이 없었으므로 스크래핑을 종료합니다.")
                break
            print("클릭 시도 중 오류가 발생했지만, 다음 반복에서 다시 시도합니다.")
            pass # 오류 발생해도 일단 계속 진행

        scroll_attempts += 1
        if scroll_attempts > max_scroll_attempts:
            print(f"--- 최대 클릭/스크롤 시도 횟수 ({max_scroll_attempts}회) 도달. 스크래핑 강제 종료. ---")
            break

    print("\n--- 스크래핑 완료 ---")
    print("데이터 정렬 및 Markdown 파일 작성 시작.")
    markdown_content = "# 강의 스크립트\n\n"
    for index in sorted(script_data.keys()):
        timestamp, script_text = script_data[index]
        markdown_content += f"**{timestamp}** \n{script_text}  \n\n"

    # Markdown 파일로 저장
    with open(output_path, "w", encoding="utf-8") as md_file: # 수정된 output_path 사용
        md_file.write(markdown_content)

    print(f"총 {len(script_data)}개의 스크립트 항목이 {output_path} 파일로 성공적으로 저장되었습니다.") # 수정된 output_path 사용

except Exception as e:
    print(f"\n!!! 스크립트 실행 중 치명적인 오류 발생: {e.__class__.__name__}: {e}")
    traceback.print_exc()

finally:
    print("\n--- 브라우저 닫기 ---")
    driver.quit()
    print("--- 스크립트 종료 ---")
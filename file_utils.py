import os
import re # 파일명 정제를 위해 추가

def sanitize_filename(filename):
    """파일명으로 사용할 수 없는 문자를 제거하거나 대체합니다."""
    filename = filename.replace(" ", "_")
    # 한글(가-힣), 영문, 숫자, _, -, . 만 허용
    filename = re.sub(r'[^a-zA-Z0-9가-힣_.-]', '', filename)
    # 빈 문자열이거나 _만 남은 경우 기본값
    if not filename.strip('_'):
        filename = "강의명없음"
    return filename

def setup_lecture_directory(base_output_dir, lecture_name):
    """최상위 출력 디렉토리 하위에 강의명으로 폴더를 생성하고 경로를 반환합니다."""
    sanitized_lecture_name = sanitize_filename(lecture_name)
    lecture_path = os.path.join(base_output_dir, sanitized_lecture_name)

    print(f"\n--- 강의 저장 디렉토리 설정 ---")
    print(f"기본 출력 디렉토리: {base_output_dir}")
    print(f"강의명 폴더 (정제됨): {sanitized_lecture_name}")
    print(f"최종 강의 저장 경로: {lecture_path}")

    if not os.path.exists(lecture_path):
        try:
            os.makedirs(lecture_path)
            print(f"강의 디렉토리 생성됨: {lecture_path}")
        except OSError as e:
            print(f"오류: 강의 디렉토리 '{lecture_path}' 생성 실패. {e}")
            # 오류 발생 시 진행이 어려우므로 None 반환 또는 예외 발생 고려
            return None 
    return lecture_path

def get_section_filepath(lecture_dir_path, section_name, section_number):
    """강의 디렉토리 내에 저장될 섹션 파일의 전체 경로를 반환합니다."""
    sanitized_section_name = sanitize_filename(section_name)
    # 파일명 중복을 피하기 위해 항상 section_number를 사용
    section_filename = f"{sanitized_section_name}_{section_number}.md"
    return os.path.join(lecture_dir_path, section_filename)

def get_total_filepath(lecture_dir_path, lecture_name):
    """강의 디렉토리 내에 저장될 전체 통합 파일의 경로를 반환합니다."""
    sanitized_lecture_name = sanitize_filename(lecture_name)
    total_filename = f"{sanitized_lecture_name}_total.md"
    return os.path.join(lecture_dir_path, total_filename)

def save_markdown_file(filepath, content):
    """주어진 내용을 Markdown 파일로 저장합니다."""
    try:
        with open(filepath, "w", encoding="utf-8") as md_file:
            md_file.write(content)
        print(f"데이터가 {filepath} 파일로 성공적으로 저장되었습니다.") # 메시지 일반화
        return True
    except Exception as e:
        print(f"파일 저장 중 오류 발생 ({filepath}): {e}")
        return False

if __name__ == '__main__':
    # 테스트용 코드
    test_base_dir = "test_output_lectures"
    test_lecture_name = "초보자를 위한 파이썬 웹 개발 CAMP! (Feat. Django)"
    test_section_name_1 = "1주차: Django 기본기 다지기"
    test_section_name_2 = "Section 2: Advanced Topics & APIs!"

    print("Sanitized lecture name:", sanitize_filename(test_lecture_name))
    print("Sanitized section 1 name:", sanitize_filename(test_section_name_1))
    print("Sanitized section 2 name:", sanitize_filename(test_section_name_2))

    # 1. 강의 디렉토리 설정 테스트
    current_lecture_dir = setup_lecture_directory(test_base_dir, test_lecture_name)
    if current_lecture_dir:
        print(f"생성된 강의 디렉토리: {current_lecture_dir}")

        # 2. 섹션 파일 경로 테스트
        section1_path = get_section_filepath(current_lecture_dir, test_section_name_1, 1)
        section2_path = get_section_filepath(current_lecture_dir, test_section_name_2, 2)
        print(f"섹션 1 파일 경로: {section1_path}")
        print(f"섹션 2 파일 경로: {section2_path}")

        # 3. 통합 파일 경로 테스트
        total_file_path = get_total_filepath(current_lecture_dir, test_lecture_name)
        print(f"통합 파일 경로: {total_file_path}")

        # 4. 파일 저장 테스트 (간단히)
        save_markdown_file(section1_path, f"# {test_section_name_1}\n\n섹션 1 내용입니다.")
        save_markdown_file(total_file_path, f"# {test_lecture_name} 통합본\n\n## {test_section_name_1}\n섹션1 내용...\n## {test_section_name_2}\n섹션2 내용...")

        # 테스트 후 생성된 디렉토리/파일 정리 (선택적)
        # import shutil
        # if os.path.exists(test_base_dir):
        #     shutil.rmtree(test_base_dir)
        #     print(f"테스트 디렉토리 {test_base_dir} 삭제 완료")
    else:
        print("강의 디렉토리 생성 실패로 테스트 중단.") 
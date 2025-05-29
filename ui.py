import tkinter as tk
from tkinter import ttk, messagebox
import os

# .env 파일에서 기본값을 가져오기 시도
try:
    from dotenv import load_dotenv
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    else:
        # ui.py가 프로젝트 루트에 있다고 가정하고 .env 로드 시도 (로컬 테스트용)
        load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env')) 
except ImportError:
    print("python-dotenv 모듈이 설치되지 않았습니다. pip install python-dotenv 실행해주세요.")
    pass 

_execute_scraping_workflow = None

def _import_app_workflow():
    global _execute_scraping_workflow
    if _execute_scraping_workflow is None:
        try:
            from app import execute_scraping_workflow as esw
            _execute_scraping_workflow = esw
        except ImportError as e:
            messagebox.showerror("임포트 오류", f"app 모듈 또는 execute_scraping_workflow 함수를 찾을 수 없습니다: {e}")
            _execute_scraping_workflow = lambda configs: messagebox.showerror("실행 오류", "워크플로우 함수가 로드되지 않았습니다.")
    return _execute_scraping_workflow

class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("인프런 스크립트 추출기")
        # 필드 감소로 높이 조절
        self.root.geometry("450x280") 

        self.config_values = {}

        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('TLabel', font=('Helvetica', 10))
        style.configure('TEntry', font=('Helvetica', 10), padding=5)
        style.configure('TButton', font=('Helvetica', 10, 'bold'), padding=5)
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('Status.TLabel', font=('Helvetica', 9))

        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(main_frame, text="추출 설정", style='Header.TLabel').pack(pady=(0,15))

        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill=tk.X)

        self.email_var = tk.StringVar(value=os.getenv("INFLEARN_EMAIL", ""))
        self.password_var = tk.StringVar(value=os.getenv("INFLEARN_PASSWORD", ""))
        # self.output_dir_var = tk.StringVar(value=os.getenv("OUTPUT_DIR", "output_lecture_scripts")) # 제거
        # self.base_filename_var = tk.StringVar(value=os.getenv("BASE_FILENAME", "lecture_script")) # 제거
        self.course_name_var = tk.StringVar()

        # labels = ["이메일:", "비밀번호:", "저장 폴더명:", "기본 파일명:", "강의명:"] # 수정
        # variables = [self.email_var, self.password_var, self.output_dir_var, self.base_filename_var, self.course_name_var] # 수정
        labels = ["이메일:", "비밀번호:", "강의명:"]
        variables = [self.email_var, self.password_var, self.course_name_var]
        entry_types = ['entry', 'password', 'entry'] # 수정

        for i, (label_text, var, entry_type) in enumerate(zip(labels, variables, entry_types)):
            row_frame = ttk.Frame(fields_frame)
            row_frame.pack(fill=tk.X, pady=3)
            lbl = ttk.Label(row_frame, text=label_text, width=12, anchor="w")
            lbl.pack(side=tk.LEFT, padx=(0,5))
            show_char = '' if entry_type != 'password' else '*'
            entry = ttk.Entry(row_frame, textvariable=var, show=show_char, width=35)
            entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
            if label_text == "강의명:":
                entry.focus_set()

        self.start_button = ttk.Button(main_frame, text="스크립트 추출 시작", command=self.trigger_extraction)
        self.start_button.pack(pady=(20,5), fill=tk.X)
        self.root.bind('<Return>', self.trigger_extraction)
        
        self.status_label = ttk.Label(main_frame, text="", style='Status.TLabel')
        self.status_label.pack(pady=(5,0), fill=tk.X)

    def trigger_extraction(self, event=None):
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        # output_dir = self.output_dir_var.get().strip() # 제거
        # base_filename = self.base_filename_var.get().strip() # 제거
        course_name = self.course_name_var.get().strip()

        # if not all([email, password, output_dir, base_filename, course_name]): # 수정
        if not all([email, password, course_name]):
            messagebox.showerror("입력 오류", "이메일, 비밀번호, 강의명을 모두 입력해주세요.") # 메시지 수정
            return

        self.config_values = {
            "email": email,
            "password": password,
            # "output_dir": output_dir, # 제거
            # "base_filename": base_filename, # 제거
            "course_name": course_name
        }
        
        self.start_button.config(state=tk.DISABLED, text="추출 중...")
        self.status_label.config(text="스크립트 추출 작업을 시작합니다. 잠시만 기다려주세요...")
        self.root.update_idletasks()

        execute_workflow_func = _import_app_workflow()
        try:
            execute_workflow_func(self.config_values)
            messagebox.showinfo("작업 완료", "스크립트 추출 작업이 완료되었습니다. 자세한 내용은 콘솔을 확인하세요.")
        except Exception as e:
            messagebox.showerror("실행 오류", f"스크립트 추출 중 오류가 발생했습니다: {e}")
        finally:
            self.status_label.config(text="작업이 완료되었거나 중단되었습니다.")
            self.start_button.config(state=tk.NORMAL, text="스크립트 추출 시작")

def launch_ui():
    """UI를 실행합니다. 실제 작업은 UI의 시작 버튼을 통해 트리거됩니다."""
    root = tk.Tk()
    AppUI(root)
    root.mainloop()

if __name__ == '__main__':
    print(".env 파일 경로 (ui.py 기준 .env 또는 ../.env):", 
          os.path.join(os.path.dirname(__file__), '.env'), "또는", 
          os.path.join(os.path.dirname(__file__), '..', '.env'))
    print("INFLEARN_EMAIL from os.getenv (ui.py):", os.getenv("INFLEARN_EMAIL"))
    
    launch_ui()
    print("UI가 종료되었습니다.") 
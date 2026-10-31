import numpy as np
from scipy.io.wavfile import write
from PIL import Image
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import threading
import time
import webbrowser
import locale
from pystray import Icon, MenuItem as item, Menu
from PIL import Image as PILImage, ImageDraw
import os
import subprocess
import queue
import winsound  # 用于播放系统声音

# 托盘图标：不依赖外部图片，运行时直接绘制
def create_tray_image():
    size = 64
    image = PILImage.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((4, 4, size - 5, size - 5), fill=(64, 158, 255, 255))
    draw.ellipse((22, 22, size - 23, size - 23), fill=(255, 255, 255, 255))
    return image

tray_image = create_tray_image()

# 定义语言字典
languages = {
    'en': {
        'title': "Image to audio tool - Created by MeowcoQAQ",
        'select_image': "Browse",
        'select_output': "Browse",
        'convert': "Convert",
        'success': "Success",
        'success_msg': "The image has been successfully converted to audio!",
        'error': "Error",
        'error_msg': "An error occurred: ",
        'progress': "Progress",
        'remaining_time': "Remaining Time: ",
        'calculating': "Calculating...",
        'view_on_github': "View source code on GitHub",
        'menu_language': "Language",
        'menu_zh': "简体中文",
        'menu_zh_tw': "繁體中文",
        'menu_en': "English",
        'menu_ja': "日本語",
        'file_types': "Image Files",
        'wav_file': "WAV Files",
        'seconds': "s",
        'close_prompt_title': "Are you sure you want to exit?",
        'close_prompt_message': "Please choose your next action",
        'close': "Exit",
        'background': "Minimize to Tray",
        'cancel': "Cancel",
        'tray_open': "Open",
        'tray_exit': "Exit",
        'open_folder': "Open Folder",
        'rate_warning': "Recommended sample rate is below 50000, and output is below 5 seconds. Higher values may take longer.",
        'rate_error': "The values you entered are too high, which may take a long time. Are you sure you want to continue?",
        'yes': "Yes",
        'no': "No",
        'invalid_output_path': "The output path is invalid or not filled.",
        'invalid_number': "Please enter a valid sample rate and output duration.",
        'no_image_selected': "You have not provided an image to convert.",
        'image_label': "Image (png, jpg, jpeg):",
        'output_label': "Output:",
        'sample_rate_label': "Sample Rate:",
        'duration_label': "Output Duration:"
    },
    'zh': {
        'title': "图片采样工具 - 由喵可QAQ制作",
        'select_image': "浏览",
        'select_output': "浏览",
        'convert': "转换",
        'success': "成功",
        'success_msg': "图像已成功转换为音频！",
        'error': "错误",
        'error_msg': "发生错误：",
        'progress': "进度",
        'remaining_time': "剩余时间: ",
        'calculating': "计算中...",
        'view_on_github': "在 GitHub 上查看源代码",
        'menu_language': "语言",
        'menu_zh': "简体中文",
        'menu_zh_tw': "繁體中文",
        'menu_en': "English",
        'menu_ja': "日本語",
        'file_types': "图像文件",
        'wav_file': "WAV 文件",
        'seconds': "秒",
        'close_prompt_title': "您确定要退出吗？",
        'close_prompt_message': "请选择您接下来的操作",
        'close': "直接退出",
        'background': "最小化到系统托盘",
        'cancel': "取消",
        'tray_open': "打开",
        'tray_exit': "退出",
        'open_folder': "打开文件夹",
        'rate_warning': "建议采样率在50000以内，输出在5秒以内，数值越高等待越久。",
        'rate_error': "您输入的数值过大，可能要等待很久，您确定要继续吗？",
        'yes': "是",
        'no': "否",
        'invalid_output_path': "您输入的路径有误或者未填写。",
        'invalid_number': "请输入有效的采样率和输出秒数。",
        'no_image_selected': "您尚未提供需要转换的图片。",
        'image_label': "图像（png、jpg、jpeg）：",
        'output_label': "导出：",
        'sample_rate_label': "采样率：",
        'duration_label': "输出秒数："
    },
    'zh_tw': {
        'title': "圖片轉音頻工具 - 由喵可QAQ製作",
        'select_image': "瀏覽",
        'select_output': "瀏覽",
        'convert': "轉換",
        'success': "成功",
        'success_msg': "圖片已成功轉換為音頻！",
        'error': "錯誤",
        'error_msg': "發生錯誤：",
        'progress': "進度",
        'remaining_time': "剩餘時間: ",
        'calculating': "計算中...",
        'view_on_github': "在 GitHub 上查看源代碼",
        'menu_language': "語言",
        'menu_zh': "简体中文",
        'menu_zh_tw': "繁體中文",
        'menu_en': "English",
        'menu_ja': "日本語",
        'file_types': "圖像文件",
        'wav_file': "WAV 文件",
        'seconds': "秒",
        'close_prompt_title': "您確定要退出嗎？",
        'close_prompt_message': "請選擇您接下來的操作",
        'close': "直接退出",
        'background': "最小化到系統托盤",
        'cancel': "取消",
        'tray_open': "打開",
        'tray_exit': "退出",
        'open_folder': "打開文件夾",
        'rate_warning': "建議采樣率在50000以內，輸出在5秒以內，數值越高等待越久。",
        'rate_error': "您輸入的數值過大，可能要等待很久，您確定要繼續嗎？",
        'yes': "是",
        'no': "否",
        'invalid_output_path': "您輸入的路徑有誤或者未填寫。",
        'invalid_number': "請輸入有效的取樣率和輸出秒數。",
        'no_image_selected': "您尚未提供需要轉換的圖片。",
        'image_label': "圖像（png、jpg、jpeg）：",
        'output_label': "導出：",
        'sample_rate_label': "采樣率：",
        'duration_label': "輸出秒數："
    },
    'ja': {
        'title': "画像から音声へのツール - ねこかわ作成",
        'select_image': "ブラウズ",
        'select_output': "ブラウズ",
        'convert': "変換",
        'success': "成功",
        'success_msg': "画像が音声に正常に変換されました！",
        'error': "エラー",
        'error_msg': "エラーが発生しました：",
        'progress': "進捗",
        'remaining_time': "残り時間：",
        'calculating': "計算中...",
        'view_on_github': "GitHubでソースコードを表示",
        'menu_language': "言語",
        'menu_zh': "简体中文",
        'menu_zh_tw': "繁體中文",
        'menu_en': "English",
        'menu_ja': "日本語",
        'file_types': "画像ファイル",
        'wav_file': "WAV ファイル",
        'seconds': "秒",
        'close_prompt_title': "本当に終了しますか？",
        'close_prompt_message': "次の操作を選択してください",
        'close': "終了",
        'background': "トレイに最小化",
        'cancel': "キャンセル",
        'tray_open': "開く",
        'tray_exit': "終了",
        'open_folder': "フォルダーを開く",
        'rate_warning': "推奨サンプリングレートは50000以下、出力は5秒以下です。より高い値はより長くかかる可能性があります。",
        'rate_error': "入力された値が高すぎます。続行しますか？",
        'yes': "はい",
        'no': "いいえ",
        'invalid_output_path': "出力パスが無効か未入力です。",
        'invalid_number': "有効なサンプリングレートと出力秒数を入力してください。",
        'no_image_selected': "変換する画像が提供されていません。",
        'image_label': "画像（png、jpg、jpeg）：",
        'output_label': "出力：",
        'sample_rate_label': "サンプリングレート：",
        'duration_label': "出力秒数："
    }
}

# 检测系统语言
def detect_language():
    lang, _ = locale.getdefaultlocale()
    if lang and ('zh' in lang):
        return 'zh'
    elif lang and ('ja' in lang):
        return 'ja'
    else:
        return 'en'

# 当前语言
current_language = detect_language()

# 工作状态标志
is_working = False

# 默认输出文件夹路径
default_output_folder = os.path.join(os.getcwd(), "image-to-audio")

# 创建默认输出文件夹
if not os.path.exists(default_output_folder):
    os.makedirs(default_output_folder)

def set_language(lang):
    global current_language
    current_language = lang
    root.title(languages[current_language]['title'])
    select_image_button.config(text=languages[current_language]['select_image'])
    select_output_button.config(text=languages[current_language]['select_output'])
    convert_button.config(text=languages[current_language]['convert'])
    progress_label.config(text="0.00%")
    time_label.config(text=languages[current_language]['remaining_time'] + languages[current_language]['calculating'])
    link_label.config(text=languages[current_language]['view_on_github'])
    rate_warning_label.config(text=languages[current_language]['rate_warning'])
    sample_rate_label.config(text=languages[current_language]['sample_rate_label'])
    duration_label.config(text=languages[current_language]['duration_label'])
    image_label.config(text=languages[current_language]['image_label'])
    output_label.config(text=languages[current_language]['output_label'])
    # 更新菜单
    menu_bar.entryconfig(0, label=languages[current_language]['menu_language'])
    language_menu.entryconfig(0, label=languages[current_language]['menu_zh'])
    language_menu.entryconfig(1, label=languages[current_language]['menu_zh_tw'])
    language_menu.entryconfig(2, label=languages[current_language]['menu_en'])
    language_menu.entryconfig(3, label=languages[current_language]['menu_ja'])
    # 同步托盘菜单文案
    if tray_icon is not None:
        tray_icon.menu = build_tray_menu()

def show_custom_messagebox(title, message, output_path=None, is_error=False):
    dialog = tk.Toplevel(root)
    dialog.title(title)
    dialog.geometry("300x150")
    dialog.transient(root)
    dialog.grab_set()

    # 播放系统自带提示音（信息/警告）
    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION if is_error else winsound.MB_ICONASTERISK)

    # 居中到程序窗口
    dialog.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")

    content = tk.Frame(dialog)
    content.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

    # 蓝色信息图标（出现错误时用红色感叹号）
    icon_canvas = tk.Canvas(content, width=32, height=32, highlightthickness=0)
    icon_canvas.pack(side=tk.LEFT, padx=(0, 10))
    icon_canvas.create_oval(1, 1, 31, 31, fill="#e81123" if is_error else "#0078d4", outline="")
    icon_canvas.create_text(16, 17, text="!" if is_error else "i", fill="white",
                            font=("Segoe UI", 16, "bold"))

    tk.Label(content, text=message, fg='red' if is_error else 'black',
             wraplength=210, justify=tk.LEFT).pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=(0, 10))

    ttk.Button(button_frame, text="OK", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    if output_path:
        def open_folder():
            subprocess.run(f'explorer /select,"{output_path}"')
            dialog.destroy()

        ttk.Button(button_frame, text=languages[current_language]['open_folder'], command=open_folder).pack(side=tk.LEFT, padx=5)

def show_warning_dialog(callback):
    dialog = tk.Toplevel(root)
    dialog.title(languages[current_language]['error'])
    dialog.geometry("300x150")
    dialog.transient(root)
    dialog.grab_set()

    tk.Label(dialog, text=languages[current_language]['rate_error'], fg='black').pack(pady=10)

    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=10)

    def on_yes():
        dialog.destroy()
        callback()

    def on_no():
        dialog.destroy()

    ttk.Button(button_frame, text=languages[current_language]['yes'], command=on_yes).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text=languages[current_language]['no'], command=on_no).pack(side=tk.LEFT, padx=5)

    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)  # 播放系统声音

# 灰度按对数映射到的频率范围（Hz）：下限 A1(55Hz)，上限不超过 20kHz 且受采样率限制
FREQUENCY_FLOOR = 55.0
FREQUENCY_CEILING = 20000.0

# 归一化后的目标峰值，留一点余量避免播放端削波
NORMALIZE_PEAK = 0.95

# 首尾淡入淡出时长（秒），避免波形被硬截断产生爆音
FADE_SECONDS = 0.01

# 后台线程只往队列里投递界面任务，由主线程定时取出执行，避免跨线程操作 Tk
ui_queue = queue.Queue()

def post_to_ui(func, *args):
    ui_queue.put((func, args))

def pump_ui_queue():
    while True:
        try:
            func, args = ui_queue.get_nowait()
        except queue.Empty:
            break
        func(*args)
    root.after(100, pump_ui_queue)

def update_progress(progress_var, progress_label, time_label, progress, start_time):
    progress_var.set(progress)
    progress_label.config(text=f"{progress:.2f}%")
    if 0 < progress < 100:
        elapsed_time = time.time() - start_time
        remaining_time = elapsed_time / (progress / 100) - elapsed_time
        remaining_time_text = f"{languages[current_language]['remaining_time']}{remaining_time:.2f} {languages[current_language]['seconds']}"
        time_label.config(text=remaining_time_text)

def convert_image_to_audio(image_path, output_path, progress_var, progress_label, time_label, sample_rate, duration):
    global is_working
    is_working = True
    try:
        start_time = time.time()
        image = Image.open(image_path).convert('L')
        data = np.asarray(image)
        num_samples = int(sample_rate * duration)

        # 相同灰度值对应相同频率，先统计每种灰度出现的次数，
        # 每种频率的正弦只需计算一次再乘权重，避免逐像素计算（O(像素数×采样点数) → O(256×采样点数)）
        counts = np.bincount(data.ravel(), minlength=256)
        values = np.nonzero(counts)[0]
        # 超过采样率一半的频率会混叠成刺耳的“滋滋”声，所以上限压在奈奎斯特以内；
        # 灰度按对数（八度等分）映射，音高更接近乐器，中灰落在几百 Hz 而不是几 kHz
        max_frequency = min(FREQUENCY_CEILING, sample_rate * 0.45)
        frequencies = FREQUENCY_FLOOR * np.power(max_frequency / FREQUENCY_FLOOR, values / 255.0)
        weights = counts[values].astype(np.float64)

        t = np.linspace(0, duration, num_samples, endpoint=False)
        audio = np.zeros(num_samples, dtype=np.float64)
        # 单块数据量控制在 8M 个 double 以内，避免大采样率/长时长下占用过多内存
        block_size = max(1, min(16, 8_000_000 // max(1, num_samples)))
        num_blocks = max(1, (len(frequencies) + block_size - 1) // block_size)

        for i in range(num_blocks):
            start = i * block_size
            end = min((i + 1) * block_size, len(frequencies))
            block_audio = np.sin(2 * np.pi * frequencies[start:end, None] * t)
            audio += (block_audio * weights[start:end, None]).sum(axis=0)
            post_to_ui(update_progress, progress_var, progress_label, time_label,
                       (i + 1) / num_blocks * 100, start_time)

        # 首尾各做一段淡入淡出，避免波形被硬截断产生爆音
        fade_len = min(num_samples // 2, int(sample_rate * FADE_SECONDS))
        if fade_len > 0:
            ramp = np.linspace(0.0, 1.0, fade_len)
            audio[:fade_len] *= ramp
            audio[-fade_len:] *= ramp[::-1]

        # 归一化：多种频率叠加后峰值可能远超满量程，不处理会让播放器削波失真
        peak = np.max(np.abs(audio))
        if peak > 0:
            audio *= NORMALIZE_PEAK / peak

        # 输出 16bit PCM：兼容性最好，避免部分播放器解析浮点 WAV 时出现杂音
        write(output_path, sample_rate, np.round(audio * 32767).astype(np.int16))
        post_to_ui(update_progress, progress_var, progress_label, time_label, 100.0, start_time)
        post_to_ui(show_custom_messagebox, languages[current_language]['success'],
                   languages[current_language]['success_msg'], output_path)
    except Exception as e:
        post_to_ui(show_custom_messagebox, languages[current_language]['error'],
                   languages[current_language]['error_msg'] + str(e), None, True)
    finally:
        is_working = False

def select_image():
    file_path = filedialog.askopenfilename(filetypes=[(languages[current_language]['file_types'], "*.png;*.jpg;*.jpeg")])
    if file_path:
        image_path_entry.delete(0, tk.END)
        image_path_entry.insert(0, file_path)

def select_output_path():
    file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[(languages[current_language]['wav_file'], "*.wav")], initialdir=default_output_folder)
    if file_path:
        output_path_entry.delete(0, tk.END)
        output_path_entry.insert(0, file_path)

def validate_and_convert():
    try:
        sample_rate = int(sample_rate_entry.get())
        duration = int(duration_entry.get())
    except ValueError:
        show_custom_messagebox(languages[current_language]['error'], languages[current_language]['invalid_number'], is_error=True)
        return
    image_path = image_path_entry.get()
    output_path = output_path_entry.get()

    if not image_path:
        show_custom_messagebox(languages[current_language]['error'], languages[current_language]['no_image_selected'], is_error=True)
        return

    if not output_path:
        show_custom_messagebox(languages[current_language]['error'], languages[current_language]['invalid_output_path'], is_error=True)
        return

    def start_conversion():
        progress_var.set(0)
        progress_label.config(text="0.00%")
        time_label.config(text=languages[current_language]['remaining_time'] + languages[current_language]['calculating'])
        threading.Thread(target=convert_image_to_audio, args=(image_path, output_path, progress_var, progress_label, time_label, sample_rate, duration)).start()

    if sample_rate > 50000 or duration > 5:
        show_warning_dialog(start_conversion)
    else:
        start_conversion()

def open_github_link(event):
    webbrowser.open_new("https://github.com/azdyqwo/image-to-audio-python")

def on_closing():
    if not is_working:
        quit_app()
    else:
        root.bell()

        dialog = tk.Toplevel(root)
        dialog.title(languages[current_language]['close_prompt_title'])
        dialog.geometry("300x150")
        dialog.transient(root)
        dialog.grab_set()

        dialog.update_idletasks()
        x = root.winfo_x() + (root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = root.winfo_y() + (root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        tk.Label(dialog, text=languages[current_language]['close_prompt_message']).pack(pady=10)

        button_frame = tk.Frame(dialog)
        button_frame.pack(expand=True)

        def close_app():
            dialog.destroy()
            quit_app()

        def minimize_to_tray():
            dialog.destroy()
            root.withdraw()
            start_tray()

        ttk.Button(button_frame, text=languages[current_language]['close'], command=close_app).pack(side=tk.LEFT, padx=10, pady=10)
        ttk.Button(button_frame, text=languages[current_language]['background'], command=minimize_to_tray).pack(side=tk.LEFT, padx=10, pady=10)
        ttk.Button(button_frame, text=languages[current_language]['cancel'], command=dialog.destroy).pack(side=tk.LEFT, padx=10, pady=10)

# 系统托盘：pystray 的 run() 会阻塞，必须放到后台线程，回调里经 ui_queue 回到主线程
tray_icon = None

def build_tray_menu():
    return Menu(
        item(languages[current_language]['tray_open'], on_tray_open, default=True),
        item(languages[current_language]['tray_exit'], on_tray_exit),
    )

def on_tray_open(icon=None, item=None):
    # 托盘回调运行在托盘线程，同样经队列交给主线程执行
    post_to_ui(restore_window)

def on_tray_exit(icon=None, item=None):
    post_to_ui(quit_app)

def restore_window():
    root.deiconify()
    root.lift()
    root.focus_force()

def start_tray():
    """首次最小化到托盘时创建托盘图标，之后复用同一个。"""
    global tray_icon
    if tray_icon is not None:
        return
    tray_icon = Icon("image_to_audio", tray_image, "Image to Audio", build_tray_menu())
    threading.Thread(target=tray_icon.run, daemon=True).start()

def stop_tray():
    global tray_icon
    if tray_icon is None:
        return
    icon, tray_icon = tray_icon, None
    icon.stop()

def quit_app():
    stop_tray()
    root.quit()

root = tk.Tk()
root.title(languages[current_language]['title'])

# 设置窗口不可调整大小和最大化
root.resizable(False, False)

# 设置窗口宽度为450，高度自适应
root.geometry("450x500")
root.update_idletasks()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
size = tuple(int(_) for _ in root.geometry().split('+')[0].split('x'))
x = screen_width // 2 - size[0] // 2
y = screen_height // 2 - size[1] // 2
root.geometry(f"{size[0]}x{size[1]}+{x}+{y}")

# 创建菜单栏（tearoff=0 否则索引 0 是可撕下条目，切换语言时 entryconfig 会报错）
menu_bar = tk.Menu(root, tearoff=0)
root.config(menu=menu_bar)

# 创建语言菜单
language_menu = tk.Menu(menu_bar, tearoff=0)
language_menu.add_command(label=languages[current_language]['menu_zh'], command=lambda: set_language('zh'))
language_menu.add_command(label=languages[current_language]['menu_zh_tw'], command=lambda: set_language('zh_tw'))
language_menu.add_command(label=languages[current_language]['menu_en'], command=lambda: set_language('en'))
language_menu.add_command(label=languages[current_language]['menu_ja'], command=lambda: set_language('ja'))
menu_bar.add_cascade(label=languages[current_language]['menu_language'], menu=language_menu)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(pady=10, fill=tk.X, padx=20)

progress_label = tk.Label(root, text="0.00%")
progress_label.pack()

time_label = tk.Label(root, text=languages[current_language]['remaining_time'] + languages[current_language]['calculating'])
time_label.pack()

# 添加采样率和输出秒数输入框
sample_rate_label = tk.Label(root, text=languages[current_language]['sample_rate_label'])
sample_rate_label.pack()
sample_rate_entry = tk.Entry(root)
sample_rate_entry.insert(0, "20000")  # 默认值
sample_rate_entry.pack()

duration_label = tk.Label(root, text=languages[current_language]['duration_label'])
duration_label.pack()
duration_entry = tk.Entry(root)
duration_entry.insert(0, "5")  # 默认值
duration_entry.pack()

rate_warning_label = tk.Label(root, text=languages[current_language]['rate_warning'], fg='red')
rate_warning_label.pack()

# 图片选择路径
image_label = tk.Label(root, text=languages[current_language]['image_label'], anchor='w')
image_label.pack(fill=tk.X, padx=20)

image_frame = tk.Frame(root)
image_frame.pack(pady=5, padx=20, fill=tk.X)

image_path_entry = tk.Entry(image_frame)
image_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

select_image_button = ttk.Button(image_frame, text=languages[current_language]['select_image'], command=select_image)
select_image_button.pack(side=tk.RIGHT)

# 输出路径选择
output_label = tk.Label(root, text=languages[current_language]['output_label'], anchor='w')
output_label.pack(fill=tk.X, padx=20)

output_frame = tk.Frame(root)
output_frame.pack(pady=5, padx=20, fill=tk.X)

output_path_entry = tk.Entry(output_frame)
output_path_entry.insert(0, os.path.join(default_output_folder, "output.wav"))  # 设置默认输出路径为当前目录下的 image-to-audio 文件夹
output_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

select_output_button = ttk.Button(output_frame, text=languages[current_language]['select_output'], command=select_output_path)
select_output_button.pack(side=tk.RIGHT)

convert_button = ttk.Button(root, text=languages[current_language]['convert'], command=validate_and_convert)
convert_button.pack(pady=20)

link_label = tk.Label(root, text=languages[current_language]['view_on_github'], fg="blue", cursor="hand2")
link_label.pack(pady=10)
link_label.bind("<Button-1>", open_github_link)

root.protocol("WM_DELETE_WINDOW", on_closing)

# 启动界面任务泵，后台线程的进度/弹窗都靠它回到主线程执行
root.after(100, pump_ui_queue)

root.mainloop()
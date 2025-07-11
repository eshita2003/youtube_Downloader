from pytubefix import YouTube
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
# //start
# --- Functions ---
yt_video = None

def fetch_thumbnail():
    global yt_video
    url = url_entry.get()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL")
        return

    try:
        yt = YouTube(url)
        thumbnail_url = yt.thumbnail_url

        response = requests.get(thumbnail_url)
        img_data = BytesIO(response.content)
        img = Image.open(img_data).resize((320, 180))  # Resize for GUI
        photo = ImageTk.PhotoImage(img)

        thumbnail_label.config(image=photo)
        thumbnail_label.image = photo  # Save reference

        root.geometry("600x600")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch thumbnail:\n{e}")


def start_download():
    thread = threading.Thread(target=download_video)
    thread.start()

def download_video():
    global yt_video
    url = url_entry.get()
    save_path = path_label["text"]
    choice = download_choice.get()

    if not url or not save_path or save_path == "No folder selected":
        messagebox.showerror("Error", "Please provide both URL and folder")
        return

    try:
        yt = YouTube(
            url,
            on_progress_callback=progress_function
        )

        if choice == "Video":
            stream = yt.streams.filter(progressive=True, file_extension="mp4").get_highest_resolution()
        else:
            stream = yt.streams.filter(only_audio=True).first()

        progress_bar["value"] = 0
        status_label.config(text="Downloading...")

        stream.download(output_path=save_path)
        status_label.config(text="Download complete!")
        messagebox.showinfo("Success", "Download completed successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Download failed:\n{e}")
        status_label.config(text="Error")


def progress_function(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage = (bytes_downloaded / total_size) * 100
    progress_bar["value"] = percentage
    root.update_idletasks()


def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        path_label.config(text=folder_selected)

# --- GUI Setup ---

root = tk.Tk()
root.title("YouTube Video Downloader")
root.geometry("600x500")
root.resizable(False, False)

# --- URL input ---
tk.Label(root, text="YouTube URL:").pack(pady=5)
url_entry = tk.Entry(root, width=70)
url_entry.pack(pady=5)

tk.Button(root, text="Fetch Thumbnail", command=fetch_thumbnail).pack(pady=5)

# --- Thumbnail Preview ---
thumbnail_label = tk.Label(root)
thumbnail_label.pack(pady=10)

# --- Folder selection ---
tk.Button(root, text="Select Folder", command=select_folder).pack(pady=5)
path_label = tk.Label(root, text="No folder selected", fg="gray")
path_label.pack(pady=5)

# --- Download type ---
tk.Label(root, text="Download Type:").pack(pady=5)
download_choice = ttk.Combobox(root, values=["Video", "Audio only"])
download_choice.current(0)
download_choice.pack(pady=5)

# --- Download Button ---
tk.Button(root, text="Download", command=start_download, bg="green", fg="white").pack(pady=15)

# --- Progress Bar ---
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

status_label = tk.Label(root, text="", fg="blue")
status_label.pack()

# --- Run App ---
root.mainloop()

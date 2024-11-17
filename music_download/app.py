import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
import os
from datetime import datetime

# Configurações do Spotify API (insira suas credenciais aqui)
SPOTIFY_CLIENT_ID = ''
SPOTIFY_CLIENT_SECRET = ''

class MusicDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Downloader")
        self.root.geometry("700x600")  # Aumentado para acomodar o histórico
        self.root.resizable(False, False)

        # Definindo a pasta padrão de download
        self.default_folder = os.path.expanduser("~/Music")
        if not os.path.exists(self.default_folder):
            os.makedirs(self.default_folder)
        self.download_folder = self.default_folder  # Variável para armazenar o diretório de download
        self.download_history = []  # Lista para armazenar o histórico de downloads
        self.current_filename = ""  # Variável para armazenar o nome do arquivo convertido
        self.current_platform = ""  # Variável para armazenar a plataforma atual

        # Inicializando cliente Spotify
        self.spotify_client = self.init_spotify_client()

        # Layout usando grid
        self.create_widgets()

    def create_widgets(self):
        # Configurando estilo
        style = ttk.Style()
        style.configure('TLabel', font=('Helvetica', 12))
        style.configure('TButton', font=('Helvetica', 12), padding=6)
        style.configure('TCombobox', font=('Helvetica', 12))

        # Configurando grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_rowconfigure(4, weight=1)
        self.root.grid_rowconfigure(5, weight=1)
        self.root.grid_rowconfigure(6, weight=1)  # Linha para o histórico
        self.root.grid_rowconfigure(7, weight=0)  # Linha para o rodapé

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Campo de entrada para URL ou Nome
        self.entry_label = ttk.Label(self.root, text="Insira o URL ou Nome:")
        self.entry_label.grid(row=0, column=0, padx=20, pady=10, sticky='w')

        self.entry = tk.Entry(self.root, width=50, font=('Helvetica', 12))
        self.entry.grid(row=0, column=1, padx=20, pady=10, sticky='ew')

        # Botões para escolher Spotify ou YouTube
        self.platform = tk.StringVar(value="Spotify")
        self.radio_spotify = ttk.Radiobutton(self.root, text="Spotify", variable=self.platform, value="Spotify")
        self.radio_youtube = ttk.Radiobutton(self.root, text="YouTube", variable=self.platform, value="YouTube")
        self.radio_spotify.grid(row=1, column=0, padx=20, pady=5, sticky='w')
        self.radio_youtube.grid(row=1, column=1, padx=20, pady=5, sticky='w')

        # Botão para escolher diretório de download
        self.folder_button = ttk.Button(self.root, text="Escolher Pasta", command=self.choose_folder)
        self.folder_button.grid(row=2, column=0, padx=20, pady=10, sticky='ew')

        self.folder_label = ttk.Label(self.root, text=f"Pasta de Download: {self.download_folder}")
        self.folder_label.grid(row=2, column=1, padx=20, pady=10, sticky='w')

        # Botão para iniciar o download
        self.download_button = ttk.Button(self.root, text="Iniciar Download", command=self.start_download)
        self.download_button.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky='ew')

        # Status de download
        self.status_label = ttk.Label(self.root, text="", font=('Helvetica', 12))
        self.status_label.grid(row=4, column=0, columnspan=2, padx=20, pady=10, sticky='w')

        # Lista de histórico de downloads
        self.history_label = ttk.Label(self.root, text="Histórico de Downloads:")
        self.history_label.grid(row=5, column=0, columnspan=2, padx=20, pady=10, sticky='w')

        self.history_listbox = tk.Listbox(self.root, width=90, height=15, font=('Helvetica', 10))
        self.history_listbox.grid(row=6, column=0, columnspan=2, padx=20, pady=10, sticky='ew')

        # Rodapé
        self.footer_label = ttk.Label(self.root, text="© 2024 Derik. Todos os direitos reservados.", font=('Helvetica', 10))
        self.footer_label.grid(row=7, column=0, columnspan=2, padx=20, pady=10, sticky='s')

    def init_spotify_client(self):
        try:
            client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
            return spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao inicializar Spotify: {e}")
            return None

    def choose_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.download_folder = folder_selected
            self.folder_label.config(text=f"Pasta de Download: {self.download_folder}")

    def start_download(self):
        download_input = self.entry.get()
        if not download_input:
            messagebox.showwarning("Erro", "Por favor, insira o URL ou Nome da música.")
            return

        if not self.download_folder:
            messagebox.showwarning("Erro", "Por favor, escolha a pasta de download.")
            return

        self.status_label.config(text="Baixando...")

        if self.platform.get() == "Spotify":
            self.current_platform = "Spotify"
            self.download_from_spotify(download_input)
        else:
            self.current_platform = "YouTube"
            self.download_from_youtube(download_input)

    def download_from_spotify(self, search_input):
        try:
            # Buscar a música no Spotify
            results = self.spotify_client.search(q=search_input, type='track', limit=1)
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                track_name = track['name']
                artist_name = track['artists'][0]['name']
                search_query = f"{track_name} {artist_name}"

                # Buscar no YouTube
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': f'{self.download_folder}/%(title)s.%(ext)s',
                    'default_search': 'ytsearch',
                    'progress_hooks': [self.progress_hook],
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([search_query])

            else:
                messagebox.showerror("Erro", "Música não encontrada no Spotify.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao baixar do Spotify: {e}")

    def download_from_youtube(self, search_input):
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': f'{self.download_folder}/%(title)s.%(ext)s',
                'default_search': 'ytsearch1',
                'progress_hooks': [self.progress_hook],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([search_input])

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao baixar do YouTube: {e}")

    def progress_hook(self, d):
        if d['status'] == 'finished':
            # Atualizar o nome do arquivo convertido
            self.current_filename = os.path.basename(d['filename']).replace('.webm', '.mp3')
            # Chamar o método para garantir que o histórico só registre o arquivo convertido
            self.download_complete(self.current_platform)

    def download_complete(self, platform):
        self.status_label.config(text="Download Concluído!")
        self.entry.delete(0, tk.END)  # Limpar o campo de entrada

        # Adicionar ao histórico
        download_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.download_history.append({
            'time': download_time,
            'filename': self.current_filename,
            'platform': platform
        })
        self.update_history_listbox()

    def update_history_listbox(self):
        self.history_listbox.delete(0, tk.END)
        for record in self.download_history:
            self.history_listbox.insert(tk.END, f"{record['time']} - {record['filename']} ({record['platform']})")

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicDownloaderApp(root)
    root.mainloop()

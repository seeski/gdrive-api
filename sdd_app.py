from __future__ import print_function
import tkinter as tk
from tkinter import ttk
import pickle
import os.path
import io
import shutil
import requests
from mimetypes import MimeTypes
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload


class DriveAPI:
    global SCOPES

    SCOPES = ['https://www.googleapis.com/auth/drive']

    def __init__(self):

        self.creds = None

        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:

            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('drive', 'v3',credentials=self.creds)

        results = self.service.files().list(
            pageSize=100, fields="files(id, name)").execute()
        self.items = results.get('files', [])


    def FileDownload(self, file_id, file_name):
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()

        downloader = MediaIoBaseDownload(fh, request, chunksize=204800)
        done = False

        try:
            while not done:
                status, done = downloader.next_chunk()

            fh.seek(0)

            with open(file_name, 'wb') as f:
                shutil.copyfileobj(fh, f)

            print(f"{file_name} File Downloaded")
            return True

        except:
            print("Something went wrong.")
            return False


class App:

    def __init__(self):
        self.win = tk.Tk()

        self.win.title = 'SDD UI'
        self.win.geometry = '200x200'
        self.win.resizable(width=False, height=False)
        self.filetypes = [
            'E2OFF',
            'SCROFF',
            'DPFOFF',
            'EGROFF',
            'tuning',
            'stop/start_off',
            "tuning_egroff",
            "tuning_e2",
            "tuning_dpfoff",
            "tuning_egroff_dpfoff",
            'egroff_dpfoff',
            'egroff_dpfoff_scroff',
            'tuning_egroff_dpfoff_scroff',
        ]

        self.frame1 = tk.Frame(self.win, width=245, height=100)
        self.frame1.grid(row=0, column=0)
        self.create_labels()
        self.create_buttons()
        self.drive = DriveAPI()
        self.win.mainloop()

    def create_labels(self):
        self.filetype_label = tk.Label(self.frame1, text='filetype:', pady=10, padx=10)
        self.filetype_label.place(x=5, y=10)

    def create_buttons(self):
        self.filetype_choice = ttk.Combobox(self.frame1, values=self.filetypes)
        self.submit_button = tk.Button(self.frame1, text='Submit', command=self.submit_command)

        self.filetype_choice.place(x=80, y=18)
        self.submit_button.place(x=171, y=60)

    def submit_command(self):
        for item in self.drive.items:
            if f"{self.filetype_choice.get()}.vbf" == item['name'].split('__')[-1]:
                self.drive.FileDownload(file_id=item['id'], file_name=item['name'])


new = App()
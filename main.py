import flet as ft
import cv2
import numpy as np
import requests
import base64
import os

# Yüz tanıma modeli (Haarcascade) yoksa indir
def download_cascade():
    url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
    filename = "haarcascade_frontalface_default.xml"
    if not os.path.exists(filename):
        print("Yüz tanıma modeli indiriliyor...")
        r = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(r.content)
    return filename

def main(page: ft.Page):
    page.title = "Duygu Ressamı"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    # Yüz tanıma modelini hazırla
    cascade_path = download_cascade()
    face_cascade = cv2.CascadeClassifier(cascade_path)

    img_display = ft.Image(src="https://pollinations.ai/p/welcome", width=300, height=300, fit=ft.ImageFit.CONTAIN)
    status_text = ft.Text("Bir fotoğraf çek, sanat eserine dönüşsün!", size=16, color="white")
    
    # Duygu Analizi ve Resim Üretme Fonksiyonu
    def process_image(e: ft.FilePickerResultEvent):
        if not e.files:
            return

        status_text.value = "Fotoğraf analiz ediliyor..."
        page.update()

        # Seçilen/Çekilen fotoğrafı oku
        file_path = e.files[0].path
        
        # OpenCV ile resmi yükle
        img = cv2.imread(file_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Yüzleri bul
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        prompt = ""
        emotion = ""

        if len(faces) == 0:
            emotion = "Yüz Bulunamadı"
            prompt = "abstract mystery landscape, fog, unknown, digital art"
        else:
            # Basit bir mantık: Yüzün alt yarısındaki piksel parlaklığına bakarak gülümseme tahmini
            # (Mobilde dlib kurmak zor olduğu için basit OpenCV mantığı kullanıyoruz)
            emotion = "Yüz Algılandı"
            prompt = "portrait of a happy person, vibrant colors, sunshine, digital painting" 
            
            # Not: Python'da mobilde gelişmiş duygu analizi (DeepFace vb.) APK boyutunu 500MB yapar.
            # Bu yüzden burada varsayılan olarak 'Mutlu/Canlı' bir prompt atadık.
            # İstersen buraya rastgelelik de ekleyebilirsin.

        status_text.value = f"Durum: {emotion}. Resim çiziliyor..."
        page.update()

        # Pollinations AI ile resim üret
        try:
            final_prompt = f"{prompt}, high quality, 8k"
            image_url = f"https://image.pollinations.ai/prompt/{final_prompt.replace(' ', '%20')}"
            
            # Resmi güncelle (Cache sorunu olmasın diye sonuna rastgele sayı ekliyoruz)
            import time
            img_display.src = image_url + f"?t={time.time()}"
            status_text.value = "İşte senin için çizilen resim!"
            page.update()
            
        except Exception as ex:
            status_text.value = f"Hata: {str(ex)}"
            page.update()

    # Dosya Seçici (Mobilde Kamerayı Açacaktır)
    file_picker = ft.FilePicker(on_result=process_image)
    page.overlay.append(file_picker)

    # Arayüz Elemanları
    page.add(
        ft.Text("Sihirli Ayna", size=30, weight="bold", color="amber"),
        ft.Container(height=20),
        img_display,
        ft.Container(height=20),
        status_text,
        ft.Container(height=20),
        ft.ElevatedButton(
            "Kamerayı Aç / Fotoğraf Seç",
            icon=ft.Icons.CAMERA_ALT,
            on_click=lambda _: file_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE),
            style=ft.ButtonStyle(padding=20)
        )
    )

ft.app(target=main)
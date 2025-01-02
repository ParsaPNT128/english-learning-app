import nltk
from nltk.corpus import wordnet as wn
from tkinter import *
from tkinter import ttk
from tkinter import messagebox, PhotoImage, scrolledtext, filedialog
import tkinter as tk
import random
import speech_recognition as sr
import pyttsx3
import sqlite3
import re
import random
import os
from PIL import ImageTk, Image
import shutil
#nltk.download('wordnet')

# main window
engine = pyttsx3.init()
root = tk.Tk()
root.title('English Application')
root.geometry('800x550')
root.resizable(False, False)

dark_mode = False

connection = sqlite3.connect("user_data.db")
cursor = connection.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users
               (username TEXT PRIMARY KEY, password TEXT NOT NULL, email TEXT NOT NULL, picture TEXT NO NULL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS notebook
                (username TEXT, word TEXT, word_info TEXT, FOREIGN KEY (username) REFERENCES users(username))''')

connection.commit()

def resize_image(image: Image, length: int) -> Image:
    if image.size[0] < image.size[1]:
        resized_image = image.resize((length, int(image.size[1] * (length / image.size[0]))))
        required_loss = (resized_image.size[1] - length)
        resized_image = resized_image.crop(
            box=(0, required_loss / 2, length, resized_image.size[1] - required_loss / 2))

        return resized_image
    else:
        resized_image = image.resize((int(image.size[0] * (length / image.size[1])), length))
        required_loss = resized_image.size[0] - length

        resized_image = resized_image.crop(
            box=(required_loss / 2, 0, resized_image.size[0] - required_loss / 2, length))

        return resized_image

def register_user():
    global pfp_label, pfp_image
    username = register_username_entry.get().strip()
    password = register_password_entry.get().strip()
    email = email_entry.get().strip()
    if not username or not password or not email:
        messagebox.showerror('Input Error', 'All fields are required.')
        return
    if not username.isalnum():
        messagebox.showerror('Input Error', 'Username must contain only letters and numbers')

    if not password.isalnum():
        messagebox.showerror('Input Error', 'Password must contain only letters and numbers')

    if not re.match(r"^\S+@\S+\.\S+$", email):
        messagebox.showerror('Input Error', 'Invalid email format')

    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        messagebox.showerror('Registeration Error', 'Username already exists')

    cursor.execute('INSERT INTO users (username, password, email, picture) VALUES (?, ?, ?, ?)', (username, password, email, 'default.jpg'))

    connection.commit()

    pfp_image = PhotoImage(file='profiles/default.jpg')
    pfp_image = pfp_image.subsample(8, 8)
    pfp_label = tk.Label(nav_bar_frame, image=pfp_image)

    pfp_label.pack(side='right', padx=10, pady=5)
    account_button.pack(side='right', pady=5)

    messagebox.showinfo('Success', 'Rgisteration successful you can now login')

    open_frame(login_frame)

def login_user():
    global pfp_label, pfp_image
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        messagebox.showerror('Input Error', 'All fields are required.')
        return
    
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()

    if not user:
        messagebox.showerror('Login Error', 'Invalid username')
    else:
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        passw = cursor.fetchone()

        if not passw:
            messagebox.showerror('Login Error', 'Incorrect password')
        else:
            cursor.execute('SELECT picture FROM users WHERE username = ?', (username_entry.get(),))
            picture = cursor.fetchone()[0]

            pfp_image = Image.open(f'profiles/{picture}').convert("RGBA")
            w, h = pfp_image.size
            pfp_image = resize_image(pfp_image, int(w/2))
            pfp_image = pfp_image.resize((30, 30))
            pfp_image = ImageTk.PhotoImage(pfp_image)
            pfp_label = tk.Label(nav_bar_frame, image=pfp_image)

            pfp_label.pack(side='right', padx=10, pady=5)
            account_button.pack(side='right', pady=5)
            
            open_frame(menu_frame)

def open_frame(frame):
    login_frame.pack_forget()
    register_frame.pack_forget()
    menu_frame.pack_forget()
    dict_frame.pack_forget()
    learn_frame.pack_forget()
    card_frame.pack_forget()
    notebook_frame.pack_forget()
    change_username_frame.pack_forget()
    change_password_frame.pack_forget()
    
    nav_bar_frame.pack(fill="x", side='top')
    if frame == login_frame or frame == register_frame:
        nav_bar_frame.pack_forget()
        
    frame.pack(fill='both', expand=True)

    if frame == menu_frame:
        back_button.pack_forget()
    else:
        mode_button.pack_forget()
        back_button.pack(side='left', padx=10, pady=5)
        mode_button.pack(side='left', padx=10, pady=5)

def change_username():
    username = new_username_entry.get()
    password = change_username_password_entry.get()

    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        messagebox.showerror('Input Error', 'Username already exists.')
        return
    
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username_entry.get(), password))
    if cursor.fetchall():
        cursor.execute('UPDATE users SET username = ? WHERE username = ?', (username, username_entry.get()))
        connection.commit()

        messagebox.showinfo('Success', 'Username successfully changed.')

        open_frame(menu_frame)
        return
    
    messagebox.showerror('Login Error', 'Incorrect password')


def change_password():
    password = change_password_entry.get()
    new_password = new_password_entry.get()
    repeat_new_password = repeat_new_password_entry.get()

    if new_password != repeat_new_password:
        messagebox.showerror('Input error', "'New Password' and 'Repeat New Password' don't match.")
        return

    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username_entry.get(), password))
    if cursor.fetchall():
        cursor.execute('UPDATE users SET password = ? WHERE username = ?', (new_password, username_entry.get()))
        connection.commit()

        messagebox.showinfo('Success', 'Password successfully changed.')

        open_frame(menu_frame)
        return
    
    messagebox.showerror('Login Error', 'Incorrect password')

def change_pfp():
    global pfp_label, pfp_image
    path = filedialog.askopenfilename(
        title='Select files',
        filetypes=[("Image files", "*.jpg. *.jpeg *.png")]
    )

    cursor.execute('SELECT picture FROM users WHERE username = ?', (username_entry.get(),))
    picture = cursor.fetchone()[0]

    if picture == 'default.jpg':
        picture = f'{random.randint(10000000000, 99999999999)}.png'

    dest = shutil.copyfile(path, f'profiles/{picture}')

    cursor.execute('UPDATE users SET picture = ? WHERE username = ?', (picture, username_entry.get()))
    connection.commit()

    pfp_image = Image.open(f'profiles/{picture}').convert("RGBA")
    w, h = pfp_image.size
    pfp_image = resize_image(pfp_image, int(w/2))
    pfp_image = pfp_image.resize((30, 30))
    pfp_image = ImageTk.PhotoImage(pfp_image)
    account_button.pack_forget()
    pfp_label.pack_forget()
    pfp_label = tk.Label(nav_bar_frame, image=pfp_image)

    pfp_label.pack(side='right', padx=10, pady=5)
    account_button.pack(side='right', pady=5)

def selection_changed(event):
    selection = account_button.get()
    account_button.set('My Account')
    if selection == 'Change Username':
        open_frame(change_username_frame)
    if selection == 'Change Password':
        open_frame(change_password_frame)
    if selection == 'Profile Picture':
        change_pfp()

def open_notebook():
    for i in notebook_content_frame.winfo_children():
        i.destroy()

    username = username_entry.get().strip()
    cursor.execute('SELECT word, word_info FROM notebook WHERE username = ? ORDER BY word', (username,))
    
    words = cursor.fetchall()

    colors = ["#FFEB3B", "#8BC34A", "#03A9F4", "#FF5722", "#9C27B0", "#E91E63"]
    if words:
        row = 0
        column = 0

        for word, wordinfo in words:
            color_i = random.randint(0, 5)
            color = colors[color_i]
            card_frame = tk.Frame(notebook_content_frame, bg=color)
            card_frame.grid(row=row, column=column, padx=10, pady=10)

            word_label = tk.Label(card_frame, text=word, bg=color)
            word_label.pack(padx=10, pady=5)

            wordinfo_label = tk.Label(card_frame, text=wordinfo, bg=color)
            wordinfo_label.pack(padx=10, pady=5)

            column += 1
            if column > 2:
                column = 0
                row += 1
    else:
        nowords_label = tk.Label(notebook_content_frame, text="No words saved in your notebook.")
        nowords_label.pack(pady=20)
        
    open_frame(notebook_frame)

def toggle_mode():
    """Switch between light and dark modes."""
    global dark_mode
    
    dark_mode = not dark_mode
    if dark_mode:
        root.configure(bg='#2b2b2b')
        menu_frame.configure(bg='#2b2b2b')
        menu_button_frame.configure(bg='#2b2b2b')
        button_frame.configure(bg='#2b2b2b')
        entry_frame.configure(bg='#2b2b2b')
        dict_frame.configure(bg='#2b2b2b')
        nav_bar_frame.configure(bg='#FF5722')
        card_frame.configure(bg='#2b2b2b')
        card_button_frame.configure(bg='#2b2b2b')
        learn_frame.configure(bg='#2b2b2b')
        notebook_frame.configure(bg='#2b2b2b')
        change_username_frame.configure(bg='#2b2b2b')
        change_password_frame.configure(bg='#2b2b2b')
        
        # Update widgets to dark mode
        menu_label.config(bg='#2b2b2b', fg='white')
        title_label.config(bg='#2b2b2b', fg='white')
        input_label.config(bg='#2b2b2b', fg='white')
        card_label.config(bg='#2b2b2b', fg='white')
        more_feature_label.config(bg='#2b2b2b', fg='white')
        learn_speak_word_button.config(bg='#2b2b2b', fg='white')
        learn_next_word_button.config(bg='#2b2b2b', fg='white')
        learn_label.config(bg='#2b2b2b', fg='white')
        word_entry.config(bg='#555555', fg='white')
        text_area.config(bg='#555555', fg='white')
        flashcard_label.config(bg='#555555', fg='white')
        notebook_label.config(bg='#555555', fg='white')
        back_button.config(bg='#FF5722', fg='black')
        change_username_label.config(bg='#2b2b2b', fg='white')
        new_username_label.config(bg='#2b2b2b', fg='white')
        new_username_entry.config(bg='#2b2b2b', fg='white')
        change_username_password_label.config(bg='#2b2b2b', fg='white')
        change_username_password_entry.config(bg='#2b2b2b', fg='white')
        change_password_frame_label.config(bg='#2b2b2b', fg='white')
        new_password_label.config(bg='#2b2b2b', fg='white')
        new_password_entry.config(bg='#2b2b2b', fg='white')
        repeat_new_password_label.config(bg='#2b2b2b', fg='white')
        repeat_new_password_entry.config(bg='#2b2b2b', fg='white')
        change_password_label.config(bg='#2b2b2b', fg='white')
        change_password_entry.config(bg='#2b2b2b', fg='white')
    
        # Update button text
        mode_button.config(text="Light Mode", bg='#FF5722', fg='black')
    else:
        root.configure(bg='#f0f0f0')
        menu_frame.configure(bg='#f0f0f0')
        menu_button_frame.configure(bg='#f0f0f0')
        button_frame.configure(bg='#f0f0f0')
        entry_frame.configure(bg='#f0f0f0')
        dict_frame.configure(bg='#f0f0f0')
        nav_bar_frame.configure(bg='#FFA500')
        card_frame.configure(bg='#f0f0f0')
        card_button_frame.configure(bg='#f0f0f0')
        learn_frame.configure(bg='#f0f0f0')
        notebook_frame.configure(bg='#f0f0f0')
        change_username_frame.configure(bg='#f0f0f0')
        change_password_frame.configure(bg='#f0f0f0')

        # Update widgets to light mode
        menu_label.config(bg='#f0f0f0', fg='black')
        title_label.config(bg='#f0f0f0', fg='black')
        input_label.config(bg='#f0f0f0', fg='black')
        card_label.config(bg='#f0f0f0', fg='black')
        more_feature_label.config(bg='#f0f0f0', fg='black')
        learn_speak_word_button.config(bg='#f0f0f0', fg='black')
        learn_next_word_button.config(bg='#f0f0f0', fg='black')
        learn_label.config(bg='#f0f0f0', fg='black')
        word_entry.config(bg='white', fg='black')
        text_area.config(bg='white', fg='black')
        flashcard_label.config(bg='white', fg='black')
        notebook_label.config(bg='white', fg='black')
        back_button.config(bg='#FFA500', fg='black')
        change_username_label.config(bg='#f0f0f0', fg='black')
        new_username_label.config(bg='#f0f0f0', fg='black')
        new_username_entry.config(bg='#f0f0f0', fg='black')
        change_username_password_label.config(bg='#f0f0f0', fg='black')
        change_username_password_entry.config(bg='#f0f0f0', fg='black')
        change_password_frame_label.config(bg='#f0f0f0', fg='black')
        new_password_label.config(bg='#f0f0f0', fg='black')
        new_password_entry.config(bg='#f0f0f0', fg='black')
        repeat_new_password_label.config(bg='#f0f0f0', fg='black')
        repeat_new_password_entry.config(bg='#f0f0f0', fg='black')
        change_password_label.config(bg='#f0f0f0', fg='black')
        change_password_entry.config(bg='#f0f0f0', fg='black')

        # Update button text
        mode_button.config(text="Dark Mode", bg='#FFA500', fg='black')

def record():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            txt = recognizer.recognize_google(audio)
            word_entry.insert(0, txt)
        except sr.UnknownValueError:
            return None

def get_info():
    global current_word_info
    word = word_entry.get().strip()
    if not word:
        messagebox.showerror('Input Error', 'Please Enter a Word.')
        return
    
    synsets = wn.synsets(word)
    text_area.delete(1.0, tk.END)

    if not synsets:
        text_area.insert(tk.END, 'No synsets found for this word!')
        return
    
    word_info = ''
    for i, synset in enumerate(synsets):
        pos = synset.pos()
        definition = synset.definition()
        examples = synset.examples()
        info = f"{i+1}.\n"
        info += f"Part Of Speach: {pos}\n"
        info += f"Definition: {definition}\n"
        if examples:
            info += f"Examples: {examples}\n"

        info += '\n'
        word_info += info

    text_area.insert(tk.END, word_info)
    global current_word_info
    current_word_info = word_info
    
def speak_word():
    word = word_entry.get().strip()
    if not word:
        messagebox.showerror('Input Error', 'Please Enter a Word.')
        return

    engine.say(word)
    engine.runAndWait()

def speak_info():
    try:
        if not current_word_info:
            messagebox.showerror('Input Error', 'Please get the info from the word.')
            return
    except:
        messagebox.showerror('Input Error', 'Please get the info from the word.')
        return        
    
    engine.say(current_word_info)
    engine.runAndWait()

def save_to_notebook():
    word = word_entry.get().strip()
    username = username_entry.get().strip()
    if not word or not current_word_info:
        messagebox.showerror('Input Error', 'Please enter a word and get its information before saving.')
        return
    
    cursor.execute('SELECT word FROM notebook WHERE username = ? AND word = ?', (username, word))
    check_word = cursor.fetchone()
    if check_word:
        messagebox.showerror('Input Error', 'The word has already been added to your notebook.')
        return
    
    cursor.execute('INSERT INTO notebook (username, word, word_info) VALUES (?, ?, ?)', (username, word, current_word_info))

    connection.commit()

    messagebox.showinfo('Success', 'Word saved to your notebook.')


def show_flashcard_word():
    global current_word
    if current_word < len(words):
        word = words[current_word]
        synsets = wn.synsets(word)
        if synsets:
            definition = synsets[0].definition()
        else:
            definition = 'definition not available'
        
        flashcard_text.set(f'Word: {word}\n\nDefinition: {definition}')

    else:
        flashcard_text.set('End of flashcards')

def load_random_words():
    global words, current_word
    words = random.sample(list(wn.words()), 10)
    current_word = 0
    show_flashcard_word()

def learn_vocab():
    open_frame(card_frame)
    load_random_words()
    card_frame.pack(fill='both', expand=True)

def next_word():
    global current_word
    if current_word < len(words) - 1:
        current_word += 1
        show_flashcard_word()
    else:
        messagebox.showinfo('Flashcards', 'You have reached the last word')

def speak_flashcard_word():
    global current_word
    if current_word < len(words):
        word = words[current_word]

        engine.say(word)
        engine.runAndWait()
    else:
        messagebox.showinfo('Flashcards', 'No Word available to pronounce')

# navbar frame

nav_bar_frame = tk.Frame(root, bg='#FFA500', height=40)
back_button = tk.Button(nav_bar_frame, text='Back To Menu', bg='#FFA500', command=lambda: open_frame(menu_frame))
mode_button = tk.Button(nav_bar_frame, text='Dark Mode', bg='#FFA500', fg='#000000', command=toggle_mode)
account_button = ttk.Combobox(nav_bar_frame, state="readonly", values=['Change Username', 'Change Password', 'Profile Picture'])

account_button.set('My Account')
account_button.bind("<<ComboboxSelected>>", selection_changed)

back_button.pack(side='left', padx=10, pady=5)
mode_button.pack(side='left', padx=10, pady=5)

# register frame
register_frame = tk.Frame(root)

register_label = tk.Label(register_frame, text='Register', font=("Arial", 24, "bold"))
register_username_label = tk.Label(register_frame, text='Username:', font=("Arial", 12))
register_username_entry = tk.Entry(register_frame, font=("Arial", 10), width=25)
register_password_label = tk.Label(register_frame, text='Password:', font=("Arial", 12))
register_password_entry = tk.Entry(register_frame, show="*", font=("Arial", 10), width=25)
email_label = tk.Label(register_frame, text='Email:', font=("Arial", 12))
email_entry = tk.Entry(register_frame, font=("Arial", 10), width=25)
register_button = tk.Button(register_frame, text='Register', bg='#8BC34A', fg='#FFFFFF', font=('Arial', 12, 'bold'), width=10, command=register_user)
have_account_label = tk.Label(register_frame, text="Already have an account? Login here.", font=("Arial", 10))
have_account_login_button = tk.Button(register_frame, text='Login', bg='#F4C34A', fg='#FFFFFF', font=('Arial', 12, 'bold'), width=10, command=lambda: open_frame(login_frame))

register_label.pack()
register_username_label.pack(pady=(15, 5))
register_username_entry.pack()
register_password_label.pack(pady=(10, 5))
register_password_entry.pack()
email_label.pack(pady=(10, 5))
email_entry.pack()
register_button.pack(pady=(25, 20))
have_account_label.pack(pady=2)
have_account_login_button.pack()

# login frame
login_frame = tk.Frame(root)

login_label = tk.Label(login_frame, text='Login', font=("Arial", 24, "bold"))
username_label = tk.Label(login_frame, text='Username:', font=("Arial", 12))
username_entry = tk.Entry(login_frame, font=('Arial', 10), width=25)
password_label = tk.Label(login_frame, text='Password:', font=('Arial', 12))
password_entry = tk.Entry(login_frame, show="*", font=('Arial', 10), width=25)
login_button = tk.Button(login_frame, text='Login', bg='#8BC34A', fg='#FFFFFF', font=('Arial', 12, 'bold'), width=10, command=login_user)
no_account_label = tk.Label(login_frame, text="Don't have an account? Register here.", font=("Arial", 10))
no_account_register_button = tk.Button(login_frame, text='Register', bg='#F4C34A', fg='#FFFFFF', font=('Arial', 12, 'bold'), width=10, command=lambda: open_frame(register_frame))

login_frame.pack(fill='both', expand=True)
login_label.pack()
username_label.pack(pady=(15, 5))
username_entry.pack()
password_label.pack(pady=(10, 5))
password_entry.pack()
login_button.pack(pady=(25, 20))
no_account_label.pack(pady=2)
no_account_register_button.pack()

# menu frame
menu_frame = tk.Frame(root)

#bg_image = PhotoImage(file="bg.png")
#bg_label = tk.Label(menu_frame, image=bg_image)

menu_label = tk.Label(menu_frame, text='Welcome To English Learning Application!', font=("Helvetica", 20, "bold"))
menu_button_frame = tk.Frame(menu_frame)
dict_button = tk.Button(menu_button_frame, text='Dictionary', bg='#FFA500', fg='#FFFFFF', font=('Helvetica', 16, 'bold'), width=15, command=lambda: open_frame(dict_frame))
learn_button = tk.Button(menu_button_frame, text='Learn English', bg='#03A9F4', fg='#FFFFFF', font=('Helvetica', 16, 'bold'), width=15, command=lambda: open_frame(learn_frame))
notebook_button = tk.Button(menu_button_frame, text='Notebook', bg='#9C27B0', fg='#FFFFFF', font=('Helvetica', 16, 'bold'), width=15, command=open_notebook)

#bg_label.place(relwidth=1, relheight=1)
menu_label.pack(pady=25)
menu_button_frame.pack(pady=50)
dict_button.pack(pady=10)
learn_button.pack(pady=10)
notebook_button.pack(pady=10)

# change username frame
change_username_frame = tk.Frame(root)

change_username_label = tk.Label(change_username_frame, text='Change Username', font=("Arial", 24, "bold"))
new_username_label = tk.Label(change_username_frame, text='New Username:', font=("Arial", 12))
new_username_entry = tk.Entry(change_username_frame, font=('Arial', 10), width=25)
change_username_password_label = tk.Label(change_username_frame, text='Password:', font=('Arial', 12))
change_username_password_entry = tk.Entry(change_username_frame, show="*", font=('Arial', 10), width=25)
change_username_button = tk.Button(change_username_frame, text='Change', bg='#8BC34A', fg='#FFFFFF', font=('Arial', 12, 'bold'), width=10, command=change_username)

change_username_label.pack()
new_username_label.pack(pady=(15, 5))
new_username_entry.pack()
change_username_password_label.pack(pady=(10, 5))
change_username_password_entry.pack()
change_username_button.pack(pady=20)

# change password frame
change_password_frame = tk.Frame(root)

change_password_frame_label = tk.Label(change_password_frame, text='Change Password', font=("Arial", 24, "bold"))
change_password_label = tk.Label(change_password_frame, text='Password:', font=('Arial', 12))
change_password_entry = tk.Entry(change_password_frame, show="*", font=('Arial', 10), width=25)
new_password_label = tk.Label(change_password_frame, text='New password:', font=("Arial", 12))
new_password_entry = tk.Entry(change_password_frame, show="*", font=('Arial', 10), width=25)
repeat_new_password_label = tk.Label(change_password_frame, text='Repeat New password:', font=("Arial", 12))
repeat_new_password_entry = tk.Entry(change_password_frame, show="*", font=('Arial', 10), width=25)
change_password_button = tk.Button(change_password_frame, text='Change', bg='#8BC34A', fg='#FFFFFF', font=('Arial', 12, 'bold'), width=10, command=change_password)

change_password_frame_label.pack()
change_password_label.pack(pady=(15, 5))
change_password_entry.pack()
new_password_label.pack(pady=(10, 5))
new_password_entry.pack()
repeat_new_password_label.pack(pady=(10, 5))
repeat_new_password_entry.pack()
change_password_button.pack(pady=20)

# dictionary frame
dict_frame = tk.Frame(root)

title_label = tk.Label(dict_frame, text='Word Meaning And Pronunciation', font=('Helvetica', 16, 'bold'), bg='#F0F0F0')

entry_frame = tk.Frame(dict_frame)
input_label = tk.Label(entry_frame, text='Enter a word:', font=('Arial', 10))
mic_image= tk.PhotoImage(file="mic.png")
mic_image = mic_image.subsample(8, 8)
speak_button = tk.Button(entry_frame, image=mic_image, command=record)
word_entry = tk.Entry(entry_frame, width=30, font=('Arial', 14))

button_frame = tk.Frame(dict_frame)
info_button = tk.Button(button_frame, text="Get Word Info", font=("Arial", 12), bg="#FF5722", fg="white", width=15, command=get_info)
speak_word_button = tk.Button(button_frame, text="Pronunciation Word", font=("Arial", 12), bg="#8BC34A", fg="white", width=15, command=speak_word)
speak_info_button = tk.Button(button_frame, text="Pronunciation Info", font=("Arial", 12), bg="#03A9F4", fg="white", width=15, command=speak_info)
save_notebook_button = tk.Button(button_frame, text="Save To Notebook", font=("Arial", 12), bg="#9C27B0", fg="white", width=15, command=save_to_notebook)
text_area = scrolledtext.ScrolledText(dict_frame, wrap=tk.WORD, width=80, height=15, font=('Arial', 11))

title_label.pack(pady=5)
entry_frame.pack(pady=10)
input_label.grid(row=0, column=0)
speak_button.grid(row=1, column=1, padx=5)
word_entry.grid(row=1, column=0)
info_button.grid(row=0, column=0, padx=10, pady=10)
speak_word_button.grid(row=0, column=1, padx=10, pady=10)
speak_info_button.grid(row=0, column=2, padx=10, pady=10)
save_notebook_button.grid(row=0, column=3, padx=10, pady=10)
button_frame.pack(pady=10)
text_area.pack(padx=10, pady=10)

# learn frame
learn_frame = tk.Frame(root)

learn_label = tk.Label(learn_frame, text='Learning English', font=('Helvetica', 16, 'bold'), bg='#F0F0F0')
learn_button = tk.Button(learn_frame, text='Learn Vocabulary', bg='#4CAF50', fg='#FFFFFF', font=('Helvetica', 12, 'bold'), width=20, command=learn_vocab)
more_feature_label = tk.Label(learn_frame, text='More features coming soon...')

learn_label.pack(pady=10)
learn_button.pack(pady=10)
more_feature_label.pack()

# flashcard frame
card_frame = tk.Frame(root)

card_label = tk.Label(card_frame, text='Flashcards: Learn Vocabulary', font=('Helvetica', 16, 'bold'), bg='#F0F0F0')
flashcard_text = tk.StringVar(card_frame)
flashcard_label = tk.Label(card_frame, textvariable=flashcard_text, bg='#F0F0F0', wraplength=500, justify='left')
card_button_frame = tk.Frame(card_frame)
learn_speak_word_button = tk.Button(card_button_frame, text='Pronounce Word', command=speak_flashcard_word)
learn_next_word_button = tk.Button(card_button_frame, text='Next Word', command=next_word)

card_label.pack()
flashcard_label.pack(pady=10)
card_button_frame.pack(pady=10)
learn_speak_word_button.grid(row=0, column=0, padx=10, pady=10)
learn_next_word_button.grid(row=0, column=1, padx=10, pady=10)

# notebook frame
notebook_frame = tk.Frame(root, bg="#F0F0F0")

notebook_label = tk.Label(notebook_frame, text="My Notebook")
canvas = tk.Canvas(notebook_frame, bg="#F0F0F0")
notebook_scrollbar = tk.Scrollbar(notebook_frame, command=canvas.yview, orient=VERTICAL)
canvas.configure(yscrollcommand=notebook_scrollbar.set)

notebook_content_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=notebook_content_frame)

def update_scrollregion(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

notebook_content_frame.bind(notebook_content_frame.bind("<Configure>", update_scrollregion))

notebook_label.pack(pady=20)
notebook_scrollbar.pack(side="right", fill="y")
canvas.pack(fill="both", expand=True, pady=10, padx=10)

root.mainloop()
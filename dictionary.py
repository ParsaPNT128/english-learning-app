import nltk
from nltk.corpus import wordnet as wn
from tkinter import *
from tkinter import messagebox, PhotoImage, scrolledtext
import tkinter as tk
import random
import speech_recognition as sr
import pyttsx3
import sqlite3
import re
#nltk.download('wordnet')

# main window
engine = pyttsx3.init()
root = tk.Tk()
root.title('English Application')
root.geometry('600x400')
root.resizable(False, False)

connection = sqlite3.connect("user_data.db")
cursor = connection.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users
               (username TEXT PRIMARY KEY, password TEXT NOT NULL, email TEXT NOT NULL)''')

connection.commit()

def open_frame(frame):
    login_frame.pack_forget()
    register_frame.pack_forget()
    menu_frame.pack_forget()
    dict_frame.pack_forget()
    learn_frame.pack_forget()
    card_frame.pack_forget()

    frame.pack(fill='both', expand=True)

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

# register frame
register_frame = tk.Frame(root)

register_label = tk.Label(register_frame, text='Register')
register_username_label = tk.Label(register_frame, text='Username:')
register_username_entry = tk.Entry(register_frame)
register_password_label = tk.Label(register_frame, text='Password:')
register_password_entry = tk.Entry(register_frame, show="*")
repeat_password_label = tk.Label(register_frame, text='Repeat Password:')
repeat_password_entry = tk.Entry(register_frame, show="*")
register_button = tk.Button(register_frame, text='Register', bg='green', fg='white')
have_account_label = tk.Label(register_frame, text="Already have an account? Login here.")
have_account_login_button = tk.Button(register_frame, text='Login', bg='gold', fg='white', command=lambda: open_frame(login_frame))

register_label.pack()
register_username_label.pack()
register_username_entry.pack()
register_password_label.pack()
register_password_entry.pack()
repeat_password_label.pack()
repeat_password_entry.pack()
register_button.pack()
have_account_label.pack()
have_account_login_button.pack()

# login frame
login_frame = tk.Frame(root)

login_label = tk.Label(login_frame, text='Login')
username_label = tk.Label(login_frame, text='Username:')
username_entry = tk.Entry(login_frame)
password_label = tk.Label(login_frame, text='Password:')
password_entry = tk.Entry(login_frame, show="*")
login_button = tk.Button(login_frame, text='Login', bg='green', fg='white')
no_account_label = tk.Label(login_frame, text="Don't have an account? Register here.")
no_account_register_button = tk.Button(login_frame, text='Register', bg='gold', fg='white', command=lambda: open_frame(register_frame))

login_frame.pack(fill='both', expand=True)
login_label.pack()
username_label.pack()
username_entry.pack()
password_label.pack()
password_entry.pack()
login_button.pack()
no_account_label.pack()
no_account_register_button.pack()

# menu frame
menu_frame = tk.Frame(root)

bg_image = PhotoImage(file="bg.png")
bg_label = tk.Label(menu_frame, image=bg_image)

menu_label = tk.Label(menu_frame, text='Welcome To English Learning Application!', font=("Helvetica", 20, "bold"))
menu_button_frame = tk.Frame(menu_frame)
dict_button = tk.Button(menu_button_frame, text='Dictionary', bg='#FFA500', fg='#FFFFFF', font=('Helvetica', 16, 'bold'), width=15, command=lambda: open_frame(dict_frame))
learn_button = tk.Button(menu_button_frame, text='Learn English', bg='#00FFFF', fg='#FFFFFF', font=('Helvetica', 16, 'bold'), width=15, command=lambda: open_frame(learn_frame))

bg_label.place(relwidth=1, relheight=1)
menu_label.pack(pady=25)
menu_button_frame.pack(pady=50)
dict_button.pack(pady=10)
learn_button.pack(pady=10)

# dictionary frame
dict_frame = tk.Frame(root)

nav_bar_frame = tk.Frame(dict_frame, bg='#FFA500', height=40)
back_button = tk.Button(nav_bar_frame, text='Back To Menu', bg='#FFA500', command=lambda: open_frame(menu_frame))

title_label = tk.Label(dict_frame, text='Word Meaning And Pronunciation', font=('Helvetica', 16, 'bold'), bg='#F0F0F0')
input_label = tk.Label(dict_frame, text='Enter a word:')
entry_frame = tk.Frame(dict_frame)

mic_image= tk.PhotoImage(file="mic.png")
mic_image = mic_image.subsample(8, 8)
speak_button = tk.Button(entry_frame, image=mic_image, command=record)
word_entry = tk.Entry(entry_frame, width=30)

button_frame = tk.Frame(dict_frame)
info_button = tk.Button(button_frame, text="Get Word Info", font=("Arial", 12), bg="#4CAF50", fg="white", width=15, command=get_info)
speak_word_button = tk.Button(button_frame, text="Pronunciation Word", font=("Arial", 12), bg="#4CAF50", fg="white", width=15, command=speak_word)
speak_info_button = tk.Button(button_frame, text="Pronunciation Info", font=("Arial", 12), bg="#4CAF50", fg="white", width=15, command=speak_info)
text_area = scrolledtext.ScrolledText(dict_frame, wrap=tk.WORD, width=60, height=10)

nav_bar_frame.pack(fill="x", side='top')
back_button.pack(side='left', padx=10, pady=5)
title_label.pack(pady=10)
input_label.pack(pady=10)
entry_frame.pack(pady=10)
speak_button.grid(row=0, column=0, padx=5)
word_entry.grid(row=0, column=1)
info_button.grid(row=0, column=0, padx=10, pady=10)
speak_word_button.grid(row=0, column=1, padx=10, pady=10)
speak_info_button.grid(row=0, column=2, padx=10, pady=10)
button_frame.pack(pady=10)
text_area.pack(padx=10, pady=10)

# learn frame
learn_frame = tk.Frame(root)

nav_bar_frame = tk.Frame(learn_frame, bg='#FFA500', height=40)
back_button = tk.Button(nav_bar_frame, text='Back To Menu', bg='#FFA500', command=lambda: open_frame(menu_frame))

learn_label = tk.Label(learn_frame, text='Learning English', font=('Helvetica', 16, 'bold'), bg='#F0F0F0')
learn_button = tk.Button(learn_frame, text='Learn Vocabulary', bg='#4CAF50', fg='#FFFFFF', font=('Helvetica', 12, 'bold'), width=20, command=learn_vocab)
more_feature_label = tk.Label(learn_frame, text='More features coming soon...')

nav_bar_frame.pack(fill="x", side='top')
back_button.pack(side='left', padx=10, pady=5)
learn_label.pack(pady=10)
learn_button.pack(pady=10)
more_feature_label.pack()

# flashcard frame
card_frame = tk.Frame(root)

nav_bar_frame = tk.Frame(card_frame, bg='#FFA500', height=40)
back_button = tk.Button(nav_bar_frame, text='Back To Menu', bg='#FFA500', command=lambda: open_frame(menu_frame))

card_label = tk.Label(card_frame, text='Flashcards: Learn Vocabulary', font=('Helvetica', 16, 'bold'), bg='#F0F0F0')
flashcard_text = tk.StringVar(card_frame)
flashcard_label = tk.Label(card_frame, textvariable=flashcard_text, bg='#F0F0F0', wraplength=500, justify='left')
card_button_frame = tk.Frame(card_frame)
learn_speak_word_button = tk.Button(card_button_frame, text='Pronounce Word', command=speak_flashcard_word)
learn_next_word_button = tk.Button(card_button_frame, text='Next Word', command=next_word)

nav_bar_frame.pack(fill="x", side='top')
back_button.pack(side='left', padx=10, pady=5)
card_label.pack()
flashcard_label.pack(pady=10)
card_button_frame.pack(pady=10)
learn_speak_word_button.grid(row=0, column=0, padx=10, pady=10)
learn_next_word_button.grid(row=0, column=1, padx=10, pady=10)


root.mainloop()
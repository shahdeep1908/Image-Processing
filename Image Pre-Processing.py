#MAKE FOLDER NAMED AZURE ON DESKTOP
from tkinter import *
import tkinter as tk
import importlib
from tkinter import filedialog
from skimage.metrics import structural_similarity
import argparse
import os.path
import imutils
import glob
import tkcalendar
import datetime
import cv2
import os
import geocoder
import time
import re
from wand.image import Image
import pymysql

#IT FILTERS WARNINGS 
import warnings
warnings.filterwarnings("ignore")

#CONNECTING TO MySQL SERVER DATABASE
global connection
global cursor
global user_credentials
connection = pymysql.connect(host="localhost",user="root",passwd="",database="azure" )
cursor = connection.cursor()

user_credentials = """CREATE TABLE IF NOT EXISTS user_credentials(
user_id INT(20) PRIMARY KEY AUTO_INCREMENT, name CHAR(20) NOT NULL,
username CHAR(20) NOT NULL, password CHAR(20) NOT NULL, contact_no CHAR(20),
email CHAR(20), city CHAR(20)) """
cursor.execute(user_credentials)

geographic_details = """CREATE TABLE IF NOT EXISTS geographic_details(
id INT(20) PRIMARY KEY AUTO_INCREMENT, user_id INT(20) , username CHAR(20) NOT NULL,  video_name CHAR(20) NOT NULL, area CHAR(20),
city CHAR(20), state CHAR(20), country CHAR(20), date CHAR(20))"""
cursor.execute(geographic_details)

video_file_details = """CREATE TABLE IF NOT EXISTS video_file_details(
id INT(20) PRIMARY KEY AUTO_INCREMENT, user_id INT(20) , username CHAR(20) NOT NULL, actual_file_name CHAR(20), file_size CHAR(20), file_extension CHAR(20),
file_resolution CHAR(20), latitude CHAR(20), longitude CHAR(20), file_status INT(2) DEFAULT 0)"""
cursor.execute(video_file_details)

ssim_images = """CREATE TABLE IF NOT EXISTS ssim_images(
id INT(20) PRIMARY KEY AUTO_INCREMENT, user_id INT(20), username CHAR(20) NOT NULL,image_name CHAR(20), image_size CHAR(20),
file_extension CHAR(20), file_resolution CHAR(20), pre_score CHAR(20), next_score CHAR(20),
latitude CHAR(20), longitude CHAR(20))"""
cursor.execute(ssim_images)

#LIST OF COUNTRIES ON SELECTION
global lista, comparision, down, up, selection, changed, AutocompleteEntry
lista = ["Afghanistan", "Albania", "Algeria", "American Samoa", "Andorra", "Angola", "Anguilla", "Antarctica", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia", "Bosnia and Herzegowina", "Botswana", "Bouvet Island", "Brazil", "British Indian Ocean Territory", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada", "Cape Verde", "Cayman Islands", "Central African Republic", "Chad", "Chile", "China", "Christmas Island", "Cocos (Keeling) Islands", "Colombia", "Comoros", "Congo", "Congo, the Democratic Republic of the", "Cook Islands", "Costa Rica", "Cote d'Ivoire", "Croatia (Hrvatska)", "Cuba", "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "East Timor", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia", "Falkland Islands (Malvinas)", "Faroe Islands", "Fiji", "Finland", "France", "France Metropolitan", "French Guiana", "French Polynesia", "French Southern Territories", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Gibraltar", "Greece", "Greenland", "Grenada", "Guadeloupe", "Guam", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Heard and Mc Donald Islands", "Holy See (Vatican City State)", "Honduras", "Hong Kong", "Hungary", "Iceland", "India", "Indonesia", "Iran (Islamic Republic of)", "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea, Democratic People's Republic of", "Korea, Republic of", "Kuwait", "Kyrgyzstan", "Lao, People's Democratic Republic", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libyan Arab Jamahiriya", "Liechtenstein", "Lithuania", "Luxembourg", "Macau", "Macedonia, The Former Yugoslav Republic of", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Martinique", "Mauritania", "Mauritius", "Mayotte", "Mexico", "Micronesia, Federated States of", "Moldova, Republic of", "Monaco", "Mongolia", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "Netherlands Antilles", "New Caledonia", "New Zealand", "Nicaragua", "Niger", "Nigeria", "Niue", "Norfolk Island", "Northern Mariana Islands", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Pitcairn", "Poland", "Portugal", "Puerto Rico", "Qatar", "Reunion", "Romania", "Russian Federation", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Seychelles", "Sierra Leone", "Singapore", "Slovakia (Slovak Republic)", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Georgia and the South Sandwich Islands", "Spain", "Sri Lanka", "St. Helena", "St. Pierre and Miquelon", "Sudan", "Suriname", "Svalbard and Jan Mayen Islands", "Swaziland", "Sweden", "Switzerland", "Syrian Arab Republic", "Taiwan, Province of China", "Tajikistan", "Tanzania, United Republic of", "Thailand", "Togo", "Tokelau", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Turks and Caicos Islands", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "United States Minor Outlying Islands", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "Virgin Islands (British)", "Virgin Islands (U.S.)", "Wallis and Futuna Islands", "Western Sahara", "Yemen", "Yugoslavia", "Zambia", "Zimbabwe"]

class AutocompleteEntry(Entry):
    def __init__(self, lista, *args, **kwargs):
        
        Entry.__init__(self, *args, **kwargs)
        self.lista = lista        
        self.var = self["textvariable"]
        if self.var == '':
            self.var = self["textvariable"] = StringVar()

        self.var.trace('w', self.changed)
        self.bind("<Right>", self.selection)
        self.bind("<Up>", self.up)
        self.bind("<Down>", self.down)
        
        self.lb_up = False

    def changed(self, name, index, mode):  

        if self.var.get() == '':
            self.lb.destroy()
            self.lb_up = False
        else:
            words = self.comparison()
            if words:            
                if not self.lb_up:
                    self.lb = Listbox()
                    self.lb.bind("<Button-1>", self.selection)
                    self.lb.bind("<Right>", self.selection)
                    self.lb.place(x=self.winfo_x(), y=self.winfo_y()+self.winfo_height())
                    self.lb_up = True
                
                self.lb.delete(0, END)
                for w in words:
                    self.lb.insert(END,w)
            else:
                if self.lb_up:
                    self.lb.destroy()
                    self.lb_up = False
        
    def selection(self, event):

        if self.lb_up:
            self.var.set(self.lb.get(ACTIVE))
            self.lb.destroy()
            self.lb_up = False
            self.icursor(END)

    def up(self, event):

        if self.lb_up:
            if self.lb.curselection() == ():
                index = '0'
            else:
                index = self.lb.curselection()[0]
            if index != '0':                
                self.lb.selection_clear(first=index)
                index = str(int(index)-1)                
                self.lb.selection_set(first=index)
                self.lb.activate(index) 

    def down(self, event):

        if self.lb_up:
            if self.lb.curselection() == ():
                index = '0'
            else:
                index = self.lb.curselection()[0]
            if index != END:                        
                self.lb.selection_clear(first=index)
                index = str(int(index)+1)        
                self.lb.selection_set(first=index)
                self.lb.activate(index) 

    def comparison(self):
        pattern = re.compile('.*' + self.var.get() + '.*')
        return [w for w in self.lista if re.match(pattern, w)]

global ins_username,Username
ins_username = ""
Username = ""

def new_user_page():
    try:
        global Username
        Name=entry_1.get()
        Username=entry_2.get()
        Password=entry_3.get()
        Contact=entry_4.get()
        Email=entry_5.get()
        City=entry_6.get()

        sel_username = """SELECT username FROM user_credentials"""
        cursor.execute(sel_username)
        row = cursor.fetchall()
        connection.commit()
        for i in row:
            i = (str(''.join(i)))
            if(i == Name):
                label_0 = tk.Label(root_2, text='Username Already Exists ')
                label_0.config(font=('helvetica', 10))
                canvas_2.create_window(200, 10, window=label_0)
                already_exists()
                break

        ins_new_user = """INSERT INTO user_credentials(name, username, password,
        contact_no, email, city) VALUES(%s, %s, %s, %s, %s, %s)"""
        insert = (Name,Username,Password,Contact,Email,City)
        cursor.execute(ins_new_user, insert)
        connection.commit()
        root_2.destroy()    
        geographic()
        
    except Exception as e:
        print(e)
    
def ex_user_page():
    try:
        global ins_username
        ins_username = entry_22.get()
        ins_password = entry_33.get()
        username = """SELECT username FROM user_credentials"""
        password = """SELECT password FROM user_credentials"""
        cursor.execute(username)
        row1 = cursor.fetchall()
        cursor.execute(password)
        row2 = cursor.fetchall()
        connection.commit()
        for i in row1:
            i = (str(''.join(i)))
            for j in row2:
                j = (str(''.join(j)))
                if(i == ins_username and j == ins_password):
                    root_3.destroy()
                    geographic()
                    break
        
        label_00 = tk.Label(root_3, text='Incorrect Username or Password ')
        label_00.config(font=('helvetica', 10))
        canvas_3.create_window(200, 10, window=label_00)
        incorrect_keyword()
        
    except Exception as e:
        print(e)

def existing_user():
    root_1.destroy()
    global incorrect_keyword
    global root_3, canvas_3
    global label_00,entry_22
    
    root_3 = tk.Tk()
    canvas_3 = tk.Canvas(root_3, width=400, height=200)
    canvas_3.pack()
    def incorrect_keyword():
        global entry_22,entry_33
        label_11 = tk.Label(root_3, text='SignIn Form ')
        label_11.config(font=('helvetica', 14))
        canvas_3.create_window(200, 30, window=label_11)

        label_22 = tk.Label(root_3, text='UserName :')
        canvas_3.create_window(32, 60, window=label_22)
        entry_22 = tk.Entry(root_3)
        canvas_3.create_window(180, 60, window=entry_22)

        label_33 = tk.Label(root_3, text='Password :')
        canvas_3.create_window(31, 90, window=label_33)
        entry_33 = tk.Entry(root_3, show="*")
        canvas_3.create_window(180, 90, window=entry_33)
            
        btn_ex = Button(root_3, text="     Submit     ", command=ex_user_page)
        canvas_3.create_window(170, 125, window=btn_ex)

        root_3.mainloop()
    incorrect_keyword()

def new_user():    
    global root_2,canvas_2
    global already_exists
    root_1.destroy()
    global Name,Username,password,Contact,Email,City,label_0,entry_2
    root_2 = tk.Tk()
    canvas_2 = tk.Canvas(root_2, width=400, height=300)
    canvas_2.pack()
    
    def already_exists():
        global entry_1,entry_2,entry_3,entry_4,entry_5,entry_6
        label_l = tk.Label(root_2, text='SignUp Form ')
        label_l.config(font=('helvetica', 14))
        canvas_2.create_window(200, 30, window=label_l)

        label_2 = tk.Label(root_2, text='Name :')
        canvas_2.create_window(24, 60, window=label_2)
        entry_1 = tk.Entry(root_2)
        canvas_2.create_window(180, 60, window=entry_1)

        label_2 = tk.Label(root_2, text='UserName :')
        canvas_2.create_window(33, 90, window=label_2)
        entry_2 = tk.Entry(root_2)
        canvas_2.create_window(180, 90, window=entry_2)

        label_3 = tk.Label(root_2, text='Password :')
        canvas_2.create_window(31, 120, window=label_3)
        entry_3 = tk.Entry(root_2, show="*")
        canvas_2.create_window(180, 120, window=entry_3)

        label_4 = tk.Label(root_2, text='Contact No. :')
        canvas_2.create_window(37, 150, window=label_4)
        entry_4 = tk.Entry(root_2)
        canvas_2.create_window(180, 150, window=entry_4)

        label_5 = tk.Label(root_2, text='Email-ID :')
        canvas_2.create_window(28, 180, window=label_5)
        entry_5 = tk.Entry(root_2)
        canvas_2.create_window(180, 180, window=entry_5)

        label_6 = tk.Label(root_2, text='City :')
        canvas_2.create_window(16, 210, window=label_6)
        entry_6 = tk.Entry(root_2)
        canvas_2.create_window(180, 210, window=entry_6)

        btn_new = Button(root_2, text="     Submit     ", command=new_user_page)
        canvas_2.create_window(170, 270, window=btn_new)
        root_2.mainloop()
    already_exists()

global root_1
root_1 = tk.Tk()
canvas_1 = tk.Canvas(root_1, width=300, height=100)
canvas_1.pack()

btn_1 = Button(root_1, text="     New User     ", command=new_user)
canvas_1.create_window(80, 50, window=btn_1)

btn_2 = Button(root_1, text="     Existing User     ", command=existing_user)
canvas_1.create_window(200, 50, window=btn_2)

#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#
def dt_ins():
    e.delete(0, tk.END)
    e.insert(0, str(datetime.datetime.now().date()))

def Page2():
    try:
        video = entry1.get()
        area = entry2.get()
        city = entry3.get()
        state = entry4.get()
        country = entry5.get()
        date = e.get()
        date = str(date)
        sel_id1 = """SELECT user_id FROM user_credentials WHERE username = %s"""
        sel_id2 = """SELECT user_id FROM user_credentials WHERE username = %s"""
        set_id1 = (Username)
        set_id2 = (ins_username)
        cursor.execute(sel_id1, set_id1)
        row1 = cursor.fetchall()
        cursor.execute(sel_id2, set_id2)
        row2 = cursor.fetchall()
        connection.commit()

        if not row1:
            uid = row2[0][0]
            ins = """INSERT INTO geographic_details (user_id, username, video_name, area, city, state, country, date) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"""
            ins_value = (uid,ins_username,video,area,city,state,country,date)
            cursor.execute(ins, ins_value)
            connection.commit()
            root.destroy()
            dumping()
        if not row2:
            uid = row1[0][0]
            ins = """INSERT INTO geographic_details (user_id, username, video_name, area, city, state, country, date) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"""
            ins_value = (uid,Username,video,area,city,state,country,date)
            cursor.execute(ins, ins_value)
            connection.commit()
            root.destroy()
            dumping()
    
    except Exception as ex:
        print("\n")

def geographic():
    global e
    global root
    global entry1,entry2,entry3,entry4,entry5,e
    root = tk.Tk()
    canvas1 = tk.Canvas(root, width=400, height=300)
    canvas1.pack()

    label = tk.Label(root, text='Geographic Details')
    label.config(font=('helvetica', 14))
    canvas1.create_window(200, 25, window=label)

    label1 = tk.Label(root, text='Name of Video :')
    canvas1.create_window(45, 60, window=label1)
    entry1 = tk.Entry(root)
    canvas1.create_window(180, 60, window=entry1)

    label2 = tk.Label(root, text='Area :')
    canvas1.create_window(18, 90, window=label2)
    entry2 = tk.Entry(root)
    canvas1.create_window(180, 90, window=entry2)

    label3 = tk.Label(root, text='City :')
    canvas1.create_window(16, 120, window=label3)
    entry3 = tk.Entry(root)
    canvas1.create_window(180, 120, window=entry3)

    label4 = tk.Label(root, text='State :')
    canvas1.create_window(20, 150, window=label4)
    entry4 = tk.Entry(root)
    canvas1.create_window(180, 150, window=entry4)

    label5 = tk.Label(root, text='Country :')
    canvas1.create_window(27, 180, window=label5)
    entry5 = AutocompleteEntry(lista, root)
    canvas1.create_window(180, 180, window=entry5)

    label6 = tk.Label(root, text='Choose a Date :')
    canvas1.create_window(45, 210, window=label6)
    e = tk.Entry(root)
    entry6 = tk.Button(root, text="Click here!", command=dt_ins)
    e.pack()
    entry6.pack()
    canvas1.create_window(180, 210, window=e)
    canvas1.create_window(280, 210, window=entry6)

    btn = Button(root, text="     Next     ", command=Page2)
    canvas1.create_window(170, 270, window=btn)

    root.mainloop()

#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#

def open():
    global path
    path = filedialog.askopenfilename()
    cap = cv2.VideoCapture(path)
    ret,frame = cap.read()
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    file_details(height, width)

def close_and_exit():
    root4.destroy()
    print('Thank You')

def de_duplication():
    root2.destroy()
    global ssim_score
    ssim_score = []
    no_of_images = len(glob.glob1("C:/Users/Admin/Desktop/azure/","*.jpg"))

    j=1
    while(True):
        file_exists = os.path.exists('C:/Users/Admin/Desktop/azure/'+str(imagename)+str(j)+'.jpg')
        if(file_exists == True):
            i=1
            while(True):
                file_exists = os.path.exists('C:/Users/Admin/Desktop/azure/'+str(imagename)+str(i+1)+'.jpg')
                if(file_exists == True and j != i+1):
                    # 3. Load the two input images
                    imageA = cv2.imread("C:/Users/Admin/Desktop/azure/"+str(imagename)+str(j)+".jpg")
                    imageB = cv2.imread("C:/Users/Admin/Desktop/azure/"+str(imagename)+str(i+1)+".jpg")

                    # 4. Convert the images to grayscale
                    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
                    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

                    # 5. Compute the Structural Similarity Index (SSIM) between the two
                    (score, diff) = structural_similarity(grayA, grayB, full=True)
                    diff = (diff * 255).astype("uint8")
                    score = round(score, 2)
                    ssim_score.append(score)

                    # 6. You can print only the score if you want
                    ##print("SSIM of Image"+str(j)+" and Image"+str(i+1), end=" ")
                    ##print(": {}".format(score))

                    if(score >= 0.85):
                        ssim_score.append(score)
                        os.remove("C:/Users/Admin/Desktop/azure/"+str(imagename)+str(i+1)+".jpg")
                        ##print("Image"+str(i+1)+" has been removed having similarity of "+str(score)+" with Image"+str(j))
                        i += 1
                        if(i+1 == j):
                            j += 1
                    else:
                        i +=1

                else:
                    i += 1
                
                if(i >= no_of_images):
                    break

            j += 1
        
        else:
            j += 1

        if(j >= no_of_images):
            global root4
            root4 = tk.Tk()
            canvas4 = tk.Canvas(root4, width=300, height=200)
            canvas4.pack()

            label_41 = tk.Label(root4, text='Applied for De-Duplication...')
            label_41.config(font=('helvetica', 14))
            canvas4.create_window(120, 10, window=label_41)
            
            label_42 = tk.Label(root4, text='...')
            canvas4.create_window(10, 40, window=label_42)
            label_42.config(font=('helvetica', 14))
            
            label_43 = tk.Label(root4, text='wait a moment...')
            label_43.config(font=('helvetica', 14))
            canvas4.create_window(70, 70, window=label_43)

            label_44 = tk.Label(root4, text='Process Ends Successfully.')
            label_44.config(font=('helvetica', 14))
            canvas4.create_window(120, 100, window=label_44)

            btn_45 = Button(root4, text="  Close and Exit  ", command = close_and_exit)
            canvas4.create_window(130, 150, window=btn_45)

            root4.mainloop()
            break

def another_file():
    root1.destroy()
    global uid,set_id1,set_id2
    lat = lat_lon[0]
    lon = lat_lon[1]
    sel_id1 = """SELECT user_id FROM user_credentials WHERE username = %s"""
    sel_id2 = """SELECT user_id FROM user_credentials WHERE username = %s"""
    set_id1 = (Username)
    set_id2 = (ins_username)
    cursor.execute(sel_id1, set_id1)
    row1 = cursor.fetchall()
    cursor.execute(sel_id2, set_id2)
    row2 = cursor.fetchall()
    connection.commit()

    if not row1:
        uid = row2[0][0]
        ins = """INSERT INTO video_file_details (user_id, username, actual_file_name, file_size, file_extension, file_resolution, latitude, longitude) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"""
        ins_value = (uid,ins_username,x,y,b,c,lat,lon)
        cursor.execute(ins, ins_value)
        connection.commit()

    if not row2:
        uid = row1[0][0]
        ins = """INSERT INTO video_file_details (user_id, username, actual_file_name, file_size, file_extension, file_resolution, latitude, longitude) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"""
        ins_value = (uid,Username,x,y,b,c,lat,lon)
        cursor.execute(ins, ins_value)
        connection.commit()
            
    folder_path = 'C:/Users/Admin/Desktop/azure'
    image_files = os.listdir(folder_path)
    for i in image_files:
        if(i.endswith('.png') or i.endswith('.jpg') or i.endswith('.bmp')):
            os.remove(os.path.join(folder_path, i))
    
    global root2
    root2 = tk.Tk()
    canvas3 = tk.Canvas(root2, width=300, height=200)
    canvas3.pack()

    label111 = tk.Label(root2, text='Extracting Your Video...')
    label111.config(font=('helvetica', 14))
    canvas3.create_window(98, 10, window=label111)
    
    label222 = tk.Label(root2, text='...')
    canvas3.create_window(10, 40, window=label222)
    label222.config(font=('helvetica', 14))
    
    label333 = tk.Label(root2, text='wait a moment...')
    label333.config(font=('helvetica', 14))
    canvas3.create_window(70, 70, window=label333)
    
    image_path = "C:/Users/Admin/Desktop/azure/" # PATH WHERE IMAGE WILL BE STORED
    cap = cv2.VideoCapture(path)

    global imagename
    select1 = """SELECT username FROM user_credentials WHERE username = %s"""
    select2 = """SELECT username FROM user_credentials WHERE username = %s"""
    set1 = (Username)
    set2 = (ins_username)
    cursor.execute(select1, set1)
    row11 = cursor.fetchall()
    cursor.execute(select2, set2)
    row22 = cursor.fetchall()

    if not row11:
        im2 = row22[0][0]
        imagename = str(im2)
    
    if not row22:
        im1 = row11[0][0]
        imagename = str(im1)

    def getframe(sec):
        global image_size, image
        cap.set(cv2.CAP_PROP_POS_MSEC,sec*1000)
        hasFrames,image = cap.read()
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        if(hasFrames):
            Image_name = str(imagename)+str(count)+".jpg"
            cv2.imwrite(os.path.join(image_path, Image_name),image)
            image_size = image_path + Image_name
            image = " "
            size = os.stat(image_size).st_size
            a,extension = os.path.splitext(image_size)
            resolution = (str(int(height)) +" x "+ str(int(width)))
            latitude = lat_lon[0]
            longitude = lat_lon[1]
            if not row1:
                uid = row2[0][0]
                ins = """INSERT INTO ssim_images (user_id, username, image_name, image_size, file_extension, file_resolution, latitude, longitude) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"""
                ins_value = (uid,set_id2,Image_name,size,extension,resolution,lat,lon)
                cursor.execute(ins, ins_value)
                connection.commit()

            if not row2:
                uid = row1[0][0]
                ins = """INSERT INTO ssim_images (user_id, username, image_name, image_size, file_extension, file_resolution, latitude, longitude) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"""
                ins_value = (uid,set_id1,Image_name,size,extension,resolution,lat,lon)
                cursor.execute(ins, ins_value)
                connection.commit()
        return hasFrames

    sec = 0
    frameRate = 0.09 # IT WILL CAPTURE IMAGE EVERY 1 SEC
    count = 1
    success = getframe(sec)
    while(success):
        count = count + 1
        sec = sec + frameRate
        sec = round(sec,2)
        success = getframe(sec)
        
    #FILE CALL FOR IMAGE TO BLOB CONVERSION    
    os.system('python image_to_blob.py')
    
    label444 = tk.Label(root2, text='Process Ends Successfully.')
    label444.config(font=('helvetica', 14))
    canvas3.create_window(120, 100, window=label444)

    btn555 = Button(root2, text="  Apply for De-Duplication  ", command=de_duplication)
    canvas3.create_window(130, 150, window=btn555)

    root2.mainloop()

def file_details(height, width):
    global x, y, b, c, lat_lon
    label22 = tk.Label(root1, text='File Name :')
    canvas2.create_window(30, 90, window=label22)
    x = os.path.basename(path)
    label22_1 = tk.Label(root1, text=x)
    canvas2.create_window(152, 90, window=label22_1)

    label33 = tk.Label(root1, text='File Size :')
    canvas2.create_window(25, 120, window=label33)
    y = os.stat(path).st_size
    label33_1 = tk.Label(root1, text=y)
    canvas2.create_window(152, 120, window=label33_1)

    label44 = tk.Label(root1, text='File Extension :')
    canvas2.create_window(40, 150, window=label44)
    a,b = os.path.splitext(path)
    label44_1 = tk.Label(root1, text=b)
    canvas2.create_window(148, 150, window=label44_1)

    label55 = tk.Label(root1, text='File Resolution :')
    canvas2.create_window(42, 180, window=label55)
    c = (str(int(height)) +" x "+ str(int(width)))
    label55_1 = tk.Label(root1, text=c)
    canvas2.create_window(148, 180, window=label55_1)

    label66 = tk.Label(root1, text='File GeoLocation :')
    canvas2.create_window(49, 210, window=label66)
    lat_lon = geocoder.ip('me')
    lat_lon = (lat_lon.latlng)
    label66_1 = tk.Label(root1, text=lat_lon)
    canvas2.create_window(148, 210, window=label66_1)

    btn_next = Button(root1, text="  Extract Video  ", command=another_file)
    canvas2.create_window(150, 240, window=btn_next)
    
def dumping():
    global root1
    global canvas2
    root1 = tk.Tk()
    canvas2 = tk.Canvas(root1, width=400, height=300)
    canvas2.pack()

    label11 = tk.Label(root1, text='Upload your Video')
    label11.config(font=('helvetica', 14))
    canvas2.create_window(200, 25, window=label11)

    labelb = tk.Label(root1, text='Choose a File :')
    canvas2.create_window(40, 55, window=labelb)
    btn_browse = Button(root1, text="  Browse  ", command=open)
    canvas2.create_window(150, 55, window=btn_browse)

    root1.mainloop()

#------------------------------------------------------------------------------#
root_1.mainloop()
connection.close()


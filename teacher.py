from flask import Flask, render_template, request, redirect, url_for
from bs4 import BeautifulSoup
app = Flask(__name__)

# determines whether the first time is before the second time
# returns True or False
# if times are the same, returns False
def before(first, second):
    fhour = int(first.split(':')[0])
    fmin = int(first.split(':')[1].split(' ')[0])
    fm = first.split(' ')[1]
    shour = int(second.split(':')[0])
    smin = int(second.split(':')[1].split(' ')[0])
    sm = second.split(' ')[1]
    if fhour == 12:
        fm = "AM" if fm == "PM" else "AM"
    if shour == 12:
        sm = "AM" if sm == "PM" else "AM"
    if fm == "AM" and sm == "PM":
        return True
    elif fm == "PM" and sm == "AM":
        return False
    if fhour < shour:
        return True
    elif fhour > shour:
        return False
    if fmin < smin:
        return True
    elif fmin > smin:
        return False
    return False #only if the times are exact same

# main function that turns the list of strings into attendance list
# list contains a list for each student where
# [student, MM, WIN, Lit, Math, SS]
def students(input):
    record = {}
    name = ''
    number = 0
    moderator = ''
    joins = 0
    firstjoin = ''
    lastleave = ''
    for i in range(0,len(input)):
        if i < 13:
            continue
        if input[i] == 'Name':
            #create a new record for new student
            if input[i+1] not in record.keys():
                record[input[i+1]] = []
            name = input[i+1]
        if name == moderator and name != '':
            continue
        elif input[i] == "Moderator":
            moderator = name
        elif input[i] == "Joined":
            temp = []
            temp.append(input[i+1])
            record[name].append(temp)
        elif input[i] == "Left":
            record[name][number].append(input[i+1])
            number += 1
            if number >= int(joins):
                number = 0
        elif input[i] == "Joins":
            joins = input[i+1]
            if joins == '1':
                temp = [firstjoin, lastleave]
                record[name].append(temp)
        elif input[i] == "First join":
            firstjoin = input[i+1]
        elif input[i] == "Last leave":
            lastleave = input[i+1]

    result = []
    for key in record:
        if len(record[key]) == 0:
            continue
        times = record[key]
        MM = "A"
        WIN = "A"
        Lit = "A"
        Math = "A"
        SS = "A"
        for i in range(0,len(times)):
            # if start time is before end time and end time is after start time
            if before(times[i][0], "8:55 AM") and not before(times[i][1], "8:30 AM"):
                MM = "P"
            if before(times[i][0], "10:00 AM") and not before(times[i][1], "9:00 AM"):
                WIN = "P"
            if before(times[i][0], "11:05 AM") and not before(times[i][1], "10:10 AM"):
                Lit = "P"
            if before(times[i][0], "2:30 PM") and not before(times[i][1], "1:40 PM"):
                Math = "P"
            if before(times[i][0], "3:15 PM") and not before(times[i][1], "2:40 PM"):
                SS = "P"
        
        result.append([key, MM, WIN, Lit, Math, SS])
    return result

def sorting(a):
    return a[0][a[0].find(" "):]

@app.route('/')
def index():
    return render_template('attendance.html', data={})

@app.route('/', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    data = {}
    error = ""
    if uploaded_file.filename != '':
        # if its not html
        if uploaded_file.filename.split('.')[-1] != "html":
            error = "This is not an html file"
        else:
            # ------------------get the file and parse-------------------------
            html = uploaded_file.stream.read()
            soup = BeautifulSoup(html, features="html.parser")
            # kill all script and style elements
            for script in soup(["script", "style"]):
                script.extract()    # rip it out
            # get text
            text = soup.get_text()
            # break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            list = text.split('\n')

            # check for incorrect files
            if len(list) < 2 or list[0] != "Bb Collaborate":
                error = "This is the wrong file type"
            # ---------set data elements-----------
            else:
                data["report"] = list[1]
                data["date"] = list[2]
                data["starttime"] = list[3]
                data["endtime"] = list[5]
                data["students"] = students(list) 
                data["students"].sort(key=sorting)  
    return render_template('attendance.html', data=data, error=error)
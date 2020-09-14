from flask import Flask, render_template, request, redirect, url_for
from bs4 import BeautifulSoup
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('attendance.html', data={})

@app.route('/', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        # -----------------------get the file and parse---------------------------------------
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
        # print(list)
        # print(list[1]) #Ms. Wang Report
        # print(list[2]) #Date e.g. Friday, Sept 1
        # print("Start Time: s" + list[3]) #Start Time
        # print("End Time: " + list[5]) #End Time
        data = {}
        data["report"] = list[1]
        data["date"] = list[2]
        data["starttime"] = list[3]
        data["endtime"] = list[5]

        record = {}
        name = ''
        number = 0
        moderator = ''
        joins = 0
        firstjoin = ''
        lastleave = ''
        for i in range(0,len(list)):
            if i < 13:
                continue
            if list[i] == 'Name':
                #create a new record for new student
                if list[i+1] not in record.keys():
                    record[list[i+1]] = []
                name = list[i+1]
            if name == moderator and name != '':
                continue
            elif list[i] == "Moderator":
                moderator = name
            elif list[i] == "Joined":
                temp = []
                temp.append(list[i+1])
                record[name].append(temp)
            elif list[i] == "Left":
                record[name][number].append(list[i+1])
                number += 1
                if number >= int(joins):
                    number = 0
            elif list[i] == "Joins":
                joins = list[i+1]
                if joins == '1':
                    temp = [firstjoin, lastleave]
                    record[name].append(temp)
            elif list[i] == "First join":
                firstjoin = list[i+1]
            elif list[i] == "Last leave":
                lastleave = list[i+1]

        #print(record)

        def before(first, second):
            fhour = int(first.split(':')[0])
            fmin = int(first.split(':')[1].split(' ')[0])
            fm = first.split(' ')[1]
            shour = int(second.split(':')[0])
            smin = int(second.split(':')[1].split(' ')[0])
            sm = second.split(' ')[1]
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

        # if before("8:30 AM", "1:30 PM"):
        #     print("worked")

        #print("Name \t\t\t\t MM \t WIN \t Lit \t Math \t SS")
        data["students"] = []
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
            
            # if len(key) > 15:
            #     print(key + "\t\t" + MM + "\t" + WIN + "\t" + Lit + "\t" + Math + "\t" + SS)
            # else:
            #     print(key + "\t\t\t" + MM + "\t" + WIN + "\t" + Lit + "\t" + Math + "\t" + SS)
            data["students"].append([key, MM, WIN, Lit, Math, SS])
    return render_template('attendance.html', data = data)
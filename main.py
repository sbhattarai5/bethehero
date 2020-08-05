## TODO
## Add recommendation
## Immediately work for contests
## Homepage
## Contests

from flask import Flask, request, render_template, url_for, redirect, session, send_from_directory, flash

import time
import os
import subprocess
from DBmediator import *
from send_email import *
from pathlib import Path 


##TODO
####################################################
#link to profile
#add crown on the no. 1 to show the king
#add approve questions
#add solving table
#add kudos
#think about adding friends
#expand the Userclass
#sending links
#can think more about groups
#can think about challenges
###################################################

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = os.urandom(24)
dbmediator = DBmediator(user='root', db='bethehero')

def allowedtxtfile(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == "txt"

def allowedcodefile(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ["cpp"]

def allowedimgfile(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ["jpg", "jpeg", "png"]



def check_session():
    return 'logged_in' in session

@app.route('/showrecommendedusers')
def showrecommendedusers():
    if not check_session(): return redirect(url_for('login'))
    Userid = session['logged_in']['Userid']
    User = dbmediator.getuser(Userid).data
    Recommendedusers = dbmediator.getrecommendedusers(Userid).data
    return render_template("showrecommendedusers.html", User=User, Recommendedusers=Recommendedusers)
    
@app.route('/showusers')
def showusers():
    if not check_session(): return redirect(url_for('login'))
    Userid = session['logged_in']['Userid']
    User = dbmediator.getuser(Userid).data
    follower = request.args.get('follower')
    followee = request.args.get('followee')
    print (follower, followee)
    Allusers = dbmediator.getallusers((Userid,), int(follower), int(followee)).data
    return render_template("showusers.html", User=User, Allusers=Allusers)
    
@app.route('/')
def main():
    if not check_session(): return redirect(url_for('login'))
    Userid = session['logged_in']['Userid']
    User = dbmediator.getuser(Userid).data
    return render_template("main.html", User=User)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if check_session(): session.pop('logged_in', None)
    if request.method == 'POST':
        Username = request.form['Username']
        Password = request.form['Password']
        ret = dbmediator.check_signin(Username, Password)
        if ret.success:
            Userid = dbmediator.getuserid(Username).data
            if not dbmediator.isverified(Userid).data:
                if dbmediator.isverificationexpired(Userid).data:
                    send_verification_email(Userid)
                    flash("New email sent. Please verify!")
                else:
                    flash("Please verify your email first!")
                return redirect(url_for('login'))
            session['logged_in'] = {"Userid": Userid, "timestamp": datetime.now()}
            flash("Welcome " + Username + '!')
            return redirect(url_for('main'))
        flash(ret.msg)
    return render_template("login.html")

@app.route('/changepp', methods=['POST'])
def changepp():
    if not check_session(): return redirect(url_for('login'))
    Userid = session['logged_in']['Userid']
    file = request.files['newpp']
    if allowedimgfile(file.filename):
        file.save('static/pp' + str(Userid) + '.jpg')
    else:
        flash("Invalid file format!")
    return redirect(url_for('showmyprofile'))

@app.route('/follow/<Followerid>/<Followeeid>', methods=["POST"])
def follow(Followerid, Followeeid):
    if not check_session(): return redirect(url_for('login'))
    if int(Followerid) != session['logged_in']['Userid']:
        return redirect(url_for('main'))
    if not dbmediator.isfollowing(Followerid, Followeeid).data:
        dbmediator.addfollower(Followerid, Followeeid)
    return redirect(request.referrer)

@app.route('/unfollow/<Followerid>/<Followeeid>', methods=["POST"])
def unfollow(Followerid, Followeeid):
    if not check_session(): return redirect(url_for('login'))
    if int(Followerid) != session['logged_in']['Userid']:
        return redirect(url_for('main'))
    print (Followerid, Followeeid)
    if dbmediator.isfollowing(Followerid, Followeeid).data:
        dbmediator.deletefollower(Followerid, Followeeid)
    return redirect(request.referrer)

@app.route('/showmyprofile')
def showmyprofile():
    if not check_session(): return redirect(url_for('login'))
    Userid = session['logged_in']['Userid']
    User = dbmediator.getuser(Userid).data
    return render_template("showmyprofile.html", User=User)
    
@app.route('/showprofile/<Userid>')
def showprofile(Userid):
    if not check_session(): return redirect(url_for('login'))
    if int(Userid) == session['logged_in']['Userid']:
        return redirect(url_for('showmyprofile'))
    if not dbmediator.isvaliduserid(Userid).data: return redirect(url_for('main'))
    Otheruser = dbmediator.getuser(Userid).data
    User = dbmediator.getuser(session['logged_in']['Userid']).data
    isfollowing = dbmediator.isfollowing(session['logged_in']['Userid'], Userid).data
    return render_template("showprofile.html", User=User, Otheruser=Otheruser, isfollowing=isfollowing)
    

def send_verification_email(Userid):
    dbmediator.generatenewsecretkey(Userid).data
    link = dbmediator.getverificationurl(Userid).data
    email = dbmediator.getemail(Userid).data
    send_email_from_python(email, link)
    return

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if check_session(): return redirect(url_for('main'))
    if request.method == 'POST':
        Fname = request.form['Fname']
        Lname = request.form['Lname']
        Email = request.form['Email']
        Username = request.form['Username']
        Password = request.form['Password']
        ret = dbmediator.add_user(Fname, Lname, Email, Username, Password)
        if ret.success:
            Userid = dbmediator.getuserid(Username).data
            send_verification_email(Userid)
            command = "cp static/default-profile-pic.jpg static/pp" + str(Userid) + ".jpg"
            os.system(command)
            flash("User successfully added! Please verify from your email!")
            return redirect(url_for('login'))
        flash(ret.msg)
    return render_template("signup.html")

def verifykey(Userid, Secretkey):
    return dbmediator.verifykey(Userid, Secretkey).data

@app.route('/verifyuser/<Userid>/<Secretkey>')
def verifyuser(Userid, Secretkey):
    if dbmediator.isverified(Userid).data:
        flash("User already verified!")
    elif verifykey(Userid, Secretkey):
        dbmediator.verifyuser(Userid)
        flash("User verified successfully!")
    else:
        flash("Invalid verifying URL")
    return redirect(url_for('main'))    

@app.route('/mysubmissions')
def mysubmissions():
    if not check_session(): return redirect(url_for('login'))
    Userid = session['logged_in']['Userid']
    User = dbmediator.getuser(Userid).data
    Submissions = dbmediator.getsubmissions(Userid).data
    return render_template("mysubmissions.html", User=User, Submissions=Submissions)
    
@app.route('/solve')
def solve():
    if not check_session(): return redirect(url_for('login'))
    Userid = session['logged_in']['Userid']
    User = dbmediator.getuser(Userid).data
    Questions = dbmediator.getquestions(Status='A').data
    return render_template("solve.html", User=User, Questions=Questions)

@app.route('/solvequestion/<Questionid>', methods=['GET', 'POST'])
def solvequestion(Questionid):
    if not check_session(): return redirect(url_for('login'))
    Userid = session['logged_in']['Userid']
    User = dbmediator.getuser(Userid).data
    if request.method == 'POST':
        newid = dbmediator.getnewsubmissionid().data
        newpath = "./usersubmissions/" + str(newid)
        os.makedirs(newpath, exist_ok=True)
        if request.form['solutionradio'] == 'file':
            file = request.files['solution']
            if allowedcodefile(file.filename):
                file.save(newpath + '/Solution.cpp')
            else:
                flash("Invalid file format!")
                return redirect(request.url)
        else:
            file = open(newpath + '/Solution.cpp', 'w')
            file.write(request.form['codetext'])
            file.close()
        dbmediator.add_submission(Userid, Questionid,datetime.now())
        flash("Submission recieved successfully!")
        evaluate_submission(newid, Questionid, Userid)
        return redirect(url_for("mysubmissions"))
    Question = loadquestion(Questionid)
    return render_template("solvequestion.html", User=User, Question=Question)


## CE = Compilation Error
## TLE = Time limit Exceeded
## WA = Wrong Answer
## RA = Right Answer

def evaluate_submission(Submissionid, Questionid, Userid):
    '''evaluates the given submission'''
    Remarks = ''
    Kudos = 0
    timelimit = 1
    ###compile
    inputfile = "usersubmissions/" + str(Submissionid) + "/Solution.cpp"
    outputfile = "usersubmissions/" + str(Submissionid) + "/Compiled.exe"
    process = subprocess.run(["g++", inputfile, "-o", outputfile], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = process.stdout.decode("utf-8")
    if (process.returncode != 0):
        Remarks = "CE"
    else:
        ##run the program
        dbmediator.increasesubmissionscount(Questionid)
        testcasesinput = ''.join(readlines("questions/q" + str(Questionid), "/Testcaseinput.txt"))
        try:
            process = subprocess.run(["usersubmissions/" + str(Submissionid) + "/Compiled.exe"], text=True, input=testcasesinput, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timelimit)
            stdout = process.stdout
            if (process.returncode != 0):
                Remarks = "RE"
            else:    
                correctoutput = ''.join(readlines("questions/q" + str(Questionid) + '/', "Testcaseoutput.txt"))
                useroutput = stdout
                f = open("usersubmissions/" + str(Submissionid) + "/Useroutput.txt", 'w+')
                f.write(stdout)
                f.close()
                if (correctoutput == useroutput):
                    Remarks = "RA"
                    dbmediator.increasecorrectsubmissionscount(Questionid)
                    Kudos = dbmediator.getmaxkudos(Questionid).data
                    Maxkudos = dbmediator.getmaxkudosgotinthisquestion(Questionid, Userid).data
                else:
                    Remarks = "WA"
        except subprocess.TimeoutExpired:
            Remarks = "TLE"    
    dbmediator.editsubmission(Submissionid, Remarks, Kudos)
    if Kudos != 0 and Maxkudos < Kudos:
        dbmediator.givekudos(Userid, Kudos - Maxkudos)
    return

@app.route('/addquestion', methods=['GET', 'POST'])
def addquestion():
    if not check_session(): return redirect(url_for('login'))
    Userid = session['logged_in']['Userid']
    User = dbmediator.getuser(Userid).data
    if request.method == 'POST':
        newid = dbmediator.getnewquestionid().data
        newpath = "./questions/q" + str(newid)
        os.makedirs(newpath, exist_ok=True)
        ##Questiontitle
        Questiontitle = request.form['Questiontitle']
        ##Questionstatement
        if request.form['qstatementradio'] == 'file':
            file = request.files['Questionstatement']
            if allowedtxtfile(file.filename):
                file.save(newpath + '/Questionstatement.txt')
            else:
                flash("Invalid file format!")
                return redirect(url_for(request.url))
        else:
            file = open(newpath + '/Questionstatement.txt', 'w')
            file.write(request.form['Questionstatement'])
            file.close()
        ##Inputformat    
        if request.form['iformatradio'] == 'file':
            file = request.files['Inputformat']
            if allowedtxtfile(file.filename):
                file.save(newpath + '/Inputformat.txt')
            else:
                flash("Invalid file format!")
                return redirect(url_for(request.url))
        else:
            file = open(newpath + '/Inputformat.txt', 'w')
            file.write(request.form['Inputformat'])
            file.close()
        ##Outputformat
        if request.form['oformatradio'] == 'file':
            file = request.files['Outputformat']
            if allowedtxtfile(file.filename):
                file.save(newpath + '/Outputformat.txt')
            else:
                flash("Invalid file format!")
                return redirect(url_for(request.url))
        else:
            file = open(newpath + '/Outputformat.txt', 'w')
            file.write(request.form['Outputformat'])
            file.close()
        ##Constraints
        if request.form['cradio'] == 'file':
            file = request.files['Constraints']
            if allowedtxtfile(file.filename):
                file.save(newpath + '/Constraints.txt')
            else:
                flash("Invalid file format!")
                return redirect(url_for(request.url))
        else:
            file = open(newpath + '/Constraints.txt', 'w')
            file.write(request.form['Constraints'])
            file.close()
        ##Sampleinput
        if request.form['sinputradio'] == 'file':
            file = request.files['Sampleinput']
            if allowedtxtfile(file.filename):
                file.save(newpath + '/Sampleinput.txt')
            else:
                flash("Invalid file format!")
                return redirect(url_for(request.url))
        else:
            file = open(newpath + '/Sampleinput.txt', 'w')
            file.write(request.form['Sampleinput'])
            file.close()
        ##Sampleoutput
        if request.form['soutputradio'] == 'file':
            file = request.files['Sampleoutput']
            if allowedtxtfile(file.filename):
                file.save(newpath + '/Sampleoutput.txt')
            else:
                flash("Invalid file format!")
                return redirect(url_for(request.url))
        else:
            file = open(newpath + '/Sampleoutput.txt', 'w')
            file.write(request.form['Sampleoutput'])
            file.close()
        ##Explanation
        if request.form['eradio'] == 'file':
            file = request.files['Explanation']
            if allowedtxtfile(file.filename):
                file.save(newpath + '/Explanation.txt')
            else:
                flash("Invalid file format!")
                return redirect(url_for(request.url))
        else:
            file = open(newpath + '/Explanation.txt', 'w')
            file.write(request.form['Explanation'])
            file.close()
        ##Testcaseinput
        if request.form['tcinputradio'] == 'file':
            file = request.files['Testcaseinput']
            if allowedtxtfile(file.filename):
                file.save(newpath + '/Testcaseinput.txt')
            else:
                flash("Invalid file format!")
                return redirect(url_for(request.url))
        else:
            file = open(newpath + '/Testcaseinput.txt', 'w')
            file.write(request.form['Testcaseinput'])
            file.close()
            
        ##Testcaseoutput
        if request.form['tcoutputradio'] == 'file':
            file = request.files['Testcaseoutput']
            if allowedtxtfile(file.filename):
                file.save(newpath + '/Testcaseoutput.txt')
            else:
                flash("Invalid file format!")
                return redirect(url_for(request.url))
        else:
            file = open(newpath + '/Testcaseoutput.txt', 'w')
            file.write(request.form['Testcaseoutput'])
            file.close()
            
        dbmediator.add_question(Userid, Questiontitle)
        flash("Question added successfully! Please wait for Admin's approval for getting Kudos!")
    return render_template("addquestion.html", User=User)

@app.route('/leaderboard')
def leaderboard():
    if not check_session(): return redirect(url_for('login'))
    Userid = session['logged_in']['Userid']
    User = dbmediator.getuser(Userid).data
    Leaderboard = dbmediator.getleaderboard().data
    return render_template("leaderboard.html", Leaderboard=Leaderboard, User=User)

@app.route('/showpendingquestions/')
def showpendingquestions():
    if not check_session(): return redirect(url_for('login'))
    if not dbmediator.isadmin(session['logged_in']['Userid']).data:
        return redirect(url_for('main'))
    Userid = session['logged_in']['Userid']
    User = dbmediator.getuser(Userid).data
    Questions = dbmediator.getquestions(Status='P').data
    return render_template("showpendingquestions.html", User=User, Questions=Questions)

@app.route('/approveordeclinequestion/<Questionid>', methods=['GET', 'POST'])
def approveordeclinequestion(Questionid):
    if not check_session(): return redirect(url_for('login'))
    if not dbmediator.isadmin(session['logged_in']['Userid']).data:
        return redirect(url_for('main'))
    QapprovedKudos = 5
    Userid = session['logged_in']['Userid']
    User = dbmediator.getuser(Userid).data
    if request.method == 'POST':
        if request.form['decisionradio'] == 'approved':
            dbmediator.approvequestion(Questionid, request.form['Maxkudos'], request.form['difficultylevel'])
            Userid = dbmediator.getwhosubmitted(Questionid).data
            dbmediator.givekudos(Userid, QapprovedKudos)
            flash("Question approved successfully!")
            return redirect(url_for('showpendingquestions'))
        else:
            dbmediator.declinequestion(Questionid)
            flash("Question declined successfully!")
            return redirect(url_for('showpendingquestions'))
    Question = loadquestion(Questionid)
    return render_template("approveordeclinequestion.html", Question=Question, User=User)
        
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("Logged out successfully!") 
    return redirect(url_for('login'))    

class Question:
    def __init__(self, Questionid, Questiontitle, Questionstatement, Inputformat, Outputformat, Constraints, Sampleinput, Sampleoutput, Explanation):
        self.Questionid = Questionid
        self.Questiontitle = Questiontitle
        self.Questionstatement = Questionstatement
        self.Inputformat = Inputformat
        self.Outputformat = Outputformat
        self.Constraints = Constraints
        self.Sampleinput = Sampleinput
        self.Sampleoutput = Sampleoutput
        self.Explanation = Explanation

def readlines(path, filename):
    lines = []
    with open(path + filename, 'r') as f:
        lines = f.readlines()
    return lines

def loadquestion(Questionid):
    path = 'questions/q' + str(Questionid) + '/'
    Questiontitle = dbmediator.getquestiontitle(Questionid).data
    Questionstatement = readlines(path, 'Questionstatement.txt')
    Inputformat = readlines(path, 'Inputformat.txt')
    Outputformat = readlines(path, 'Outputformat.txt')
    Constraints = readlines(path, 'Constraints.txt')
    Sampleinput = readlines(path, 'Sampleinput.txt')
    Sampleoutput = readlines(path, 'Sampleoutput.txt')
    Explanation = readlines(path, 'Explanation.txt')
    return Question(Questionid, Questiontitle, Questionstatement, Inputformat, Outputformat,
                    Constraints, Sampleinput, Sampleoutput, Explanation)
    

@app.route('/downloadtestcaseinput/<Questionid>')
def downloadtestcaseinput(Questionid):
    if not check_session(): return redirect(url_for('login'))
    if not dbmediator.isadmin(session['logged_in']['Userid']).data:
        return redirect(url_for('main'))
    return send_from_directory('questions/q' + str(Questionid),
                               'Testcaseinput.txt', as_attachment=True)

@app.route('/downloadtestcaseoutput/<Questionid>')
def downloadtestcaseoutput(Questionid):
    if not check_session(): return redirect(url_for('login'))
    if not dbmediator.isadmin(session['logged_in']['Userid']).data:
        return redirect(url_for('main'))
    return send_from_directory('questions/q' + str(Questionid), 'Testcaseoutput.txt', as_attachment=True)

@app.route('/downloadsubmittedcode/<Submissionid>')
def downloadsubmittedcode(Submissionid):
    if not check_session(): return redirect(url_for('login'))
    if not dbmediator.isadmin(session['logged_in']['Userid']).data and dbmediator.getwhosubmittedcode(Submissionid).data != session['logged_in']['Userid']:
        return redirect(url_for('main'))
    return send_from_directory('usersubmissions/' + str(Submissionid),
                               'Solution.cpp', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)


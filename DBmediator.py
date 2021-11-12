################################################
## error codes
## 1 -- invalid username or password
## 2 -- error while running the sql
################################################

import MySQLdb
from datetime import datetime, timedelta
from ReturnObj import *
import secrets


class User:
    def __init__(self, Userid, Username, Kudos, Admin, Followers, Followees):
        self.Userid = Userid
        self.Username = Username
        self.Kudos = Kudos
        self.Admin = Admin
        self.Followers = Followers
        self.Followees = Followees


class DBmediator:
    """mediates between the user and the database.. main purpose of this class is to avoid the direct interaction between the user and the database"""

    def __init__(self, user, db):
        self.user = user
        self.db = db

    def connect(self):
        """connects to the database and returns the connected object"""
        return MySQLdb.connect(user=self.user, db=self.db)

    def dosql(self, sql, params=()):
        """runs the sql commands by creating connection with the database.. uses the sanitization method"""
        print(sql, params)
        db = self.connect()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql, params)
        ret = cursor.fetchall()
        cursor.close()
        db.commit()
        db.close()
        return ret

    def check_signin(self, Username, Password):
        """returns return object with meaningful message"""
        sql = "Select * from Users where Username=%s and Password=%s"
        ret = ReturnObj(lfunction="check sign_in")
        try:
            if (
                self.dosql(sql, (Username, Password)) != ()
            ):  # user found with the given username and password
                ret.success = True
                ret.msg = "Login Successful!"
            else:
                ret.success = False
                ret.errorcode = 1
                ret.msg = "Username or password incorrect"
        except:
            ret.success = False
            ret.error_code = 2
            ret.msg = "Error in SQL"
        return ret

    def add_user(self, Fname, Lname, Email, Username, Password, Kudos=0):
        """returns the ReturnObject"""
        ret = ReturnObj(lfunction="add_user")
        sql = "Insert into Users (Fname, Lname, Email, Username, Password, Kudos) VALUES (%s, %s, %s, %s, %s, %s)"
        params = (Fname, Lname, Email, Username, Password, Kudos)
        try:
            self.dosql(sql, params)
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.msg = "Username or Email not unique!"
            ret.errorcode = 2
        return ret

    def add_question(self, Userid, Questiontitle):
        """adds the question to the Questions table"""
        sql = "Insert into Questions (Userid, Questiontitle) VALUES (%s, %s)"
        params = (Userid, Questiontitle)
        ret = ReturnObj(lfunction="add_question")
        try:
            self.dosql(sql, params)
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.msg = "Error in SQL"
            ret.errorcode = 2
        return ret

    def getuserid(self, Username):
        """returns the id of a given username in the data property of the ReturnObj"""
        ret = ReturnObj(lfunction="getuserid")
        sql = "Select Userid from Users where Username=%s"
        params = (Username,)
        try:
            ret.data = self.dosql(sql, params)[0]["Userid"]
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Cannot find the username or error in the command by the Emperor"
        return ret

    def getusername(self, Userid):
        """returns the Username of a given Userid in the data property of the ReturnObj"""
        ret = ReturnObj(lfunction="getusername")
        sql = "Select Username from Users where Userid=%s"
        params = (Userid,)
        try:
            ret.data = self.dosql(sql, params)[0]["Username"]
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Cannot find the userid or error in the command by the Emperor"
        return ret

    def getemail(self, Userid):
        """returns the email of a given Userid in the data property of the ReturnObj"""
        ret = ReturnObj(lfunction="getemail")
        sql = "Select Email from Users where Userid=%s"
        params = (Userid,)
        try:
            ret.data = self.dosql(sql, params)[0]["Email"]
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Cannot find the userid or error in the command by the Emperor"
        return ret

    def getKudos(self, Userid):
        """returns the Kudos of a given Username in the data property of Ret object"""
        ret = ReturnObj(lfunction="getKudos")
        sql = "Select Kudos from Users where Userid=%s"
        params = (Userid,)
        try:
            ret.data = self.dosql(sql, params)[0]["Kudos"]
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Cannot find the userid or error in the command by the Emperor"
        return ret

    def getleaderboard(self):
        """returns a sorted tuple of users on the basis of Kudos """
        ret = ReturnObj(lfunction="getleaderboard")
        sql = "Select Username, Userid, Kudos from Users where Admin=0 ORDER BY Kudos DESC"
        params = ()
        try:
            ret.data = self.dosql(sql, params)
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def isadmin(self, Userid):
        """returns if the Userid is Admin in the data property of Ret obj"""
        ret = ReturnObj(lfunction="isadmin")
        sql = "Select Username from Users where Userid=%s and Admin=1"
        params = (Userid,)
        try:
            ret.data = self.dosql(sql, params) != ()
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def approvequestion(self, Questionid, Maxkudos, Difficulty):
        """approves the given question in the Questions table"""
        ret = ReturnObj(lfunction="approvequestion")
        sql = "Update Questions set Status='A', Maxkudos=%s, Difficulty=%s where Questionid=%s"
        params = (Maxkudos, Difficulty, Questionid)
        try:
            ret.data = self.dosql(sql, params)
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def declinequestion(self, Questionid):
        """declines the given question in the Questions table"""
        ret = ReturnObj(lfunction="approvequestion")
        sql = "Update Questions set Status='D' where Questionid=%s"
        params = (Questionid,)
        try:
            ret.data = self.dosql(sql, params)
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def getuser(self, Userid):
        """returns the User object in ret.data with all the details of the user"""
        ret = ReturnObj(lfunction="getuser")
        sql1 = "select * from Users where Userid=%s"
        sql2 = "select * from Follows where FolloweeUserid=%s"
        sql3 = "select * from Follows where FollowerUserid=%s"
        params = (Userid,)
        try:
            datasql1 = self.dosql(sql1, params)
            userid = datasql1[0]["Userid"]
            username = datasql1[0]["Username"]
            kudos = datasql1[0]["Kudos"]
            admin = datasql1[0]["Admin"]
            followers = []
            followees = []
            datasql2 = self.dosql(sql2, params)
            for item in datasql2:
                followers.append(item["FollowerUserid"])
            datasql3 = self.dosql(sql3, params)
            for item in datasql3:
                followees.append(item["FolloweeUserid"])
            ret.data = User(
                Userid=userid,
                Username=username,
                Kudos=kudos,
                Admin=admin,
                Followers=followers,
                Followees=followees,
            )
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def getquestions(self, Status):
        """returns the questions from the Questions table where the status is as provided"""
        ret = ReturnObj(lfunction="getquestions")
        sql = "Select Questionid, Users.Userid, Username, Questiontitle, Maxkudos, Difficulty, Submissionscount, Correctsubmissionscount from Questions join Users on Users.Userid=Questions.Userid where Status=%s"
        params = (Status,)
        try:
            ret.data = self.dosql(sql, params)
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def getnewquestionid(self):
        """returns the new Questionid from the Questions table in the data attribute of ReturnObj"""
        sql = "Select MAX(Questionid) as maximum from Questions"
        params = ()
        ret = ReturnObj(lfunction="getnewquestionid")
        try:
            preret = self.dosql(sql, params)
            if preret[0]["maximum"] == None:
                ret.data = 1
            else:
                ret.data = preret[0]["maximum"] + 1
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def getquestiontitle(self, Questionid):
        """returns the Questiontitle of a given Questionid from the Questions table in the data attribute of ReturnObj"""
        sql = "Select Questiontitle from Questions where Questionid=%s"
        params = (Questionid,)
        ret = ReturnObj(lfunction="getquestiontitle")
        try:
            ret.data = self.dosql(sql, params)[0]["Questiontitle"]
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def getwhosubmitted(self, Questionid):
        """returns the Userid who submitted Questionid"""
        sql = "Select Userid from Questions where Questionid=%s"
        params = (Questionid,)
        ret = ReturnObj(lfunction="getwhosubmitted")
        try:
            ret.data = self.dosql(sql, params)[0]["Userid"]
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def givekudos(self, Userid, Kudos):
        """adds Kudos to the total Kudos of Userid"""
        sql = "Select Kudos from Users where Userid=%s"
        params = (Userid,)
        ret = ReturnObj(lfunction="givekudos")
        try:
            Kudos += self.dosql(sql, params)[0]["Kudos"]
            sql = "Update Users set Kudos=%s where Userid=%s"
            params = (Kudos, Userid)
            self.dosql(sql, params)
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def getsubmissions(self, Userid):
        """returns the submissions by the given user"""
        ret = ReturnObj(lfunction="getsubmissions")
        sql = "Select Submissionid, Submissions.Questionid, Questiontitle, Remarks, Submissions.Kudos, Questions.Maxkudos, Submissiontime from Submissions join Questions on Submissions.Questionid=Questions.Questionid where Submissions.Userid=%s ORDER BY Submissiontime DESC"
        params = (Userid,)
        try:
            ret.data = self.dosql(sql, params)
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def getnewsubmissionid(self):
        """returns the new Submissionid from the Submissions table in the data attribute of ReturnObj"""
        sql = "Select MAX(Submissionid) as maximum from Submissions"
        params = ()
        ret = ReturnObj(lfunction="getnewsubmissionid")
        try:
            preret = self.dosql(sql, params)
            if preret[0]["maximum"] == None:
                ret.data = 1
            else:
                ret.data = preret[0]["maximum"] + 1
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def add_submission(self, Userid, Questionid, timestamp):
        """adds the submission to Submissions table"""
        sql = "Insert into Submissions (Userid, Questionid, Submissiontime) VALUES (%s, %s, %s)"
        params = (Userid, Questionid, timestamp)
        ret = ReturnObj(lfunction="add_submission")
        try:
            self.dosql(sql, params)
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.msg = "Error in SQL"
            ret.errorcode = 2
        return ret

    def getwhosubmittedcode(self, Submissionid):
        """returns the Userid who submitted Submissionid"""
        sql = "Select Userid from Submissions where Submissionid=%s"
        params = (Submissionid,)
        ret = ReturnObj(lfunction="getwhosubmittedcode")
        try:
            ret.data = self.dosql(sql, params)[0]["Userid"]
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def editsubmission(self, Submissionid, Remarks, Kudos):
        """edits the given Submission with given parameters"""
        ret = ReturnObj(lfunction="editsubmission")
        sql = "Update Submissions set Remarks=%s, Kudos=%s where Submissionid=%s"
        params = (Remarks, Kudos, Submissionid)
        try:
            ret.data = self.dosql(sql, params)
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def getmaxkudos(self, Questionid):
        """returns the max possible Kudos for a given Questionid"""
        ret = ReturnObj(lfunction="getmaxkudos")
        sql = "Select Maxkudos from Questions where Questionid=%s"
        params = (Questionid,)
        try:
            ret.data = self.dosql(sql, params)[0]["Maxkudos"]
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def increasesubmissionscount(self, Questionid):
        """increases Submissionscount by 1 in Questions table"""
        ret = ReturnObj(lfunction="increasesubmissionscount")
        currentcount = self.dosql(
            "Select Submissionscount from Questions where Questionid=%s", (Questionid,)
        )[0]["Submissionscount"]
        sql = "Update Questions set Submissionscount=%s where Questionid=%s"
        params = (currentcount + 1, Questionid)
        try:
            ret.data = self.dosql(sql, params)
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def increasecorrectsubmissionscount(self, Questionid):
        """increases Correctsubmissionscount by 1 in Questions table"""
        ret = ReturnObj(lfunction="increacorrectsesubmissionscount")
        currentcount = self.dosql(
            "Select Correctsubmissionscount from Questions where Questionid=%s",
            (Questionid,),
        )[0]["Correctsubmissionscount"]
        sql = "Update Questions set Correctsubmissionscount=%s where Questionid=%s"
        params = (currentcount + 1, Questionid)
        try:
            ret.data = self.dosql(sql, params)
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def getmaxkudosgotinthisquestion(self, Questionid, Userid):
        """returns the max Kudos got by a user in the given Question"""
        ret = ReturnObj(lfunction="getmaxkudosgotinthisquestion")
        sql = "Select Max(Kudos) as maximum from Submissions where Questionid=%s and Userid=%s"
        params = (Questionid, Userid)
        try:
            ret.data = self.dosql(sql, params)[0]["maximum"]
            if ret.data == None:
                ret.data = 0
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def isvaliduserid(self, Userid):
        """returns true if the Userid exists"""
        ret = ReturnObj(lfunction="isvaliduserid")
        sql = "Select * from Users where Userid=%s"
        params = (Userid,)
        try:
            ret.data = self.dosql(sql, params) != ()
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def isfollowing(self, Followerid, Followeeid):
        """returns true if followerid is following followeeid"""
        ret = ReturnObj(lfunction="isfollowing")
        sql = "Select * from Follows where FollowerUserid=%s and FolloweeUserid =%s"
        params = (Followerid, Followeeid)
        try:
            ret.data = self.dosql(sql, params) != ()
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def addfollower(self, Followerid, Followeeid):
        """adds the given follower"""
        ret = ReturnObj(lfunction="addfollower")
        sql = "Insert into Follows set FollowerUserid=%s, FolloweeUserid =%s"
        params = (Followerid, Followeeid)
        try:
            ret.data = self.dosql(sql, params) != ()
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def deletefollower(self, Followerid, Followeeid):
        """deletes the given follower"""
        ret = ReturnObj(lfunction="deletefollower")
        sql = "Delete from Follows where FollowerUserid=%s and FolloweeUserid =%s"
        params = (Followerid, Followeeid)
        try:
            ret.data = self.dosql(sql, params) != ()
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def getallusers(self, exclude=(), follower=-1, followee=-1):
        """returns the list of all the users"""
        ret = ReturnObj(lfunction="getallusers")
        sql = "select * from Users where Userid not in %s and Admin=0 ORDER BY Username"
        exclude += (1,)
        params = (exclude,)
        try:
            ret.data = []
            allusers = self.dosql(sql, params)
            for user in allusers:
                u = self.getuser(user["Userid"]).data
                if (follower == -1 or follower in u.Followers) and (
                    followee == -1 or followee in u.Followees
                ):
                    ret.data.append(u)
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def isverified(self, Userid):
        """returns if the given User is verified"""
        ret = ReturnObj(lfunction="isverified")
        sql = "select * from Users where Userid=%s and Verified=1"
        params = (Userid,)
        try:
            ret.data = self.dosql(sql, params) != ()
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def verifyuser(self, Userid):
        """Verifies the given User"""
        ret = ReturnObj(lfunction="verifyuser")
        sql = "Update Users set Verified=1 where Userid=%s"
        params = (Userid,)
        try:
            self.dosql(sql, params)
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def getrandomusers(self, limit, exclude=()):
        """returns a list of random users of size limit excluding the Userid in exclude tuple"""
        ret = ReturnObj(lfunction="getrandomusers")
        sql = "SELECT * FROM Users where Userid NOT IN %s ORDER BY RAND() LIMIT %s"
        params = (exclude, limit)
        try:
            ret.data = []
            datasql = self.dosql(sql, params)
            for user in datasql:
                ret.data.append(self.getuser(user["Userid"]).data)
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def getrecommendedusers(self, Userid, exclude=()):
        """returns the recommended list of Users for the given Userid"""
        ret = ReturnObj(lfunction="getrecommendedusers")
        totallimit = 5
        exclude += (Userid, 1)
        sql0 = "select FolloweeUserid from Follows where FollowerUserid=%s"
        params0 = (Userid,)
        sql1 = "Select A.FolloweeUserid as Userid from Follows as A join (Select FolloweeUserid from Follows where FollowerUserid=%s) as B on A.FollowerUserid = B.FolloweeUserid where A.FolloweeUserid not in %s LIMIT %s"
        sql2 = "Select A.FolloweeUserid as Userid from Follows as A join (Select FollowerUserid from Follows where FolloweeUserid=%s) as B on A.FollowerUserid = B.FollowerUserid where A.FolloweeUserid not in %s LIMIT %s"
        try:
            ret.data = []
            datasql0 = self.dosql(sql0, params0)
            for user in datasql0:
                exclude += (user["FolloweeUserid"],)
            params1 = (Userid, exclude, totallimit)
            datasql1 = self.dosql(sql1, params1)
            for user in datasql1:
                ret.data.append(self.getuser(user["Userid"]).data)
                exclude += (user["Userid"],)
            params2 = (Userid, exclude, totallimit - len(ret.data))
            datasql2 = self.dosql(sql2, params2)
            for user in datasql2:
                ret.data.append(self.getuser(user["Userid"]).data)
                exclude += (user["Userid"],)
            ret.data += self.getrandomusers(totallimit - len(ret.data), exclude).data
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"

        return ret

    def verifykey(self, Userid, Secretkey):
        """returns if the given secretkey belongs to the user and not expired"""
        ret = ReturnObj(lfunction="verifykey")
        sql = "select Expiresat from Verifications where Userid=%s and Secretkey=%s"
        params = (Userid, Secretkey)
        try:
            data = self.dosql(sql, params)
            ret.data = False
            current_time = datetime.now()
            for item in data:
                if item["Expiresat"] > current_time:
                    ret.data = True
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        return ret

    def getverificationurl(self, Userid):
        """returns current verificationurl for existing Userid"""
        ret = ReturnObj(lfunction="getverificationurl")
        sql = "Select Secretkey from Verifications where Userid=%s"
        params = (Userid,)
        try:
            data = self.dosql(sql, params)
            if data == ():
                raise Exception()
            else:
                ret.data = (
                    "http://127.0.0.1:5000/verifyuser/"
                    + str(Userid)
                    + "/"
                    + data[0]["Secretkey"]
                )
                print(ret.data)
            ret.success = True
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        print(ret.lfunction, ret.success)
        return ret

    def generatenewsecretkey(self, Userid):
        """generates new secretkey for the given user"""
        Secretkey = secrets.token_urlsafe(32)
        ret = ReturnObj(lfunction="generatenewsecretkey")
        sql = "select * from Verifications where Userid=%s"
        params = (Userid,)
        try:
            Expiresat = datetime.now() + timedelta(hours=6)  # expires in 6 hours
            if self.dosql(sql, params) != ():  # user already exists
                sql = "Update Verifications set Secretkey=%s, Expiresat=%s where Userid=%s"
                params = (Secretkey, Expiresat, Userid)
                print(sql % params)
                self.dosql(sql, params)
            else:
                sql = "Insert into Verifications (Userid, Secretkey, Expiresat) VALUES (%s, %s, %s)"
                params = (Userid, Secretkey, Expiresat)
                self.dosql(sql, params)
            ret.success = True
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        print(ret.lfunction, ret.success)
        return ret

    def isverificationexpired(self, Userid):
        """returns if the given user has unexpired key"""
        ret = ReturnObj(lfunction="isverificationexpired")
        sql = "select Expiresat from Verifications where Userid=%s"
        params = (Userid,)
        try:
            data = self.dosql(sql, params)[0]["Expiresat"]
            ret.data = False
            current_time = datetime.now()
            print(data, current_time)
            if data < current_time:
                ret.data = True
            ret.success = True
            ret.msg = "Success!"
        except:
            ret.success = False
            ret.errorcode = 2
            ret.msg = "Error in SQL statement!"
        print(ret.lfunction, ret.success)
        return ret

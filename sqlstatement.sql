-- All the table creation statements, used for automation
-- using database

USE bethehero;

-- creating tables

--Users

CREATE TABLE Users (
Userid INT AUTO_INCREMENT,
Username VARCHAR(100) UNIQUE,
Password VARCHAR(100),
Fname VARCHAR(100) NOT NULL,
Lname VARCHAR(100) NOT NULL,
Email VARCHAR(100) NOT NULL UNIQUE,
Kudos INT default 0,
Admin TINYINT(1) default 0 NOT NULL,
Verified TINYINT(1) default 0 NOT NULL,
PRIMARY KEY (Userid)
) engine=innodb;

--Questions

CREATE TABLE Questions (
Questionid INT AUTO_INCREMENT,
Userid INT,
Questiontitle VARCHAR(100) NOT NULL,
Maxkudos INT,
Status enum('A', 'D', 'P') default 'P' NOT NULL,
Difficulty enum('E', 'M', 'H'),
Submissionscount INT default 0,
Correctsubmissionscount INT default 0,
PRIMARY KEY (Questionid),
FOREIGN KEY(Userid) REFERENCES Users(Userid)
) engine=innodb;


--Submissions
CREATE TABLE Submissions (
Submissionid INT AUTO_INCREMENT,
Userid INT,
Questionid INT,
Remarks enum('RA', 'WA', 'PJ', 'TLE', 'RE', 'CE') default 'PJ',
Kudos INT,
Submissiontime TIMESTAMP,
PRIMARY KEY (Submissionid),
FOREIGN KEY(Userid) REFERENCES Users(Userid),
FOREIGN KEY(Questionid) REFERENCES Questions(Questionid)
) engine=innodb;

--Follows
CREATE TABLE Follows (
Followid INT AUTO_INCREMENT,
FollowerUserid INT NOT NULL,
FolloweeUserid INT NOT NULL,
Followtime TIMESTAMP,
PRIMARY KEY(Followid),
FOREIGN KEY(FollowerUserid) REFERENCES Users(Userid),
FOREIGN KEY(FolloweeUserid) REFERENCES Users(Userid)
) engine=innodb;


--Verifications
CREATE TABLE Verifications (
Vid INT AUTO_INCREMENT,
Userid INT NOT NULL,
Secretkey VARCHAR(100) NOT NULL,
Expiresat TIMESTAMP,
PRIMARY KEY(Vid),
FOREIGN KEY(Userid) REFERENCES Users(Userid)
) engine=innodb;

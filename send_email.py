import smtplib, ssl

def send_email_from_python(receiver_email, link):
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    sender_email = "bethehero.noreply@gmail.com"
    password = "" #type the password
    subject = "Verify your bethehero account"
    text = "Hi there,\n\nPlease verify you bethehero account by clicking this link: " + link + ".This link expires in 6 hours.\n\nThank you,\nBeTheHero team"
    message = "Subject: {}\n\n{}".format(subject, text)
    
    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server,port)
        server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        server.ehlo() # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit() 

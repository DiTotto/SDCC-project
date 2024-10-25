# import packages
# below packages are built-in - no need to install anything new!
# yupi :)
import smtplib, json
from email.message import EmailMessage

# set your email and password
# please use App Password
email_address = "sdccdmdt@gmail.com"
email_password = "ecfvmlqnrfqtedfb"
def send(text, nome):

    # Apriamo il file in modalità lettura
    with open('indirizzi.json', 'r') as file:
    # Carichiamo il contenuto del file in un oggetto JSON
        dati = json.load(file)

    # Creiamo un dizionario Python a partire dall'oggetto JSON
    dizionario = dict(dati)

    if nome in dizionario.keys():
        indirizzo = dizionario[nome]
        #print(indirizzo)
    else:
        #print("Il valore cercato non è presente nel dizionario.")
        indirizzo = email_address


    # create email
    #print(emailto)
    msg = EmailMessage()
    msg['Subject'] = "Email subject"
    msg['From'] = email_address
    msg['To'] = indirizzo
    msg.set_content(text)

    # send email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email_address, email_password)
        smtp.send_message(msg)
    return 0

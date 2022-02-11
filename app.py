from cgitb import text
from tokenize import Number
from urllib import response
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

#tls=True, tlsAllowInvalidCertificates=True
#cluster = MongoClient("YOUR_MONGODB_URI", tls=True, tlsAllowInvalidCertificates=True)

cluster = MongoClient("mongodb+srv://admacsgloba:Andromeda2016@cluster0.ymjij.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster["whatsapp_data"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)

@app.route("/", methods=["get", "post"])
def reply():

    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp:", "")    
    response = MessagingResponse()
    user = users.find_one({"number": number})  

    if bool(user) == False: 
        response.message("Hola, Favor de seleccionar alguna de las siguientes opciones:"
                    "\n\n*Opciones*\n\n 1️⃣ Datos de contacto \n 2️⃣ Opciones \n 3️⃣ Horarios \n 4️⃣ "
                    "Direccion")       
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            options = int(text)
        except:
            response.message("Ingresar un valor valido")
            return str(response)

        if options == 1:
            response.message("favor de contactarte a:\n\n"
                             "Telefono: 0000000000\n\n"
                             "Mail: contacto@acsglobal.org")
        elif options == 2:
            response.message("Favor de ingresar una de las siguientes opciones:")
            users.update_one({"number": number}, {"$set": {"status": "opcion" }})
            response.message("Opciones: \n\n1️⃣ numero 1  \n2️⃣ numero 2 \n3️⃣ numero 3"
                "\n4️⃣ numero 4 \n5️⃣ numero 5 \n6️⃣ numero 6 \n7️⃣ numero 7 \n8️⃣ numero 8 \n9️⃣ numero 9  \n0️⃣ Regresar a el menu principal")
        #0️⃣1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣🔟
        elif options == 3: 
            response.message("Nuestros horarios son de 8 am a 5 pm")
        elif options == 4:
            response.message("Nuetra direccion es calle sin numero 1 toluca mexico")
        else:
            response.message("Ingresar un valor valido")
            return str(response)            
    elif user["status"] == "opcion":
        try:
            options = int(text)
        except:
            response.message("Ingresar un valor valido")
            return str(response)

        if options == 0:
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            response.message("Favor de seleccionar alguna de las siguientes opciones:"
                    "\n\n*Opciones*\n\n 1️⃣ Datos de contacto \n 2️⃣ Opciones \n 3️⃣ Horarios \n 4️⃣ "
                    "Direccion")
        elif 1 <= options <= 9:
            Numeros_Seleccionados = ["1","2","3","4","5","6","7","8","9"]
            selected = Numeros_Seleccionados[options - 1]
            users.update_one({"number": number}, {"$set": {"status": "direccion"}})
            users.update_one({"number": number}, {"$set": {"numero": selected}})
            response.message("gracias por su seleccion")
            response.message("favor de ingresar una direccion")
        else:
            response.message("Ingresar un valor valido") 

    elif user["status"] == "direccion":
        selected = user["numero"]
        response.message("Gracias por la direccion")
        response.message(f"Tu orden fue {selected}")
        orders.insert_one({"number": number,"numero": selected, "direccion": text, "fecha de orden": datetime.now()})
        users.update_one({"number": number}, {"$set": {"status": "orden"}})
    elif user["status"] == "orden":
        response.message("Hola, Favor de seleccionar alguna de las siguientes opciones, de nuevo:"
                    "\n\n*Opciones*\n\n 1️⃣ Datos de contacto \n 2️⃣ Opciones \n 3️⃣ Horarios \n 4️⃣ "
                    "Direccion")
        users.update_one({"number": number}, {"$set": {"status": "main"}})
    
    users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})
    return str(response)

if __name__ == "__main__":
    app.run()

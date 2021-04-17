from flask import Flask, render_template, request, redirect
from werkzeug.security import check_password_hash, generate_password_hash
import redis
import os

app = Flask(__name__)

db = redis.from_url(os.environ["REDISCLOUD_URL"]) 

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/crear_usuario")
def nuevo_usuario():
    return render_template("crear_usuario.html")

@app.route("/agregar_usuario", methods=["POST"])
def agregar_usuario():
    nombre=request.form.get("nombre")
    contraseña=request.form.get("contraseña")

    if db.exists("user:" +nombre):
        error = "Ya existe el usuario, por favor use otro."
        return render_template("crear_usuario.html", error=error)
    else:
        contraseña_hash = generate_password_hash(contraseña,"pbkdf2:sha256")
        db.set("user:" +nombre, contraseña_hash)
        return redirect("/")


    


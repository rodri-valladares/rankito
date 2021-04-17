from flask import Flask, render_template, request
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

    return render_template("crear_usuario.html")


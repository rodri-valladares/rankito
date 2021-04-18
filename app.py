from flask import Flask, render_template, request, redirect, make_response
from werkzeug.security import check_password_hash, generate_password_hash
import redis
import os

app = Flask(__name__)

db = redis.from_url(os.environ["REDISCLOUD_URL"])


@app.route("/limpiar")
def limpiar():
    db.delete("rankito")


@app.route("/")
def home():
    usuario_logueado = request.cookies.get("usuario_logueado")

    datos = db.zrevrange("rankito", 0, -1, withscores=True)
    rankito = []

    for dato in datos:
        texto = dato[0].decode("utf-8")
        puntaje = int(dato[1])
        usuario = db.get(texto).decode("utf-8")
        votable = usuario_logueado != usuario
        kito = {
            "texto": texto,
            "puntaje": puntaje,
            "votable": votable,
            "usuario": usuario,
        }
        rankito.append(kito)

    return render_template(
        "index.html", usuario_logueado=usuario_logueado, rankito=rankito,
    )


@app.route("/crear_usuario")
def nuevo_usuario():
    return render_template("crear_usuario.html")


@app.route("/agregar_usuario", methods=["POST"])
def agregar_usuario():
    nombre = request.form.get("nombre")
    contraseña = request.form.get("contraseña")

    if db.exists("user:" + nombre):
        error = "Ya existe el usuario, por favor use otro."
        return render_template("crear_usuario.html", error=error)
    else:
        contraseña_hash = generate_password_hash(contraseña, "pbkdf2:sha256")
        db.set("user:" + nombre, contraseña_hash)
        respuesta = make_response(redirect("/"))
        respuesta.set_cookie("usuario_logueado", nombre)
        return respuesta


@app.route("/ingreso_usuario")
def ingreso_usuario():
    return render_template("ingreso_usuario.html")


@app.route("/login", methods=["POST"])
def login():
    nombre = request.form.get("nombre")
    contraseña = request.form.get("contraseña")

    try:
        contraseña_hash = db.get("user:" + nombre).decode("utf-8")
    except AttributeError as e:
        error = "Contraseña y/o usuario incorrectos"
        return render_template("ingreso_usuario.html", error=error)

    if check_password_hash(contraseña_hash, contraseña):
        respuesta = make_response(redirect("/"))
        respuesta.set_cookie("usuario_logueado", nombre)
        return respuesta
    else:
        error = "Contraseña y/o usuario incorrectos"
        return render_template("ingreso_usuario.html", error=error)


@app.route("/nuevo_kito", methods=["POST"])
def crear_kito():

    kito = request.form.get("kito")
    db.zadd("rankito", {kito: 0})

    db.set(kito, request.cookies.get("usuario_logueado"))
    return redirect("/")


@app.route("/votar_mas_uno", methods=["POST"])
def votar_mas_uno():

    kito = request.form.get("kito")
    db.zincrby("rankito", 1, kito)

    return redirect("/")


@app.route("/votar_menos_uno", methods=["POST"])
def votar_menos_uno():

    kito = request.form.get("kito")
    db.zincrby("rankito", -1, kito)

    return redirect("/")


@app.route("/logout")
def cerrar_sesion():
    respuesta = make_response(redirect("/"))
    respuesta.delete_cookie("usuario_logueado")
    return respuesta

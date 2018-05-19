from flask import Flask,render_template,request,redirect,url_for
import MySQLdb
app= Flask(__name__)

conn=MySQLdb.connect(host="localhost",user="root",password="1234",db="banco")
@app.route("/")
def main():
	return render_template('Index2.html')

@app.route("/registro",methods=['GET','POST'])
def registro():
	if request.method == 'POST':
		user = str(request.form["usuario"])
		nombre = str(request.form["nombre"])
		cont= str(request.form["contrasenia"])
		cursor =conn.cursor()
		cursor.execute("INSERT INTO cliente(usuario,nombre,contrasenia) values(%s,%s,%s)",(user,nombre,cont))
		conn.commit()
		cursor.close()
		return redirect(url_for("main"))
	return render_template('Registro.html')

@app.route("/perfil")
def perfil():
	return render_template("perfil.html")

@app.route("/comprobar",methods=['POST'])
def comprobar():
	if request.method=='POST':
		user = str(request.form["usuario"])
		ps = str(request.form["contrasenia"])
		cursor =conn.cursor()
		try:
			cursor.execute("select * from cliente where usuario =%s",(user,))
			us= cursor.fetchone()
			if us[2] == user:
				if us[1] == ps:
					return redirect(url_for('perfil'))
				else:
					return "fallo al iniciar sesión"
		except:
			return 'error'

if __name__ == "__main__":
	app.run(debug=True)

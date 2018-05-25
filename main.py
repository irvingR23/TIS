from flask import Flask,render_template,request,redirect,url_for,session,jsonify
import MySQLdb
app= Flask(__name__)

app.secret_key = 'secreto'

conn=MySQLdb.connect(host="localhost",user="root",password="1234",db="banco")
@app.route("/",methods=['GET','POST'])
def main():
	session['username']=' '
	if request.method=='POST':
		user = str(request.form["usuario"])
		ps = str(request.form["contrasenia"])
		cursor =conn.cursor()
		try:
			cursor.execute("select * from cliente where usuario =%s",(user,))
			us= cursor.fetchone()
			if us[2] == user:
				if us[1] == ps:
					session['logged_in']=True
					session.pop('username',None)
					session['username']=us[2]
					return redirect(url_for('perfil'))
				else:
					return "fallo al iniciar sesión"
		except:
			try:
				cursor.execute("select * from administrador where usuario =%s",(user,))
				us= cursor.fetchone()
				if us[1] == user:
					if us[2] == ps:
						session['logged_in']=True
						session.pop('username',None)
						session['username']=us[1]
						return redirect(url_for('perfila'))
					else:
						return "fallo al iniciar sesión"
			except:
				return 'error'
	return render_template('Index2.html')
	

@app.route("/registro",methods=['GET','POST'])
def registro():
	if request.method == 'POST':
		user = str(request.form["usuario"])
		nombre = str(request.form["nombre"])
		cont= str(request.form["contrasenia"])
		cursor =conn.cursor()
		cursor.execute("INSERT INTO cliente(usuario,nombre,contrasenia,saldo) values(%s,%s,%s,20000)",(user,nombre,cont))
		conn.commit()
		cursor.close()
		return redirect(url_for("main"))
	return render_template('Registro.html')

@app.route("/perfil")
def perfil():
	cursor=conn.cursor()
	usern=session.get('username')
	cursor.execute("select * from cliente where usuario=%s",(usern,))
	datos=cursor.fetchone()
	return render_template("perfil.html",datos=datos)

@app.route("/salir")
def salir():
	session['logged_in']=False
	return redirect(url_for("main"))

@app.route("/homes")
def homes():
	return redirect(url_for("main"))	

@app.route("/prestamo",methods=['POST','GET'])
def prestamo():
	if request.method=='POST' and session["logged_in"]==True:
		can=int(request.form["cantidad"])
		cursor = conn.cursor()
		noUs=session.get('username')
		cursor.execute("select numeroCuenta from cliente where usuario=%s",(noUs,))
		us=cursor.fetchone()
		cursor.execute("INSERT INTO peticion(nombre,usuario,admin,cantidad,estado) values('peticion',%s,1,%s,'pendiente')",(us[0],can))
		conn.commit()
		cursor.close()
	return render_template('SPrestamo.html')

@app.route("/perfila")
def  perfila():
	cursor=conn.cursor()
	usern=session.get('username')
	cursor.execute("select * from administrador where usuario=%s",(usern,))
	datos=cursor.fetchone()
	return render_template("PerfilAdminist.html",datos=datos)

@app.route("/borrarUsuario")
def borraru():
	cursor=conn.cursor()
	usern=session.get('username')
	cursor.execute("delete cliente from cliente where usuario=%s",(usern,))
	conn.commit()
	cursor.close()
	return redirect(url_for("main"))

@app.route("/crearTarjeta",methods=['POST','GET'])
def crearTarjeta():
	if request.method=='POST':
		user=int(request.form["us"])
		cv=int(request.form["cvv"])
		fechaE=str(request.form["fechaEx"])
		cursor=conn.cursor()
		cursor.execute("select * from cliente where numeroCuenta=%s",(user,))
		dat=cursor.fetchone()
		cursor.execute("INSERT INTO tarjeta(credDisp,deuda,saldo,usuario,CVV,propietario,fechaExpiracion) values(20000,0,15000,%s,%s,%s,%s)",(user,cv,dat[3],fechaE))
		conn.commit()
		return redirect(url_for("perfila"))

@app.route("/estadoCuenta")
def estadoCuenta():
	cursor=conn.cursor()
	us=session.get('username')
	cursor.execute("select * from cliente where numeroC=%s",(us,))
	dat=cursor.fetchone()
	cursor.execute("select * from tarjeta where ")
	return render_template("estadoCuenta.html")

@app.route("/banco/operacion/<int:cantidad>,<int:cuDest>,<int:numeroTarjeta>,<int:cvv>,<string:propietario>,<string:fechaExpiracion>",methods=['GET'])
def transaccion(cantidad,cuDest,numeroTarjeta,cvv,propietario,fechaExpiracion):
	try:
		cursor=conn.cursor()
		can=cantidad
		cuD=cuDest
		nt=numeroTarjeta
		cvvd=cvv
		prop=propietario
		fechaE=fechaExpiracion
		cursor.execute("select * from tarjeta where numero=%s",(nt,))
		dat=cursor.fetchone()
		cursor.execute("select * from cliente where numeroCuenta=%s",(dat[4],))
		cliente=cursor.fetchone()
		valor=cliente[7]-can
		cursor.execute("select * from cliente where numeroCuenta=%s",(cuD,))
		clienteD=cursor.fetchone()
		valord=clienteD[7]+can
		cursor.execute("update cliente set saldo=%s where numeroCuenta=%s",(valor,dat[4]))
		conn.commit()
		cursor.execute("update cliente set saldo=%s where numeroCuenta=%s",(valord,cuD))
		conn.commit()
		cursor.execute("INSERT INTO transac(cantidad,cuDest,numeroTarjeta,cvv,propietario,fechaExpiracion) values(%s,%s,%s,%s,%s,%s)",(can,cuD,nt,cvvd,prop,fechaE))
		conn.commit()
		return jsonify({'exito':True})
	except:
		return jsonify({'exito':False})

if __name__ == "__main__":
	app.run(debug=True)

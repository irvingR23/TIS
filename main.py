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
		existe=0
		cursor =conn.cursor()
		cursor.execute("select * from cliente")
		Usuarios=cursor.fetchall()
		for us in Usuarios:
			if us[2] == user:
				existe=1
		if existe==0:
			try:
				cursor.execute("INSERT INTO cliente(usuario,nombre,contrasenia,saldo) values(%s,%s,%s,20000)",(user,nombre,cont))
				conn.commit()
				cursor.execute("select * from cliente where usuario=%s",(user,))
				cliente=cursor.fetchone()
				cvg=cliente[0]+233
				cursor.execute("INSERT INTO tarjeta(credDisp,deuda,saldo,usuario,cvv,propietario,fechaExpiracion,borrable) values(20000,0,20000,%s,%s,%s,'2021-10-21','no')",(cliente[0],cvg,nombre))
				conn.commit()
				cursor.close()
				return redirect(url_for("main"))
			except:
				return "error ha ingresado datos incorrectos"
		else:
			return "error el usuario existe"
	return render_template('Registro.html')

@app.route("/perfil")
def perfil():
	cursor=conn.cursor()
	usern=session.get('username')
	cursor.execute("select * from cliente where usuario=%s",(usern,))
	datos=cursor.fetchone()
	cursor.execute("select * from tarjeta where usuario=%s",(datos[0],))
	tarjetas=cursor.fetchall()
	return render_template("perfil.html",datos=datos,tarjetas=tarjetas)

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
		try:
			cursor.execute("INSERT INTO peticion(nombre,usuario,admin,cantidad,estado) values('peticion',%s,1,%s,'pendiente')",(us[0],can))
			conn.commit()
			cursor.close()
		except:
			return "Error ha ingresado datos no validos"
	return render_template('SPrestamo.html')

@app.route("/perfila")
def  perfila():
	cursor=conn.cursor()
	usern=session.get('username')
	cursor.execute("select * from administrador where usuario=%s",(usern,))
	datos=cursor.fetchone()
	cursor.execute("select * from peticion")
	peticiones=cursor.fetchall()
	return render_template("PerfilAdminist.html",datos=datos,peticiones=peticiones)

@app.route("/borrarUsuario")
def borraru():
	cursor=conn.cursor()
	usern=session.get('username')
	try:
		cursor.execute("delete from cliente where usuario=%s",(usern,))
		conn.commit()
		cursor.close()
		return redirect(url_for("main"))
	except:
		return "error el usuario todavia tiene tarjetas"

@app.route("/crearTarjeta",methods=['POST','GET'])
def crearTarjeta():
	if request.method=='POST':
		user=int(request.form["us"])
		cv=int(request.form["cvv"])
		fechaE=str(request.form["fechaEx"])
		cursor=conn.cursor()
		cursor.execute("select * from cliente where numeroCuenta=%s",(user,))
		dat=cursor.fetchone()
		try:
			cursor.execute("INSERT INTO tarjeta(credDisp,deuda,saldo,usuario,CVV,propietario,fechaExpiracion,borrable) values(20000,0,15000,%s,%s,%s,%s,'si')",(user,cv,dat[3],fechaE))
			conn.commit()
			return redirect(url_for("perfila"))
		except:
			return "Error datos ingresados no validos"

@app.route("/estadoCuenta")
def estadoCuenta():
	cursor=conn.cursor()
	us=session.get('username')
	cursor.execute("select * from cliente where usuario=%s",(us,))
	dat=cursor.fetchone()
	cursor.execute("select * from tarjeta where usuario=%s",(dat[0],))
	tarjetas=cursor.fetchall()
	return render_template("estadoCuenta.html",dat=dat,tarjetas=tarjetas)

@app.route("/banco/operacion/<int:cantidad>,<int:cuDest>,<int:numeroTarjeta>,<int:cvv>,<string:propietario>,<string:fechaExpiracion>",methods=['GET'])
def transaccion(cantidad,cuDest,numeroTarjeta,cvv,propietario,fechaExpiracion):
	cursor=conn.cursor()
	can=cantidad
	cuD=cuDest
	nt=numeroTarjeta
	cvvd=cvv
	prop=propietario
	fechaE=fechaExpiracion
	cursor.execute("select * from tarjeta where numero=%s",(nt,))
	dat=cursor.fetchone()
	cursor.execute("select * from tarjeta where usuario=%s",(dat[4],))
	cliente=cursor.fetchone()
	valor=cliente[3]-can
	cursor.execute("select * from cliente where numeroCuenta=%s",(cuD,))
	clienteD=cursor.fetchone()
	valord=clienteD[7]+can
	cursor.execute("update tarjeta set saldo=%s where usuario=%s",(valor,dat[4]))
	conn.commit()
	cursor.execute("update cliente set saldo=%s where numeroCuenta=%s",(valord,cuD))
	conn.commit()
	try:
		cursor.execute("INSERT INTO transac(cantidad,cuDest,numeroTarjeta,cvv,propietario,fechaExpiracion,tipo) values(%s,%s,%s,%s,%s,%s,'envio')",(can,cuD,nt,cvvd,prop,fechaE))
		conn.commit()
		return jsonify({'exito':True})
	except:
		return jsonify({'exito':False})

@app.route("/historial")
def historial():
	cursor=conn.cursor()
	us=session.get('username')
	cursor.execute("select * from cliente where usuario=%s",(us,))
	dat=cursor.fetchone()
	cursor.execute("select * from transac where cuDest=%s",(dat[0],))
	recibir=cursor.fetchall()
	cursor.execute("select * from transac where cuRe=%s",(dat[0],))
	dar=cursor.fetchall()
	return render_template("Historial.html",recibir=recibir,dar=dar)

@app.route("/confirmarPrestamo/<int:idf>,<int:cantidad>,<int:peticion>")
def confirmarPrestamo(idf,cantidad,peticion):
	ids=idf
	can=cantidad
	pet=peticion
	cursor=conn.cursor()
	cursor.execute("select * from cliente where numeroCuenta=%s",(ids,))
	saldoI=cursor.fetchone()
	saldoAgregar=saldoI[7]+can
	cursor.execute("update cliente set saldo=%s where numeroCuenta=%s",(saldoAgregar,ids))
	conn.commit()
	cursor.execute("delete from peticion where id=%s",(pet,))
	conn.commit()
	return redirect(url_for("perfila"))

@app.route("/cancelarTarjeta/<int:idt>,<int:deuda>,<string:borrab>")
def cancelarTarjeta(idt,deuda,borrab):
	de=deuda
	i=idt
	b=borrab
	if deuda < 1:
		if b == 'si':
			cursor=conn.cursor()
			cursor.execute("delete from tarjeta where numero=%s",(i,))
		else:
			return "esta la tarjeta no se puede borrar"
	else:
		return "error aun tiene una deuda"

@app.route("/transf",methods=['POST','GET'])
def transf():
	if request.method=='POST':
		ct=int(request.form["cantidad"])
		cnd=int(request.form["cardNumber"])
		nt=int(request.form["numeroT"])
		nomb=str(request.form["propiet"])
		cv=int(request.form["cv"])
		fe=str(request.form["fechae"])
		cursor=conn.cursor()
		use=session.get('username')
		cursor.execute("select * from cliente where usuario=%s",(use,))
		dat=cursor.fetchone()
		try:
			cursor.execute("INSERT INTO transac(cantidad,cuDest,cuRe,numeroTarjeta,cvv,propietario,fechaExpiracion,tipo) values(%s,%s,%s,%s,%s,%s,%s,'envio')",(ct,cnd,dat[0],nt,cv,nomb,fe))
			conn.commit()
			cursor.execute("select * from cliente where numeroCuenta=%s",(cnd,))
			dat1=cursor.fetchone()
			restasaldo=dat[7]-ct
			sumasaldo=dat1[7]+ct
			cursor.execute("update cliente set saldo=%s where numeroCuenta=%s",(restasaldo,dat[0]))
			conn.commit()
			cursor.execute("update cliente set saldo=%s where numeroCuenta=%s",(sumasaldo,dat1[0]))
			conn.commit()
			return redirect(url_for("transf"))
		except:
			return "Error los datos ingresados no son validos"
	return render_template("Transferencia.html")

if __name__ == "__main__":
	app.run(debug=True)

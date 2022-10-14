from flask import Flask, jsonify, render_template, request, send_file
from JSTEG_spatial import hidedata as hide_sp
from JSTEG_spatial import showData as show_sp
from F5__spatial import matrix_encoding as matrix_sp
from F5__spatial import matrix_decoding as decode_sp
from JSTEG_freq import hidedata as hide_freq
from JSTEG_freq import showData as show_freq
from F5_freq import matrix_encoding as matrix_fq
from F5_freq import matrix_decoding as decode_fq
from files import *
import os
import cv2
import base64

app = Flask(__name__)
app.static_folder = 'static'

@app.route("/")
def home():
	return render_template("index.html")

@app.route("/encrypt", methods=['POST', 'GET'])
def encrypt():
	if(request.method == 'GET'):
		return render_template("encrypt.html")
	else:
		# load files
		image = request.files['image']
		message = request.files['message']
		password = request.form.get('password')
		domaine=request.form.get('domaine')
		algo=request.form.get('algos')

		# save files
		image_filename = 'image' + os.path.splitext(image.filename)[1]
		image.save(image_filename)
		message.save('message.txt')

		# DO LOGIC TO CONVERT (IMAGE, MESSAGE, PASSWORD) -> IMAGE
		img = cv2.imread(image_filename)
		msg = file_str('message.txt')
		if (domaine=='Spatial'):
			if(algo=='F5'):
				result = matrix_sp(img, msg,password)
			if(algo=='JSTEG'):
				result=hide_sp(img,msg)
		elif(domaine=='Frequentiel'):
			if(algo=='F5'):
				result = matrix_fq(img, msg)
			if(algo=='JSTEG'):
				result=hide_freq(img,msg)

		
		output = base64.b64encode(cv2.imencode('.png', result)[1]).decode() #encode to base64 (of a jpeg) since it's an image
		
		# TODO: delete the files we created since we don't need em anymore

		# reply with json string of the result
		return jsonify(
			output = output
		)

@app.route("/decrypt", methods=['POST', 'GET'])
def decrypt():
	if(request.method == 'GET'):
		return render_template("decrypt.html")
	else:
		image = request.files['image']
		password = request.form.get('password')
		domaine=request.form.get('domaine')
		algo=request.form.get('algos')
		# save files
		image_filename = 'image' + os.path.splitext(image.filename)[1]
		image.save(image_filename)

		# DO LOGIC TO CONVERT (IMAGE, MESSAGE, PASSWORD) -> IMAGE
		img = cv2.imread(image_filename)
		
		if (domaine=='Spatial'):
			if(algo=='F5'):
				result = decode_sp(img,password)
			if(algo=='JSTEG'):
				result=show_sp(img)
		elif(domaine=='Frequentiel'):
			if(algo=='F5'):
				result = decode_fq(img,password)
			if(algo=='JSTEG'):
				result=show_freq(img)
		

		# TODO: delete the files we created since we don't need em anymore

		# reply with json string of the result
		return jsonify(
			output = result,
		)

if __name__ == "__main__":
	app.run(debug=True)
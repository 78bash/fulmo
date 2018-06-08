from lightning import LightningRpc
from flask import Flask, request, render_template
import random
import qrcode
app = Flask(__name__)

# Connect to local LN node
ln = LightningRpc("/tmp/lightning-rpc")

@app.route("/")
def fulmo():
	return render_template('index.html')

@app.route("/newaddr/")
def newaddr():
	bech32 = request.args.get('type')
	addr = ln.newaddr(bech32)
	return addr['address'] + qr(addr['address'])

@app.route("/getinfo/")
def getinfo():
	info = ln.getinfo()
	return prepare(info) + "On-chain Balance: " + str(listfunds()) + " Millisatoshis"

@app.route("/listfunds/")
def listfunds():
	balance = 0;
        funds = ln.listfunds()
	for item in funds['outputs']:
		balance = balance + item["value"]
	
        return str(balance)

@app.route("/invoice/")
def invoice():
	make_qr = request.args.get("qr")
	satoshis = request.args.get("amount")
	description = request.args.get("description")
	invoice = ln.invoice(satoshis, "lbl{}".format(random.random()), description)
	bolt11 = str(invoice["bolt11"])
	if make_qr is not None:
		return bolt11 + qr("lightning:" + bolt11)
	else:
		return bolt11

@app.route("/help/")
def help():
        help = ln.help()
        return prepare(help)

@app.route("/listchannels/")
def listchannels():
        channels = ln.listpeers()
	print str(channels)
        return prepare(channels)

@app.route("/connect/")
def connect():
	connection_string = request.args.get("c")
	nodeID = connection_string[:connection_string.find("@")]
	ip = connection_string[connection_string.find("@")+1:connection_string.find(":")]
	port = connection_string[connection_string.find(":")+1:]

	connect = ln.connect(nodeID, ip, port)
	return prepare(connect)

def qr(data): 
        img = qrcode.make(data)
        filename = "static/qrcodes/" + data  + ".png"
        img.save(filename)
        return str("<br /><img src='/" + filename + "'height='200' width='200'/>")
        

def prepare(data):
	data_string = ""
	for key, value in data.iteritems():
		if isinstance(value, dict):	
			data_string = prepare(value)
		else:
			data_string = data_string + key + ": " + str(value) + "<br />"

	return data_string

if __name__ == "__main__":
    app.run(host="192.168.0.100",ssl_context='adhoc')

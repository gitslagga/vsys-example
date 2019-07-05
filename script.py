import pyvsystems
from flask import Flask, abort, request, jsonify

import logging
import datetime
import base58
import json

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
logging.warning('logging info test')

# storage data on memory
chain = pyvsystems.testnet_chain()  # pyvsystems.default_chain()
confirms = 31

@app.route('/address', methods=['POST'])
def address():
    data = pyvsystems.Account(chain=chain)
    return jsonify({'code': 0, 'data': {
        'address': data.address,
        'publicKey': data.publicKey,
        'privateKey': data.privateKey,
        'seed': data.seed,
        'nonce': data.nonce,
    }})
    
@app.route('/addressinfo', methods=['POST'])
def addressinfo():
    logging.info("request params: {}".format(request.json))

    if not request.json or 'address' not in request.json or 'publicKey' not in request.json:
        abort(400)
    else:
        address = request.json['address']
        publicKey = request.json['publicKey']
        addressinfo = pyvsystems.Account(chain=chain, address=address, public_key=publicKey).get_info()
        return jsonify({'code': 0, 'data': addressinfo})

@app.route('/addressbalance', methods=['POST'])
def addressbalance():
    logging.info("request params: {}".format(request.json))

    if not request.json or 'address' not in request.json:
        abort(400)
    else:
        address = request.json['address']
        balance = pyvsystems.Account(chain=chain, address=address).balance(confirmations=confirms)
        return jsonify({'code': 0, 'data': balance})



@app.route('/height', methods=['POST'])
def height():
    height = chain.height()
    return jsonify({'code': 0, 'data': height})

@app.route('/lastblock', methods=['POST'])
def lastblock():
    lastblock = chain.lastblock()
    return jsonify({'code': 0, 'data': lastblock})

@app.route('/block', methods=['POST'])
def block():
    logging.info("request params: {}".format(request.json))

    if not request.json or 'height' not in request.json:
        abort(400)
    else:
        height = request.json['height']
        block = chain.block(n=height)
        return jsonify({'code': 0, 'data': block})



@app.route('/check', methods=['POST'])
def check():
    logging.info("request params: {}".format(request.json))

    if not request.json or 'txid' not in request.json:
        abort(400)
    else:
        result = {}
        result['txid'] = request.json['txid']
        result['status'] = pyvsystems.Account(chain=chain).check_tx(request.json['txid'], confirms)
        return jsonify({'code': 0, 'data': result})
        

@app.route('/sendpayment', methods=['POST'])
def sendpayment():
    logging.info("request params: {}".format(request.json))

    if not request.json or 'privateKey' not in request.json or 'address' not in request.json or 'amount' not in request.json:
        abort(400)
    else:
        privatekey = request.json['privateKey']
        address = request.json['address']
        amount = request.json['amount']
        send = pyvsystems.Account(chain=chain, private_key=privatekey)
        recipient = pyvsystems.Account(chain=chain, address=address)
        
    result = {}
    try:
        resp = send.send_payment(recipient, amount=amount)
        print("Payment TX result: {}".format(resp))

        result['txid'] = resp['id']
        result['status'] = send.check_tx(resp['id'], confirms)
        result['time'] = str(datetime.datetime.fromtimestamp(resp['timestamp'] // 1000000000))

        sender_public_key = base58.b58decode(resp['proofs'][0]['publicKey'])
        result['from'] = chain.public_key_to_address(sender_public_key)
        result['to'] = resp['recipient']
        result['amount'] = resp['amount']
        result['fee'] = resp['fee']
    except Exception as ex:
        # Handle Invalid Parameter issue here
        print("Invalid Parameter: {}".format(ex))
        return jsonify({'code': 500})
        
    return jsonify({'code': 0, 'data': result})



if __name__ == "__main__":
    # 将host设置为0.0.0.0，则外网用户也可以访问到这个服务
    app.run(host="0.0.0.0", debug=True)
    
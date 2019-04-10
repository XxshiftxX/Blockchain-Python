from uuid import uuid4

from flask import Flask, jsonify, request

from blockchain import Blockchain


app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
  last_block = blockchain.last_block
  last_proof = last_block['proof']
  proof = blockchain.proof_of_work(last_proof)

  blockchain.new_transaction(
    sender = '0',
    recipient = node_identifier,
    amount = 1,
  )

  previous_hash = blockchain.hash(last_block)
  block = blockchain.new_block(proof, previous_hash)

  res = {
    'message': 'New Block Forged',
    'index': block['index'],
    'transactions': block['transactions'],
    'proof': block['proof'],
    'previous_hash': block['previous_hash'],
  }

  return jsonify(res), 200

  
@app.route('/transactions/new', methods=['POST'])
def new_transactions():
  values = request.get_json()

  required = ['sender', 'recipient', 'amount']

  if not all(k in values for k in required):
    return 'Missing values', 400
  
  index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
  
  res = { 'message': f'Transaction will be added to Block {index}' }
  
  return jsonify(res), 201

@app.route('/chain', methods=['GET'])
def full_chain():
  res = {
    'chain': blockchain.chain,
    'length': len(blockchain.chain),
  }

  return jsonify(res), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
  values = request.get_json()

  nodes = values.get('nodes')
  if nodes is None:
    return 'Error: Please supply a valid list of nodes', 400
  
  for node in nodes:
    blockchain.register_node(node)
  
  res = {
    'message': 'New nodes have been added',
    'total_nodes': list(blockchain.nodes),
  }

  return jsonify(res), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
  replaced = blockchain.resolve_conflicts()

  if replaced:
    res = {
      'message': 'Our chain was replaced',
      'new_chain': blockchain.chain,
    }
  else:
    res = {
      'message': 'Our chain is authoritative',
      'chain': blockchain.chain,
    }
  
  return jsonify(res), 200


if __name__ == '__main__':
  app.run(host= '0.0.0.0', port= int(input('SELECT PORT >> ')))
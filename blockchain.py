import hashlib
import requests
import json
from time import time
from uuid import uuid4
from urllib.parse import urlparse

class Blockchain(object):
  def __init__(self):
    self.chain = []
    self.current_transactions = []
    self.nodes = set()

    self.new_block(previous_hash = 1, proof = 100)
  

  def new_block(self, proof, previous_hash = None):
    block = {
      'index': len(self.chain) + 1,
      'timestamp': time(),
      'transactions': self.current_transactions,
      'proof': proof,
      'previous_hash': previous_hash or self.hash(self.chain[-1]),
    }

    self.current_transactions = []
    self.chain.append(block)

    return block
  

  def new_transaction(self, sender, recipient, amount):
    self.current_transactions.append({
      'sender': sender,
      'recipient': recipient,
      'amount': amount,
    })

    return self.last_block['index'] + 1
  

  @property
  def last_block(self):
    return self.chain[-1]


  @staticmethod
  def hash(block):
    block_string = json.dumps(block, sort_keys= True).encode()
    return hashlib.sha256(block_string).hexdigest()
  
  def proof_of_work(self, last_proof):
    proof = 0
    while self.vaild_proof(last_proof, proof) is False:
      proof += 1
    
    return proof
  
  @staticmethod
  def vaild_proof(last_proof, proof):
    guess = f'{last_proof}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()

    return guess_hash[:4] == '0000'
  
  def register_node(self, address):
    parsed_url = urlparse(address)
    self.nodes.add(parsed_url.netloc)
  
  def vaild_chain(self, chain):
    last_block = chain[0]
    current_index = 1

    while current_index < len(chain):
      block = chain[current_index]
      print(f'{last_block}')
      print(f'{block}')
      print(f'\n--------------\n')
      
      if block['previous_hash'] != self.hash(last_block):
        return False

      if not self.vaild_proof(last_block['proof'], block['proof']):
        return False

      last_block = block
      current_index += 1
    
    return True
  
  def resolve_conflicts(self):
    neighbours = self.nodes
    new_chain = None

    max_length = len(self.chain)

    for node in neighbours:
      res = requests.get(f'http://{node}/chain')

      if res.status_code == 200:
        length = res.json()['length']
        chain = res.json()['chain']

        if length > max_length and self.vaild_chain(chain):
          max_length = length
          new_chain = chain

    if new_chain:
      self.chain = new_chain
      return True
    
    return False
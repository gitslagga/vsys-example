import pyvsystems

# if __name__ == '__main__':
    
print('hello world')
account_info = pyvsystems.Account(chain=pyvsystems.testnet_chain()).get_info()
print(account_info)
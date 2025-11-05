import datetime

class Account:
    def __init__(self, account_id: str, initial_deposit: float):
        self.account_id = account_id
        self.initial_deposit = initial_deposit
        self.balance = initial_deposit
        self.holdings = {}
        self.transactions = []
        self._record_transaction('deposit', initial_deposit, 'Initial deposit')
    
    def deposit_funds(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        self._record_transaction('deposit', amount, f"Deposit: ${amount:.2f}")
    
    def withdraw_funds(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if self.balance - amount < 0:
            return False
        self.balance -= amount
        self._record_transaction('withdraw', amount, f"Withdrawal: ${amount:.2f}")
        return True
    
    def buy_shares(self, symbol: str, quantity: int) -> bool:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        price_per_share = get_share_price(symbol)
        total_cost = price_per_share * quantity
        
        if self.balance < total_cost:
            return False
        
        self.balance -= total_cost
        if symbol in self.holdings:
            self.holdings[symbol] += quantity
        else:
            self.holdings[symbol] = quantity
        
        self._record_transaction('buy', total_cost, f"Bought {quantity} shares of {symbol} at ${price_per_share:.2f}")
        return True
    
    def sell_shares(self, symbol: str, quantity: int) -> bool:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        if symbol not in self.holdings or self.holdings[symbol] < quantity:
            return False
        
        price_per_share = get_share_price(symbol)
        total_value = price_per_share * quantity
        
        self.balance += total_value
        self.holdings[symbol] -= quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
        
        self._record_transaction('sell', total_value, f"Sold {quantity} shares of {symbol} at ${price_per_share:.2f}")
        return True
    
    def calculate_portfolio_value(self) -> float:
        total_value = self.balance
        for symbol, quantity in self.holdings.items():
            price_per_share = get_share_price(symbol)
            total_value += price_per_share * quantity
        return total_value
    
    def calculate_profit_loss(self) -> float:
        current_value = self.calculate_portfolio_value()
        return current_value - self.initial_deposit
    
    def get_holdings(self) -> dict:
        return self.holdings.copy()
    
    def get_transaction_history(self) -> list:
        return self.transactions.copy()
    
    def get_profit_loss_report(self) -> float:
        return self.calculate_profit_loss()
    
    def _record_transaction(self, transaction_type: str, amount: float, description: str):
        timestamp = datetime.datetime.now()
        transaction = {
            'timestamp': timestamp,
            'type': transaction_type,
            'amount': amount,
            'description': description,
            'balance_after': self.balance
        }
        self.transactions.append(transaction)

def get_share_price(symbol: str) -> float:
    prices = {
        'AAPL': 150.00,
        'TSLA': 650.00,
        'GOOGL': 2800.00
    }
    return prices.get(symbol.upper(), 0.0)
import unittest
from unittest.mock import patch
import datetime
import accounts

class TestAccount(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.account = accounts.Account("test123", 1000.0)
    
    def test_initialization(self):
        """Test account initialization with valid parameters."""
        self.assertEqual(self.account.account_id, "test123")
        self.assertEqual(self.account.initial_deposit, 1000.0)
        self.assertEqual(self.account.balance, 1000.0)
        self.assertEqual(self.account.holdings, {})
        self.assertEqual(len(self.account.transactions), 1)
        
        # Check initial transaction
        initial_transaction = self.account.transactions[0]
        self.assertEqual(initial_transaction['type'], 'deposit')
        self.assertEqual(initial_transaction['amount'], 1000.0)
        self.assertEqual(initial_transaction['description'], 'Initial deposit')
    
    def test_deposit_funds_positive(self):
        """Test depositing positive amount."""
        initial_balance = self.account.balance
        self.account.deposit_funds(500.0)
        
        self.assertEqual(self.account.balance, initial_balance + 500.0)
        self.assertEqual(len(self.account.transactions), 2)
        
        transaction = self.account.transactions[1]
        self.assertEqual(transaction['type'], 'deposit')
        self.assertEqual(transaction['amount'], 500.0)
    
    def test_deposit_funds_zero(self):
        """Test depositing zero amount raises ValueError."""
        with self.assertRaises(ValueError):
            self.account.deposit_funds(0)
    
    def test_deposit_funds_negative(self):
        """Test depositing negative amount raises ValueError."""
        with self.assertRaises(ValueError):
            self.account.deposit_funds(-100)
    
    def test_withdraw_funds_success(self):
        """Test successful withdrawal."""
        initial_balance = self.account.balance
        result = self.account.withdraw_funds(300.0)
        
        self.assertTrue(result)
        self.assertEqual(self.account.balance, initial_balance - 300.0)
        self.assertEqual(len(self.account.transactions), 2)
        
        transaction = self.account.transactions[1]
        self.assertEqual(transaction['type'], 'withdraw')
        self.assertEqual(transaction['amount'], 300.0)
    
    def test_withdraw_funds_insufficient_funds(self):
        """Test withdrawal with insufficient funds."""
        result = self.account.withdraw_funds(1500.0)
        
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 1000.0)  # Balance unchanged
        self.assertEqual(len(self.account.transactions), 1)  # No new transaction
    
    def test_withdraw_funds_zero(self):
        """Test withdrawing zero amount raises ValueError."""
        with self.assertRaises(ValueError):
            self.account.withdraw_funds(0)
    
    def test_withdraw_funds_negative(self):
        """Test withdrawing negative amount raises ValueError."""
        with self.assertRaises(ValueError):
            self.account.withdraw_funds(-100)
    
    @patch('accounts.get_share_price')
    def test_buy_shares_success(self, mock_get_price):
        """Test successful share purchase."""
        mock_get_price.return_value = 150.0  # AAPL price
        initial_balance = self.account.balance
        
        result = self.account.buy_shares('AAPL', 2)
        
        self.assertTrue(result)
        self.assertEqual(self.account.balance, initial_balance - 300.0)  # 2 * 150
        self.assertEqual(self.account.holdings['AAPL'], 2)
        self.assertEqual(len(self.account.transactions), 2)
        
        transaction = self.account.transactions[1]
        self.assertEqual(transaction['type'], 'buy')
        self.assertEqual(transaction['amount'], 300.0)
    
    @patch('accounts.get_share_price')
    def test_buy_shares_insufficient_funds(self, mock_get_price):
        """Test share purchase with insufficient funds."""
        mock_get_price.return_value = 150.0
        
        result = self.account.buy_shares('AAPL', 10)  # Would cost 1500, but only 1000 available
        
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 1000.0)  # Balance unchanged
        self.assertEqual(self.account.holdings, {})  # No holdings added
        self.assertEqual(len(self.account.transactions), 1)  # No new transaction
    
    @patch('accounts.get_share_price')
    def test_buy_shares_zero_quantity(self, mock_get_price):
        """Test buying zero shares raises ValueError."""
        mock_get_price.return_value = 150.0
        
        with self.assertRaises(ValueError):
            self.account.buy_shares('AAPL', 0)
    
    @patch('accounts.get_share_price')
    def test_buy_shares_negative_quantity(self, mock_get_price):
        """Test buying negative shares raises ValueError."""
        mock_get_price.return_value = 150.0
        
        with self.assertRaises(ValueError):
            self.account.buy_shares('AAPL', -5)
    
    @patch('accounts.get_share_price')
    def test_sell_shares_success(self, mock_get_price):
        """Test successful share sale."""
        mock_get_price.return_value = 150.0
        
        # First buy some shares
        self.account.buy_shares('AAPL', 4)
        initial_balance = self.account.balance
        
        # Then sell some
        result = self.account.sell_shares('AAPL', 2)
        
        self.assertTrue(result)
        self.assertEqual(self.account.balance, initial_balance + 300.0)  # 2 * 150
        self.assertEqual(self.account.holdings['AAPL'], 2)  # 4 - 2 = 2 remaining
        
        # Check transaction
        transaction = self.account.transactions[2]
        self.assertEqual(transaction['type'], 'sell')
        self.assertEqual(transaction['amount'], 300.0)
    
    @patch('accounts.get_share_price')
    def test_sell_shares_insufficient_holdings(self, mock_get_price):
        """Test selling more shares than owned."""
        mock_get_price.return_value = 150.0
        
        # Buy some shares
        self.account.buy_shares('AAPL', 2)
        initial_balance = self.account.balance
        
        # Try to sell more than owned
        result = self.account.sell_shares('AAPL', 5)
        
        self.assertFalse(result)
        self.assertEqual(self.account.balance, initial_balance)  # Balance unchanged
        self.assertEqual(self.account.holdings['AAPL'], 2)  # Holdings unchanged
    
    @patch('accounts.get_share_price')
    def test_sell_shares_zero_quantity(self, mock_get_price):
        """Test selling zero shares raises ValueError."""
        mock_get_price.return_value = 150.0
        
        with self.assertRaises(ValueError):
            self.account.sell_shares('AAPL', 0)
    
    @patch('accounts.get_share_price')
    def test_sell_shares_negative_quantity(self, mock_get_price):
        """Test selling negative shares raises ValueError."""
        mock_get_price.return_value = 150.0
        
        with self.assertRaises(ValueError):
            self.account.sell_shares('AAPL', -3)
    
    @patch('accounts.get_share_price')
    def test_sell_shares_nonexistent_symbol(self, mock_get_price):
        """Test selling shares of a symbol not in holdings."""
        mock_get_price.return_value = 150.0
        
        result = self.account.sell_shares('MSFT', 2)
        
        self.assertFalse(result)
    
    @patch('accounts.get_share_price')
    def test_calculate_portfolio_value(self, mock_get_price):
        """Test portfolio value calculation."""
        mock_get_price.return_value = 150.0
        
        # Buy some shares
        self.account.buy_shares('AAPL', 4)
        
        # Portfolio value should be balance + (shares * price)
        expected_value = self.account.balance + (4 * 150.0)
        portfolio_value = self.account.calculate_portfolio_value()
        
        self.assertEqual(portfolio_value, expected_value)
    
    @patch('accounts.get_share_price')
    def test_calculate_profit_loss(self, mock_get_price):
        """Test profit/loss calculation."""
        mock_get_price.return_value = 150.0
        
        # Buy some shares
        self.account.buy_shares('AAPL', 4)
        
        current_portfolio_value = self.account.calculate_portfolio_value()
        expected_profit_loss = current_portfolio_value - self.account.initial_deposit
        
        profit_loss = self.account.calculate_profit_loss()
        
        self.assertEqual(profit_loss, expected_profit_loss)
    
    def test_get_holdings(self):
        """Test getting holdings copy."""
        # Holdings should start empty
        holdings = self.account.get_holdings()
        self.assertEqual(holdings, {})
        
        # Modify the copy shouldn't affect original
        holdings['TEST'] = 100
        self.assertEqual(self.account.holdings, {})
    
    def test_get_transaction_history(self):
        """Test getting transaction history copy."""
        transactions = self.account.get_transaction_history()
        self.assertEqual(len(transactions), 1)
        
        # Modify the copy shouldn't affect original
        transactions.append('fake_transaction')
        self.assertEqual(len(self.account.transactions), 1)
    
    @patch('accounts.get_share_price')
    def test_get_profit_loss_report(self, mock_get_price):
        """Test profit/loss report."""
        mock_get_price.return_value = 150.0
        
        # Buy some shares
        self.account.buy_shares('AAPL', 4)
        
        profit_loss = self.account.get_profit_loss_report()
        calculated_profit_loss = self.account.calculate_profit_loss()
        
        self.assertEqual(profit_loss, calculated_profit_loss)

class TestGetSharePrice(unittest.TestCase):
    
    def test_get_share_price_existing_symbol(self):
        """Test getting price for existing symbols."""
        self.assertEqual(accounts.get_share_price('AAPL'), 150.00)
        self.assertEqual(accounts.get_share_price('TSLA'), 650.00)
        self.assertEqual(accounts.get_share_price('GOOGL'), 2800.00)
        
        # Test case insensitivity
        self.assertEqual(accounts.get_share_price('aapl'), 150.00)
        self.assertEqual(accounts.get_share_price('TsLa'), 650.00)
    
    def test_get_share_price_nonexistent_symbol(self):
        """Test getting price for non-existent symbol."""
        self.assertEqual(accounts.get_share_price('MSFT'), 0.0)
        self.assertEqual(accounts.get_share_price('INVALID'), 0.0)

if __name__ == '__main__':
    unittest.main()
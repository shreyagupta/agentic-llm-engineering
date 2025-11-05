import gradio as gr
from accounts import Account, get_share_price

# Global account instance
account = None

def create_account(account_id, initial_deposit):
    global account
    try:
        initial_deposit = float(initial_deposit)
        if initial_deposit <= 0:
            return "Error: Initial deposit must be positive", "", "", "", ""
        
        account = Account(account_id, initial_deposit)
        return f"Account created successfully! ID: {account_id}, Initial deposit: ${initial_deposit:.2f}", get_balance(), get_holdings(), get_portfolio_value(), get_profit_loss()
    except Exception as e:
        return f"Error creating account: {str(e)}", "", "", "", ""

def deposit_funds(amount):
    global account
    if account is None:
        return "Please create an account first", get_balance(), get_holdings(), get_portfolio_value(), get_profit_loss()
    
    try:
        amount = float(amount)
        account.deposit_funds(amount)
        return f"Deposited ${amount:.2f} successfully", get_balance(), get_holdings(), get_portfolio_value(), get_profit_loss()
    except Exception as e:
        return f"Error: {str(e)}", get_balance(), get_holdings(), get_portfolio_value(), get_profit_loss()

def withdraw_funds(amount):
    global account
    if account is None:
        return "Please create an account first", get_balance(), get_holdings(), get_portfolio_value(), get_profit_loss()
    
    try:
        amount = float(amount)
        success = account.withdraw_funds(amount)
        if success:
            return f"Withdrew ${amount:.2f} successfully", get_balance(), get_holdings(), get_portfolio_value(), get_profit_loss()
        else:
            return "Error: Insufficient funds for withdrawal", get_balance(), get_holdings(), get_portfolio_value(), get_profit_loss()
    except Exception as e:
        return f"Error: {str(e)}", get_balance(), get_holdings(), get_portfolio_value(), get_profit_loss()

def buy_shares(symbol, quantity):
    global account
    if account is None:
        return "Please create an account first", get_balance(), get_holdings(), get_portfolio_value(), get_profit_loss()
    
    try:
        quantity = int(quantity)
        success = account.buy_shares(symbol, quantity)
        if success:
            return f"Bought {quantity} shares of {symbol} successfully", get_balance(), get_holdings(), get_portfolio_value(), get_profit_loss()
        else:
            return "Error: Insufficient funds to buy shares", get_balance(), get_holdings(), get_portfolio_value(), get_profit_loss()
    except Exception as e:
        return f"Error: {str(e)}", get_balance(), get_holdings(), get_portfolio_value(), get_profit_loss()

def sell_shares(symbol, quantity):
    global account
    if account is None:
        return "Please create an account first", get_balance(), get_holdings(), get_portfolio_value(), get_profit_loss()
    
    try:
        quantity = int(quantity)
        success = account.sell_shares(symbol, quantity)
        if success:
            return f"Sold {quantity} shares of {symbol} successfully", get_balance(), get_holdings(), get_portfolio_value(), get_profit_loss()
        else:
            return "Error: Insufficient shares to sell", get_balance(), get_holdings(), get_portfolio_value(), get_profit_loss()
    except Exception as e:
        return f"Error: {str(e)}", get_balance(), get_holdings(), get_portfolio_value(), get_profit_loss()

def get_balance():
    if account is None:
        return "No account created"
    return f"${account.balance:.2f}"

def get_holdings():
    if account is None:
        return "No account created"
    holdings = account.get_holdings()
    if not holdings:
        return "No holdings"
    return "\n".join([f"{symbol}: {quantity} shares" for symbol, quantity in holdings.items()])

def get_portfolio_value():
    if account is None:
        return "No account created"
    return f"${account.calculate_portfolio_value():.2f}"

def get_profit_loss():
    if account is None:
        return "No account created"
    pl = account.calculate_profit_loss()
    return f"${pl:.2f} ({'Profit' if pl >= 0 else 'Loss'})"

def get_transactions():
    if account is None:
        return "No account created"
    transactions = account.get_transaction_history()
    if not transactions:
        return "No transactions"
    
    transaction_list = []
    for t in transactions:
        transaction_list.append(f"{t['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - {t['description']} - Balance: ${t['balance_after']:.2f}")
    
    return "\n".join(transaction_list)

def get_available_symbols():
    return "AAPL, TSLA, GOOGL"

with gr.Blocks(title="Trading Account Demo") as demo:
    gr.Markdown("# Trading Account Management System")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("## Account Setup")
            account_id = gr.Textbox(label="Account ID", placeholder="Enter account ID")
            initial_deposit = gr.Textbox(label="Initial Deposit ($)", placeholder="Enter initial deposit amount")
            create_btn = gr.Button("Create Account")
            
            gr.Markdown("## Fund Management")
            deposit_amount = gr.Textbox(label="Deposit Amount ($)", placeholder="Enter deposit amount")
            deposit_btn = gr.Button("Deposit Funds")
            withdraw_amount = gr.Textbox(label="Withdraw Amount ($)", placeholder="Enter withdrawal amount")
            withdraw_btn = gr.Button("Withdraw Funds")
            
            gr.Markdown("## Stock Trading")
            symbol = gr.Textbox(label="Stock Symbol", placeholder="AAPL, TSLA, GOOGL")
            quantity = gr.Textbox(label="Quantity", placeholder="Enter number of shares")
            with gr.Row():
                buy_btn = gr.Button("Buy Shares")
                sell_btn = gr.Button("Sell Shares")
            
            gr.Markdown("## Available Symbols")
            available_symbols = gr.Textbox(value=get_available_symbols(), interactive=False)
        
        with gr.Column():
            gr.Markdown("## Account Information")
            result_output = gr.Textbox(label="Operation Result", interactive=False)
            current_balance = gr.Textbox(label="Current Balance", interactive=False)
            portfolio_value = gr.Textbox(label="Portfolio Value", interactive=False)
            profit_loss = gr.Textbox(label="Profit/Loss", interactive=False)
            
            gr.Markdown("## Current Holdings")
            holdings_output = gr.Textbox(label="Holdings", interactive=False, lines=5)
            
            gr.Markdown("## Transaction History")
            transactions_output = gr.Textbox(label="Transactions", interactive=False, lines=10)
    
    # Event handlers
    create_btn.click(
        create_account,
        inputs=[account_id, initial_deposit],
        outputs=[result_output, current_balance, holdings_output, portfolio_value, profit_loss]
    )
    
    deposit_btn.click(
        deposit_funds,
        inputs=[deposit_amount],
        outputs=[result_output, current_balance, holdings_output, portfolio_value, profit_loss]
    )
    
    withdraw_btn.click(
        withdraw_funds,
        inputs=[withdraw_amount],
        outputs=[result_output, current_balance, holdings_output, portfolio_value, profit_loss]
    )
    
    buy_btn.click(
        buy_shares,
        inputs=[symbol, quantity],
        outputs=[result_output, current_balance, holdings_output, portfolio_value, profit_loss]
    )
    
    sell_btn.click(
        sell_shares,
        inputs=[symbol, quantity],
        outputs=[result_output, current_balance, holdings_output, portfolio_value, profit_loss]
    )
    
    # Add a refresh button for transactions
    refresh_btn = gr.Button("Refresh Transactions")
    refresh_btn.click(
        lambda: get_transactions(),
        outputs=[transactions_output]
    )

if __name__ == "__main__":
    demo.launch()
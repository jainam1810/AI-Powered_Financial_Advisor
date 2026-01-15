"""
Custom CSS styling for the Finance AI app
This makes everything look beautiful!
"""


def get_custom_css():
    """
    Returns custom CSS to make the app look modern and professional
    Think of CSS as makeup for websites - makes everything pretty!
    """
    return """
    <style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main container */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Balance Card - The big purple card */
    .balance-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .balance-amount {
        font-size: 3.5rem;
        font-weight: 700;
        margin: 1rem 0;
    }
    
    .balance-label {
        font-size: 1rem;
        opacity: 0.9;
        font-weight: 500;
    }
    
    .balance-subtitle {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        padding: 0.5rem 1.5rem;
        border-radius: 10px;
        margin-top: 1rem;
        font-size: 1.1rem;
    }
    
    /* Alert Cards */
    .alert-card {
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 4px solid;
    }
    
    .alert-success {
        background: #f0fdf4;
        border-color: #22c55e;
    }
    
    .alert-warning {
        background: #fefce8;
        border-color: #eab308;
    }
    
    .alert-danger {
        background: #fef2f2;
        border-color: #ef4444;
    }
    
    .alert-info {
        background: #eff6ff;
        border-color: #3b82f6;
    }
    
    .alert-icon {
        font-size: 2rem;
        margin-right: 1rem;
    }
    
    .alert-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #1f2937;
    }
    
    .alert-text {
        font-size: 1rem;
        color: #4b5563;
        line-height: 1.6;
    }
    
    /* Insight Cards */
    .insight-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        margin: 1rem 0;
        border: 1px solid #f3f4f6;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .insight-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    }
    
    /* Transaction Items */
    .transaction-item {
        display: flex;
        align-items: center;
        padding: 1rem;
        background: white;
        border-radius: 12px;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .transaction-icon {
        width: 45px;
        height: 45px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        margin-right: 1rem;
    }
    
    /* Category Colors */
    .cat-groceries { background: #fef3c7; }
    .cat-transport { background: #dbeafe; }
    .cat-subscriptions { background: #fce7f3; }
    .cat-eating-out { background: #fed7aa; }
    .cat-bills { background: #e0e7ff; }
    .cat-shopping { background: #fecaca; }
    .cat-income { background: #d1fae5; }
    
    /* Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.2);
        padding: 1.5rem;
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-bottom: 0.5rem;
    }
    
    /* Buttons */
    .custom-button {
        background: #22c55e;
        color: white;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .custom-button:hover {
        background: #16a34a;
        transform: translateY(-1px);
    }
    
    /* Progress Bars */
    .progress-bar {
        background: #e5e7eb;
        height: 10px;
        border-radius: 10px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0 2rem;
        background-color: transparent;
        border-radius: 10px 10px 0 0;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
    
    /* Prediction Cards */
    .prediction-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    .prediction-title {
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    .prediction-date {
        color: #64748b;
        font-size: 0.9rem;
    }
    
    .prediction-amount {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    /* Subscription List */
    .subscription-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        background: white;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 1px solid #f1f5f9;
    }
    
    .subscription-name {
        font-weight: 600;
        font-size: 1rem;
    }
    
    .subscription-price {
        color: #64748b;
        font-size: 0.95rem;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .balance-amount {
            font-size: 2.5rem;
        }
        .metric-value {
            font-size: 1.5rem;
        }
    }
    </style>
    """


def get_category_icon(category):
    """
    Returns an emoji icon for each category
    Makes the UI more visual and friendly!
    """
    icons = {
        'Groceries': '🛒',
        'Transport': '🚇',
        'Subscriptions': '🎵',
        'Eating Out': '🍽️',
        'Bills': '💡',
        'Shopping': '🛍️',
        'Income': '💼'
    }
    return icons.get(category, '💰')


def get_category_color(category):
    """
    Returns a color class for each category
    """
    colors = {
        'Groceries': 'cat-groceries',
        'Transport': 'cat-transport',
        'Subscriptions': 'cat-subscriptions',
        'Eating Out': 'cat-eating-out',
        'Bills': 'cat-bills',
        'Shopping': 'cat-shopping',
        'Income': 'cat-income'
    }
    return colors.get(category, 'cat-groceries')


def format_currency(amount):
    """
    Format numbers as currency (£1,234.56)
    """
    return f"£{abs(amount):,.2f}"

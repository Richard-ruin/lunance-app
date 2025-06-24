import locale
from typing import Union, Optional
from decimal import Decimal, ROUND_HALF_UP
import re


class IndonesianCurrencyFormatter:
    """Indonesian Rupiah currency formatter with localization support"""
    
    def __init__(self):
        self.currency_symbol = "Rp"
        self.thousand_separator = "."
        self.decimal_separator = ","
        
    def format_currency(
        self, 
        amount: Union[int, float, Decimal], 
        include_symbol: bool = True,
        include_decimals: bool = False,
        compact: bool = False
    ) -> str:
        """
        Format amount as Indonesian Rupiah currency
        
        Args:
            amount: The amount to format
            include_symbol: Whether to include 'Rp' symbol
            include_decimals: Whether to show decimal places
            compact: Whether to use compact format (K, M, B)
            
        Returns:
            Formatted currency string
        """
        try:
            # Handle None or invalid values
            if amount is None:
                return "Rp 0" if include_symbol else "0"
            
            # Convert to Decimal for precise calculations
            if isinstance(amount, str):
                amount = float(amount.replace(",", "."))
            amount = Decimal(str(amount))
            
            # Round to appropriate decimal places
            if include_decimals:
                amount = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            else:
                amount = amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            
            # Handle compact format
            if compact:
                return self._format_compact(amount, include_symbol)
            
            # Convert to string and handle negative numbers
            is_negative = amount < 0
            amount_str = str(abs(amount))
            
            # Split integer and decimal parts
            if '.' in amount_str:
                integer_part, decimal_part = amount_str.split('.')
            else:
                integer_part = amount_str
                decimal_part = "00" if include_decimals else ""
            
            # Add thousand separators
            formatted_integer = self._add_thousand_separators(integer_part)
            
            # Combine parts
            if include_decimals and decimal_part:
                # Ensure 2 decimal places
                decimal_part = decimal_part.ljust(2, '0')[:2]
                formatted_amount = f"{formatted_integer}{self.decimal_separator}{decimal_part}"
            else:
                formatted_amount = formatted_integer
            
            # Add currency symbol and handle negative
            if include_symbol:
                if is_negative:
                    return f"-{self.currency_symbol} {formatted_amount}"
                else:
                    return f"{self.currency_symbol} {formatted_amount}"
            else:
                if is_negative:
                    return f"-{formatted_amount}"
                else:
                    return formatted_amount
                    
        except Exception as e:
            # Fallback formatting
            return f"{self.currency_symbol} {amount}" if include_symbol else str(amount)
    
    def _add_thousand_separators(self, integer_str: str) -> str:
        """Add thousand separators to integer string"""
        # Reverse the string to add separators from right to left
        reversed_str = integer_str[::-1]
        
        # Add separators every 3 digits
        groups = []
        for i in range(0, len(reversed_str), 3):
            groups.append(reversed_str[i:i+3])
        
        # Join groups with separator and reverse back
        return self.thousand_separator.join(groups)[::-1]
    
    def _format_compact(self, amount: Decimal, include_symbol: bool) -> str:
        """Format amount in compact notation (K, M, B)"""
        abs_amount = abs(amount)
        is_negative = amount < 0
        
        if abs_amount >= 1_000_000_000:  # Billions
            formatted = f"{abs_amount / 1_000_000_000:.1f}B"
        elif abs_amount >= 1_000_000:  # Millions
            formatted = f"{abs_amount / 1_000_000:.1f}M"
        elif abs_amount >= 1_000:  # Thousands
            formatted = f"{abs_amount / 1_000:.1f}K"
        else:
            formatted = str(int(abs_amount))
        
        # Remove unnecessary .0
        formatted = formatted.replace('.0K', 'K').replace('.0M', 'M').replace('.0B', 'B')
        
        # Add negative sign
        if is_negative:
            formatted = f"-{formatted}"
        
        # Add currency symbol
        if include_symbol:
            return f"{self.currency_symbol} {formatted}"
        else:
            return formatted
    
    def parse_currency(self, currency_str: str) -> float:
        """
        Parse Indonesian currency string back to float
        
        Args:
            currency_str: Currency string like "Rp 1.500.000,50"
            
        Returns:
            Float value
        """
        try:
            # Remove currency symbol and whitespace
            cleaned = currency_str.replace(self.currency_symbol, "").strip()
            
            # Handle negative numbers
            is_negative = cleaned.startswith('-')
            if is_negative:
                cleaned = cleaned[1:].strip()
            
            # Handle compact notation
            if cleaned.endswith(('K', 'M', 'B')):
                return self._parse_compact(cleaned, is_negative)
            
            # Replace Indonesian separators with standard format
            # First replace decimal separator with temporary marker
            if self.decimal_separator in cleaned:
                parts = cleaned.split(self.decimal_separator)
                if len(parts) == 2:
                    integer_part = parts[0].replace(self.thousand_separator, "")
                    decimal_part = parts[1]
                    result = float(f"{integer_part}.{decimal_part}")
                else:
                    # Multiple decimal separators, treat as thousand separators
                    result = float(cleaned.replace(self.thousand_separator, "").replace(self.decimal_separator, ""))
            else:
                # No decimal separator, just remove thousand separators
                result = float(cleaned.replace(self.thousand_separator, ""))
            
            return -result if is_negative else result
            
        except Exception:
            # Fallback: try to extract numbers only
            numbers_only = re.sub(r'[^\d,.-]', '', currency_str)
            try:
                return float(numbers_only.replace(',', '.'))
            except:
                return 0.0
    
    def _parse_compact(self, compact_str: str, is_negative: bool) -> float:
        """Parse compact notation back to float"""
        try:
            if compact_str.endswith('K'):
                multiplier = 1_000
                number_str = compact_str[:-1]
            elif compact_str.endswith('M'):
                multiplier = 1_000_000
                number_str = compact_str[:-1]
            elif compact_str.endswith('B'):
                multiplier = 1_000_000_000
                number_str = compact_str[:-1]
            else:
                return float(compact_str) * (-1 if is_negative else 1)
            
            number = float(number_str.replace(',', '.'))
            result = number * multiplier
            
            return -result if is_negative else result
            
        except Exception:
            return 0.0
    
    def format_percentage(self, value: float, decimal_places: int = 1) -> str:
        """Format percentage with Indonesian locale"""
        try:
            formatted = f"{value:.{decimal_places}f}%"
            # Replace decimal point with comma for Indonesian locale
            return formatted.replace('.', self.decimal_separator)
        except Exception:
            return f"{value}%"
    
    def format_number(self, number: Union[int, float], decimal_places: int = 0) -> str:
        """Format number with Indonesian thousand separators"""
        try:
            if decimal_places > 0:
                formatted = f"{number:.{decimal_places}f}"
                # Split integer and decimal parts
                if '.' in formatted:
                    integer_part, decimal_part = formatted.split('.')
                    integer_with_separators = self._add_thousand_separators(integer_part)
                    return f"{integer_with_separators}{self.decimal_separator}{decimal_part}"
                else:
                    return self._add_thousand_separators(formatted)
            else:
                integer_str = str(int(number))
                return self._add_thousand_separators(integer_str)
                
        except Exception:
            return str(number)


# Global formatter instance
formatter = IndonesianCurrencyFormatter()

# Convenience functions
def format_idr(
    amount: Union[int, float, Decimal], 
    include_symbol: bool = True,
    include_decimals: bool = False,
    compact: bool = False
) -> str:
    """Format amount as Indonesian Rupiah"""
    return formatter.format_currency(amount, include_symbol, include_decimals, compact)

def format_idr_compact(amount: Union[int, float, Decimal]) -> str:
    """Format amount in compact notation (e.g., Rp 1.5M)"""
    return formatter.format_currency(amount, compact=True)

def format_idr_no_symbol(amount: Union[int, float, Decimal]) -> str:
    """Format amount without currency symbol"""
    return formatter.format_currency(amount, include_symbol=False)

def parse_idr(currency_str: str) -> float:
    """Parse Indonesian currency string to float"""
    return formatter.parse_currency(currency_str)

def format_percentage_id(value: float, decimal_places: int = 1) -> str:
    """Format percentage with Indonesian locale"""
    return formatter.format_percentage(value, decimal_places)

def format_number_id(number: Union[int, float], decimal_places: int = 0) -> str:
    """Format number with Indonesian thousand separators"""
    return formatter.format_number(number, decimal_places)

# Currency conversion utilities (for future use)
def convert_currency(amount: float, from_currency: str, to_currency: str, exchange_rate: float) -> float:
    """Convert between currencies using exchange rate"""
    if from_currency == to_currency:
        return amount
    
    if from_currency == "IDR" and to_currency == "USD":
        return amount / exchange_rate
    elif from_currency == "USD" and to_currency == "IDR":
        return amount * exchange_rate
    else:
        # For other currencies, implement as needed
        return amount

# Budget formatting utilities
def format_budget_summary(budget: dict, spent: dict) -> dict:
    """Format budget vs spent summary"""
    summary = {}
    
    for category in budget.keys():
        budget_amount = budget.get(category, 0)
        spent_amount = spent.get(category, 0)
        remaining = budget_amount - spent_amount
        percentage_used = (spent_amount / budget_amount * 100) if budget_amount > 0 else 0
        
        summary[category] = {
            "budget": format_idr(budget_amount),
            "spent": format_idr(spent_amount),
            "remaining": format_idr(remaining),
            "percentage_used": format_percentage_id(percentage_used),
            "status": "over_budget" if spent_amount > budget_amount else "on_track"
        }
    
    return summary

# Expense categorization helpers
def categorize_expense_by_amount(amount: float) -> str:
    """Categorize expense by amount level"""
    if amount < 10_000:  # Under 10K IDR
        return "small"
    elif amount < 50_000:  # Under 50K IDR
        return "medium"
    elif amount < 200_000:  # Under 200K IDR
        return "large"
    else:
        return "very_large"

def get_spending_level_description(amount: float) -> str:
    """Get spending level description in Indonesian"""
    level = categorize_expense_by_amount(amount)
    
    descriptions = {
        "small": "Pengeluaran kecil",
        "medium": "Pengeluaran sedang", 
        "large": "Pengeluaran besar",
        "very_large": "Pengeluaran sangat besar"
    }
    
    return descriptions.get(level, "Pengeluaran")

# Student-specific formatting
def format_allowance_breakdown(monthly_allowance: float, days_in_month: int = 30) -> dict:
    """Format monthly allowance breakdown for students"""
    daily_budget = monthly_allowance / days_in_month
    weekly_budget = daily_budget * 7
    
    return {
        "monthly": format_idr(monthly_allowance),
        "weekly": format_idr(weekly_budget), 
        "daily": format_idr(daily_budget),
        "per_meal": format_idr(daily_budget / 3),  # Assuming 3 meals per day
        "weekend_budget": format_idr(daily_budget * 2)  # Weekend budget
    }
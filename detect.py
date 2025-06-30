def detect_fraud(buyer_id, seller_id, amount, payment_method):
    """
    Placeholder function to simulate fraud detection.
    In a real project, this would use a trained ML model or advanced rules.
    """
    # Simple rule-based detection
    if amount > 1000:  # High amount
        return "Fraudulent"
    if buyer_id == seller_id:  # Same buyer and seller
        return "Fraudulent"
    if payment_method.lower() == "cryptocurrency":  # Risky payment method
        return "Fraudulent"
    return "Legitimate"
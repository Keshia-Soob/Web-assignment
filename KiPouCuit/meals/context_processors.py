def cart_context(request):
    cart = request.session.get('cart', {})
    cart_count = sum(item['quantity'] for item in cart.values())
    subtotal = sum(item['quantity'] * item['price'] for item in cart.values())
    return {'cart': cart, 'cart_count': cart_count, 'cart_subtotal': subtotal}

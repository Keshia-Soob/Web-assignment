# orders/forms.py

from django import forms

class NewCardForm(forms.Form):
    # Make all fields NOT required by default
    card_holder_name = forms.CharField(
        max_length=150, 
        label="Name on card",
        required=False 
    )
    card_number = forms.CharField(
        max_length=32, 
        label="Card number",
        required=False  
    )
    expiry_month = forms.IntegerField(
        min_value=1, 
        max_value=12,
        required=False 
    )
    expiry_year = forms.IntegerField(
        min_value=2023, 
        max_value=2100,
        required=False 
    )
    save_card = forms.BooleanField(
        required=False, 
        initial=True, 
        label="Save card for next time"
    )
    set_default = forms.BooleanField(
        required=False, 
        initial=False, 
        label="Set as default"
    )

    def clean(self):
        """
        Custom validation: If any new card field is filled, 
        then ALL card fields must be filled.
        """
        cleaned_data = super().clean()
        
        card_holder = cleaned_data.get('card_holder_name')
        card_number = cleaned_data.get('card_number')
        exp_month = cleaned_data.get('expiry_month')
        exp_year = cleaned_data.get('expiry_year')
        
        # Check if user is trying to enter a new card
        any_card_field_filled = any([card_holder, card_number, exp_month, exp_year])
        
        if any_card_field_filled:
            # If they started filling new card, all fields must be complete
            if not card_holder:
                self.add_error('card_holder_name', 'Please enter the name on card')
            if not card_number:
                self.add_error('card_number', 'Please enter the card number')
            if not exp_month:
                self.add_error('expiry_month', 'Please enter expiry month')
            if not exp_year:
                self.add_error('expiry_year', 'Please enter expiry year')
        
        return cleaned_data


class CheckoutForm(forms.Form):
    payment_method_id = forms.IntegerField(required=False)
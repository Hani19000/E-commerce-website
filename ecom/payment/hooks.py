# from paypal.standard.models import ST_PP_COMPLETED
# from paypal.standard.ipn.signals import valid_ipn_received
# from django.dispatch import receiver
# from django.conf import settings

# @receiver(valid_ipn_received)
# def payment_notification(sender, **kwargs):
#     #grab the info that paypal sendss
#     paypal_obj = sender
#     print(paypal_obj)
#     print(f'Amount Paid: {paypal_obj.mc_gross}')
    
    # if ipn.payment_status == ST_PP_COMPLETED:
    #     # Payment was successful
    #     order_id = ipn.invoice  # Assuming 'invoice' contains the order ID
    #     try:
    #         order = Order.objects.get(id=order_id)
    #         order.status = 'Paid'
    #         order.save()
    #     except Order.DoesNotExist:
    #         pass  # Handle the case where the order does not exist
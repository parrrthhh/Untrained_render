import argparse
# Assuming the main functions are correctly imported
from find_transaction_number import number_main as find_transaction_number
from find_transaction_dates import date_main as find_transaction_dates
from find_transaction_total import total_main as find_transaction_total
from find_gst_details import gst_main
from Sharepoint_Integration import Untrained
def main(pdf_name):
    invoice_number = '-'
    purchase_order_number = '-'
    order_number ='-' 
    bill_number = '-'
    due_date = '-'
    delivery_date = '-'
    invoice_date ='-'
    total = '-'

    verbose=True    
    print(f"Processing {pdf_name} \n")

    try:
        transaction_number_result = find_transaction_number(pdf_name)

        if "invoice_number" in transaction_number_result:
                invoice_number = transaction_number_result["invoice_number"]
        
        if "order_number" in transaction_number_result:
              purchase_order_number = transaction_number_result["order_number"]
              

        if "purchase_order_number" in transaction_number_result:
                purchase_order_number = transaction_number_result["purchase_order_number"]


        if "bill_number" in transaction_number_result:
                bill_number = transaction_number_result["bill_number"]
        
        print(invoice_number)
        print(purchase_order_number)
        print(bill_number)
    except Exception as e:
            print(f"Error processing {pdf_name} at transaction number function: {e}")

    try:
            transaction_dates_result = find_transaction_dates(pdf_name)
            date_keywords = ["invoice_date", "receipt_date","purchase_order_date", "bill_date", "order_date", "due_date", "delivery_date","date"]

            for keyword in date_keywords:
                if keyword in transaction_dates_result:
                    if keyword == "due_date":
                        due_date = transaction_dates_result[keyword]
                    elif keyword == "delivery_date":
                        delivery_date = transaction_dates_result[keyword]
                    else:
                        invoice_date = transaction_dates_result[keyword]
            

            print(invoice_date)
            print(due_date)
            print(delivery_date)
    except Exception as e:
            print(f"Error processing {pdf_name} at transaction dates function: {e}")

    try:
            transaction_total_result = find_transaction_total(pdf_name)
            print(transaction_total_result)
            if "total" in transaction_total_result:
                total = transaction_total_result["total"]    
    except Exception as e:
            print(f"Error processing {pdf_name} at transaction total function: {e}")
        
    print('\n')


    try:
        gst1,gst1_name, gst1_addr,gst2,gst2_name, gst2_addr = gst_main(pdf_name)
        
        #print(gst1,gst1_name, gst1_addr,gst2,gst2_name, gst2_addr)
    except Exception as e:
        print(e)

    Untrained(pdf_name,invoice_number,invoice_date,total,gst1,gst1_name, gst1_addr,gst2,gst2_name, gst2_addr,purchase_order_number,bill_number,due_date,delivery_date)
#main("D:\Advait Invoice code\PO1.pdf")

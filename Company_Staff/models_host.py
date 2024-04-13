class debitnote(models.Model):
    company = models.ForeignKey(CompanyDetails, on_delete=models.CASCADE,null=True)
    login_details = models.ForeignKey(LoginDetails, on_delete=models.CASCADE,null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,null=True)
    bills = models.ForeignKey(Bill, on_delete=models.CASCADE,null=True)

    
    profile_name = models.CharField(max_length=100, null=True, blank=True)

    vendor_email = models.EmailField(max_length=100, null=True, blank=True)
    billing_address = models.TextField(null=True, blank=True)
    gst_type = models.CharField(max_length=100, null=True, blank=True)
    gstin = models.CharField(max_length=100, null=True, blank=True)
    place_of_supply = models.CharField(max_length=100, null=True, blank=True)
    bill_type = models.CharField(max_length=20, null=True, blank=True)
    reference_no = models.BigIntegerField(null=True, blank=True)
    bill_no = models.CharField(max_length=100)
    debitnote_date = models.DateField(null=True, blank=True)
    debitnote_no = models.CharField(max_length=100, null=True, blank=True)
    
    price_list_applied = models.BooleanField(null=True, default=False)
    price_list = models.ForeignKey(PriceList, on_delete = models.SET_NULL,null=True)
    payment_method = models.CharField(max_length=20, null=True,blank=True)
    cheque_number = models.CharField(max_length=100, null=True, blank=True)
    upi_number = models.CharField(max_length=100, null=True, blank=True)
    bank_account_number = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    terms_and_conditions = models.TextField(null=True, blank=True)
    document=models.FileField(upload_to="images/",null=True)
    subtotal = models.IntegerField(default=0, null=True)
    igst = models.FloatField(default=0.0, null=True, blank=True)
    cgst = models.FloatField(default=0.0, null=True, blank=True)
    sgst = models.FloatField(default=0.0, null=True, blank=True)
    tax_amount = models.FloatField(default=0.0, null=True, blank=True)
    adjustment = models.FloatField(default=0.0, null=True, blank=True)
    shipping_charge = models.FloatField(default=0.0, null=True, blank=True)
    grandtotal = models.FloatField(default=0.0, null=True, blank=True)
    advance_paid = models.FloatField(default=0.0, null=True, blank=True)
    balance = models.FloatField(default=0.0, null=True, blank=True)
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Saved', 'Saved'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
class debitnote_History(models.Model):
    company = models.ForeignKey(CompanyDetails, on_delete=models.CASCADE)
    login_details = models.ForeignKey(LoginDetails, on_delete=models.CASCADE)
    debit_note = models.ForeignKey(debitnote, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    
    action = models.CharField(max_length=20, null=True)


class debitnote_item(models.Model):
    login_details = models.ForeignKey(LoginDetails, on_delete=models.CASCADE,null=True,blank=True)
    company=models.ForeignKey(CompanyDetails,on_delete=models.CASCADE,null=True,blank=True)
    debit_note=models.ForeignKey(debitnote,on_delete=models.CASCADE,null=True,blank=True)
    
    item=models.ForeignKey(Items, on_delete=models.CASCADE,null=True,blank=True)
    hsn = models.CharField(max_length=200,null=True)
    quantity = models.IntegerField(null=True)
    price=  models.FloatField(default=0.0, null=True, blank=True)
    tax_rate= models.FloatField(default=0.0, null=True, blank=True)
    discount= models.FloatField(default=0.0, null=True, blank=True)
    total =  models.FloatField(default=0.0, null=True, blank=True)


class debitnote_Reference(models.Model):
    login_details = models.ForeignKey(LoginDetails, on_delete=models.CASCADE,null=True,blank=True)
    company=models.ForeignKey(CompanyDetails,on_delete=models.CASCADE,null=True,blank=True)
    reference_number = models.BigIntegerField(null=True, blank=True)

class debitnote_Comments(models.Model):
    company = models.ForeignKey(CompanyDetails, on_delete=models.CASCADE, null=True)
    debit_note=models.ForeignKey(debitnote,on_delete=models.CASCADE,null=True,blank=True)
    comments = models.CharField(max_length=500,null=True,blank=True)
    
    
    #--------------------------------bills-------------------#
    
    
    
       
#------------Bill---------------
class Bill(models.Model):
    Vendor = models.ForeignKey(Vendor,on_delete=models.CASCADE,null=True,blank=True)
    Bill_Number = models.CharField(max_length=220,null=True,blank=True)
    Reference_Number = models.IntegerField(null=True)
    Purchase_Order_Number = models.CharField(max_length=220,null=True,blank=True)
    Bill_Date = models.DateField(null=True)

    Company_Payment_Terms = models.ForeignKey(Company_Payment_Term,on_delete=models.CASCADE,null=True,blank=True)
    Due_Date = models.DateField(null=True)
    Payment_Method = models.CharField(max_length=220,null=True,blank=True)
    Cheque_Number = models.CharField(max_length=220,null=True,blank=True)
    UPI_Id = models.CharField(max_length=220,null=True,blank=True)
    Bank_Account = models.CharField(max_length=220,null=True,blank=True)
    Customer = models.ForeignKey(Customer, on_delete=models.CASCADE,null=True,blank=True)
    Description = models.CharField(max_length=220,null=True,blank=True)
    Document = models.FileField(upload_to='doc/')
    Sub_Total = models.DecimalField(max_digits=10, decimal_places=2,default=0.00,null=True,blank=True)
    CGST = models.DecimalField(max_digits=10, decimal_places=2,default=0.00,null=True,blank=True)
    SGST = models.DecimalField(max_digits=10, decimal_places=2,default=0.00,null=True,blank=True)
    IGST = models.DecimalField(max_digits=10, decimal_places=2,default=0.00,null=True,blank=True)
    Tax_Amount = models.DecimalField(max_digits=10, decimal_places=2,default=0.00,null=True,blank=True)
    Shipping_Charge =models.DecimalField(max_digits=10, decimal_places=2,default=0.00,null=True,blank=True)
    Adjustment_Number = models.DecimalField(max_digits=10, decimal_places=2,default=0.00,null=True,blank=True)
    Grand_Total = models.DecimalField(max_digits=10, decimal_places=2,default=0.00,null=True,blank=True)
    Advance_amount_Paid = models.DecimalField(max_digits=10, decimal_places=2,default=0.00,null=True,blank=True)
    Balance = models.DecimalField(max_digits=10, decimal_places=2,default=0.00,null=True,blank=True)
    Status = models.CharField(max_length=220,null=True,blank=True)
    Login_Details = models.ForeignKey(LoginDetails, on_delete=models.CASCADE,null=True,blank=True)
    Company = models.ForeignKey(CompanyDetails,on_delete=models.CASCADE)
    Action = models.CharField(max_length=220,null=True,blank=True)

    def getNumFieldName(self):
        return 'Bill_Number'
    
        
class BillItems(models.Model):
    Items = models.CharField(max_length=220,null=True,blank=True)
    HSN = models.CharField(max_length=220,null=True,blank=True)
    Quantity = models.IntegerField(null=True)
    Price = models.IntegerField(null=True)
    Tax_Rate = models.IntegerField(null=True)
    Discount = models.IntegerField(null=True)
    Total = models.IntegerField(null=True)
    Bills = models.ForeignKey(Bill,on_delete=models.CASCADE)
    Login_Details = models.ForeignKey(LoginDetails, on_delete=models.CASCADE,null=True,blank=True)
    Company = models.ForeignKey(CompanyDetails,on_delete=models.CASCADE)
    
class Bill_History(models.Model):
    Company = models.ForeignKey(CompanyDetails,on_delete=models.CASCADE)
    Login_Details = models.ForeignKey(LoginDetails, on_delete=models.CASCADE,null=True,blank=True)
    Bill = models.ForeignKey(Bill,on_delete=models.CASCADE)
    Date = models.DateField(null=True)
    Action = models.CharField(max_length=220,null=True,blank=True)

class Bill_Reference(models.Model):
    Reference_Number = models.IntegerField(null=True)
    Company = models.ForeignKey(CompanyDetails,on_delete=models.CASCADE)
    Login_Details = models.ForeignKey(LoginDetails, on_delete=models.CASCADE,null=True,blank=True)
    Bill = models.ForeignKey(Bill,on_delete=models.CASCADE,null=True,blank=True)
      
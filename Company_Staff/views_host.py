

def debitnote_list(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Company':
            cmp = CompanyDetails.objects.get(login_details = log_details)
            dash_details = CompanyDetails.objects.get(login_details=log_details)
        else:
            cmp = StaffDetails.objects.get(login_details = log_details).company
            dash_details = StaffDetails.objects.get(login_details=log_details)

        rec = debitnote.objects.filter(company = cmp)
        allmodules= ZohoModules.objects.get(company = cmp)
        context = {
            'invoices': rec, 'allmodules':allmodules, 'details':dash_details
        }
        return render(request, 'zohomodules/debitnote/debitnote_list.html', context)
    else:
        return redirect('/')
    
    
def adddebit_note(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Company':
            cmp = CompanyDetails.objects.get(login_details = log_details)
            dash_details = CompanyDetails.objects.get(login_details=log_details)
        else:
            cmp = StaffDetails.objects.get(login_details = log_details).company
            dash_details = StaffDetails.objects.get(login_details=log_details)

        allmodules= ZohoModules.objects.get(company = cmp)
        cust = Vendor.objects.filter(company = cmp, vendor_status = 'Active')
        trm = Company_Payment_Term.objects.filter(company = cmp)
        repeat = CompanyRepeatEvery.objects.filter(company = cmp)
        bnk = Banking.objects.filter(company = cmp)
        priceList = PriceList.objects.filter(company = cmp, type = 'Purchase', status = 'Active')
        itms = Items.objects.filter(company = cmp, activation_tag = 'active')
        units = Unit.objects.filter(company=cmp)
        accounts=Chart_of_Accounts.objects.filter(company=cmp)

        # Fetching last rec_invoice and assigning upcoming ref no as current + 1
        # Also check for if any bill is deleted and ref no is continuos w r t the deleted rec_invoice
        latest_inv = debitnote.objects.filter(company = cmp).order_by('-id').first()

        new_number = int(latest_inv.reference_no) + 1 if latest_inv else 1

        if debitnote_Reference.objects.filter(company = cmp).exists():
            deleted = debitnote_Reference.objects.get(company = cmp)
            
            if deleted:
                while int(deleted.reference_number) >= new_number:
                    new_number+=1

        # Finding next rec_invoice number w r t last rec_invoice number if exists.
        nxtInv = ""
        lastInv = debitnote.objects.filter(company=cmp).last()

        if lastInv:
            inv_no = str(lastInv.debitnote_no)
            numbers = []
            stri = []
            for word in inv_no:
                if word.isdigit():
                    numbers.append(word)
                else:
                    stri.append(word)

            num = ''.join(numbers)
            st = ''.join(stri)

            inv_num = int(num) + 1
            if num[0] == 0:
                nxtInv = st + num.zfill(len(num)) 
            else:
                nxtInv = st + str(inv_num).zfill(len(num))
        else:
            nxtInv = 'DB-001'
        context = {
            'cmp':cmp,'allmodules':allmodules, 'details':dash_details, 'customers': cust,'pTerms':trm, 'repeat':repeat, 'banks':bnk, 'priceListItems':priceList, 'items':itms,
            'invNo':nxtInv, 'ref_no':new_number,'units': units,'accounts':accounts,
        }
        return render(request, 'zohomodules/debitnote/create_debitnote.html', context)
    else:
        return redirect('/')
def newdebitnoteCustomerAjax(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Company':
            com = CompanyDetails.objects.get(login_details = log_details)
        else:
            com = StaffDetails.objects.get(login_details = log_details).company

        if Vendor.objects.filter(company = com, gst_number=request.POST['gst_number']).exists():
            return JsonResponse({'status':False, 'message':'GSTIN already exists'})
        elif Vendor.objects.filter(company = com, pan_number=request.POST['pan_number']).exists():
            return JsonResponse({'status':False, 'message':'PAN No. already exists'})
        elif Vendor.objects.filter(company = com, vendor_email=request.POST['vendor_email']).exists():
            return JsonResponse({'status':False, 'message':'Email already exists'})
        elif Vendor.objects.filter(company = com, phone=request.POST['w_phone']).exists():
            return JsonResponse({'status':False, 'message':'Work Phone no. already exists'})
        elif Vendor.objects.filter(company = com, mobile=request.POST['m_phone']).exists():
            return JsonResponse({'status':False, 'message':'Mobile No. already exists'})

        if request.method=="POST":
            vendor_data=Vendor()
            vendor_data.login_details=log_details
            vendor_data.company=com
            vendor_data.title = request.POST.get('salutation')
            vendor_data.first_name=request.POST['first_name']
            vendor_data.last_name=request.POST['last_name']
            vendor_data.company_name=request.POST['company_name']
            vendor_data.vendor_display_name=request.POST['v_display_name']
            vendor_data.vendor_email=request.POST['vendor_email']
            vendor_data.phone=request.POST['w_phone']
            vendor_data.mobile=request.POST['m_phone']
            vendor_data.skype_name_number=request.POST['skype_number']
            vendor_data.designation=request.POST['designation']
            vendor_data.department=request.POST['department']
            vendor_data.website=request.POST['website']
            vendor_data.gst_treatment=request.POST['gst']
            vendor_data.vendor_status="Active"
            vendor_data.remarks=request.POST['remark']
            vendor_data.current_balance=request.POST['opening_bal']

            x=request.POST['gst']
            if x=="Unregistered Business-not Registered under GST":
                vendor_data.pan_number=request.POST['pan_number']
                vendor_data.gst_number="null"
            else:
                vendor_data.gst_number=request.POST['gst_number']
                vendor_data.pan_number=request.POST['pan_number']

            vendor_data.source_of_supply=request.POST['source_supply']
            vendor_data.currency=request.POST['currency']
            print(vendor_data.currency)
            op_type=request.POST.get('op_type')
            if op_type is not None:
                vendor_data.opening_balance_type=op_type
            else:
                vendor_data.opening_balance_type='Opening Balance not selected'
    
            vendor_data.opening_balance=request.POST['opening_bal']
            vendor_data.payment_term=Company_Payment_Term.objects.get(id=request.POST['payment_terms'])

           
            vendor_data.billing_attention=request.POST['battention']
            vendor_data.billing_country=request.POST['bcountry']
            vendor_data.billing_address=request.POST['baddress']
            vendor_data.billing_city=request.POST['bcity']
            vendor_data.billing_state=request.POST['bstate']
            vendor_data.billing_pin_code=request.POST['bzip']
            vendor_data.billing_phone=request.POST['bphone']
            vendor_data.billing_fax=request.POST['bfax']
            vendor_data.shipping_attention=request.POST['sattention']
            vendor_data.shipping_country=request.POST['s_country']
            vendor_data.shipping_address=request.POST['saddress']
            vendor_data.shipping_city=request.POST['scity']
            vendor_data.shipping_state=request.POST['sstate']
            vendor_data.shipping_pin_code=request.POST['szip']
            vendor_data.shipping_phone=request.POST['sphone']
            vendor_data.shipping_fax=request.POST['sfax']
            vendor_data.save()
           # ................ Adding to History table...........................
            
            vendor_history_obj=VendorHistory()
            vendor_history_obj.company=com
            vendor_history_obj.login_details=log_details
            vendor_history_obj.vendor=vendor_data
            vendor_history_obj.date=date.today()
            vendor_history_obj.action='Completed'
            vendor_history_obj.save()

    # .......................................................adding to remaks table.....................
            vdata=Vendor.objects.get(id=vendor_data.id)
            vendor=vdata
            rdata=Vendor_remarks_table()
            rdata.remarks=request.POST['remark']
            rdata.company=com
            rdata.vendor=vdata
            rdata.save()


     #...........................adding multiple rows of table to model  ........................................................  
            title =request.POST.getlist('tsalutation[]')
            first_name =request.POST.getlist('tfirstName[]')
            last_name =request.POST.getlist('tlastName[]')
            email =request.POST.getlist('tEmail[]')
            work_phone =request.POST.getlist('tWorkPhone[]')
            mobile =request.POST.getlist('tMobilePhone[]')
            skype_name_number =request.POST.getlist('tSkype[]')
            designation =request.POST.getlist('tDesignation[]')
            department =request.POST.getlist('tDepartment[]') 
            print(department) 

            vdata=Vendor.objects.get(id=vendor_data.id)
            vendor=vdata

            if len(title)==len(first_name)==len(last_name)==len(email)==len(work_phone)==len(mobile)==len(skype_name_number)==len(designation)==len(department):
                mapped2=zip(title,first_name,last_name,email,work_phone,mobile,skype_name_number,designation,department)
                mapped2=list(mapped2)
                print(mapped2)
                for ele in mapped2:
                    VendorContactPerson.objects.create(title=ele[0],first_name=ele[1],last_name=ele[2],email=ele[3],work_phone=ele[4],mobile=ele[5],skype_name_number=ele[6],designation=ele[7],department=ele[8],company=com,vendor=vdata)
        
            return JsonResponse({'status':True})
        else:
            return JsonResponse({'status':False})
        
def getvendorsAjax(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Company':
            com = CompanyDetails.objects.get(login_details = log_details)
        else:
            com = StaffDetails.objects.get(login_details = log_details).company

        options = {}
        option_objects = Vendor.objects.filter(company = com, vendor_status = 'Active')
        for option in option_objects:
            options[option.id] = [option.id , option.title, option.first_name, option.last_name]

        return JsonResponse(options)
    else:
        return redirect('/')
    
    
def getVendorrDetailsAjax(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Company':
            cmp = CompanyDetails.objects.get(login_details = log_details)
        else:
            cmp = StaffDetails.objects.get(login_details = log_details).company
        
        custId = request.POST['id']
        cust = Vendor.objects.get(id = custId)
        purbill = Bill.objects.filter(Vendor=custId, Company=cmp)
        recbill_data = [{'id': bill.id, 'bill_number': bill.Bill_Number} for bill in purbill]
        for data in recbill_data:
            print(data['bill_number'])
        data7 = {
      
            'recbill_data': recbill_data,
        }
        print(data7)



        if cust:
            context = {
                'status':True, 'id':cust.id, 'email':cust.vendor_email, 'gstType':cust.gst_treatment,'shipState':cust.source_of_supply,'gstin':False if cust.gst_number == "" or cust.gst_number == None or cust.gst_number == 'null' else True, 'gstNo':cust.gst_number,
                'street':cust.billing_address, 'city':cust.billing_city, 'state':cust.billing_state, 'country':cust.billing_country,'recbill_data': data7, 'recbill_data': recbill_data, 'pincode':cust.billing_pin_code
            }
            return JsonResponse(context)
        else:
            return JsonResponse({'status':False, 'message':'Something went wrong..!'})
    else:
       return redirect('/')

def createdebitnote(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Company':
            com = CompanyDetails.objects.get(login_details = log_details)
        else:
            com = StaffDetails.objects.get(login_details = log_details).company

        if request.method == 'POST':
            invNum = request.POST['rec_invoice_no']

            PatternStr = []
            for word in invNum:
                if word.isdigit():
                    pass
                else:
                    PatternStr.append(word)
            
            pattern = ''
            for j in PatternStr:
                pattern += j

            pattern_exists = checkRecInvNumberPattern(pattern)

            if pattern !="" and pattern_exists:
                res = f'<script>alert("debit note No. Pattern already Exists.! Try another!");window.history.back();</script>'
                return HttpResponse(res)

            if debitnote.objects.filter(company = com, debitnote_no__iexact = invNum).exists():
                res = f'<script>alert("debit note Number `{invNum}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)
            bill_no= request.POST['billSelect'],
            print(bill_no)
            # bill_id=Bill.objects.get(Bill_Number = bill_no)
            bill_id = Bill.objects.get(Bill_Number = request.POST['billSelect'])
            print(bill_id.id)




            inv = debitnote(
                company = com,
                login_details = com.login_details,
                vendor = Vendor.objects.get(id = request.POST['customerId']),
                bills=bill_id,
                vendor_email = request.POST['customer_email'],
                billing_address = request.POST['bill_address'],
                gst_type = request.POST['customer_gst_type'],
                gstin = request.POST['customer_gstin'],
                place_of_supply = request.POST['place_of_supply'],
                # profile_name = request.POST['profile_name'],
                # entry_type = None if request.POST['entry_type'] == "" else request.POST['entry_type'],
                reference_no = request.POST['reference_number'],
                debitnote_no = invNum,
                bill_no= request.POST['billSelect'],

                # payment_terms = Company_Payment_Term.objects.get(id = request.POST['payment_term']),
                debitnote_date = request.POST['start_date'],
                # end_date = datetime.strptime(request.POST['end_date'], '%d-%m-%Y').date(),
                # salesOrder_no = request.POST['order_number'],
                price_list_applied = True if 'priceList' in request.POST else False,
                price_list = None if request.POST['price_list_id'] == "" else PriceList.objects.get(id = request.POST['price_list_id']),
                # repeat_every = CompanyRepeatEvery.objects.get(id = request.POST['repeat_every']),
                payment_method = None if request.POST['payment_method'] == "" else request.POST['payment_method'],
                cheque_number = None if request.POST['cheque_id'] == "" else request.POST['cheque_id'],
                upi_number = None if request.POST['upi_id'] == "" else request.POST['upi_id'],
                bank_account_number = None if request.POST['bnk_id'] == "" else request.POST['bnk_id'],
                subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal']),
                igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst']),
                cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst']),
                sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst']),
                tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount']),
                adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj']),
                shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship']),
                grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal']),
                advance_paid = 0.0 if request.POST['advance'] == "" else float(request.POST['advance']),
                balance = request.POST['grandtotal'] if request.POST['balance'] == "" else float(request.POST['balance']),
                description = request.POST['note'],
                terms_and_conditions = request.POST['terms']
            )

            inv.save()

            if len(request.FILES) != 0:
                inv.document=request.FILES.get('file')
            inv.save()

            if 'Draft' in request.POST:
                inv.status = "Draft"
            elif "Saved" in request.POST:
                inv.status = "Saved" 
            inv.save()

            # Save rec_invoice items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("priceListPrice[]") if 'priceList' in request.POST else request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.state else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total) and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total)
                mapped = list(mapped)
                for ele in mapped:
                    itm = Items.objects.get(id = int(ele[0]))
                    debitnote_item.objects.create(company = com, login_details = com.login_details, debit_note = inv, item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax_rate = ele[5], discount = float(ele[6]), total = float(ele[7]))
                    itm.current_stock -= int(ele[3])
                    itm.save()

            # Save transaction
                    
            debitnote_History.objects.create(
                company = com,
                login_details = log_details,
                debit_note = inv,
                action = 'Created'
            )

            return redirect(debitnote_list)
        else:
            return redirect(adddebit_note)
    else:
       return redirect('/')
   
def view_debitnote(request, id):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Company':
            cmp = CompanyDetails.objects.get(login_details = log_details)
            dash_details = CompanyDetails.objects.get(login_details=log_details)
        else:
            cmp = StaffDetails.objects.get(login_details = log_details).company
            dash_details = StaffDetails.objects.get(login_details=log_details)

        allmodules= ZohoModules.objects.get(company = cmp)

        invoice = debitnote.objects.get(id = id)
        invItems = debitnote_item.objects.filter(debit_note = invoice)
        recInv = debitnote.objects.filter(company = cmp)
        cmts = debitnote_Comments.objects.filter(debit_note = invoice)
        hist = debitnote_History.objects.filter(debit_note = invoice)
        last_history = debitnote_History.objects.filter(debit_note = invoice).last()
        created = debitnote_History.objects.get(debit_note = invoice, action = 'Created')

        context = {
            'cmp':cmp,'allmodules':allmodules, 'details':dash_details, 'invoice':invoice, 'invItems': invItems, 'allInvoices':recInv, 'comments':cmts, 'history':hist, 'last_history':last_history, 'created':created,
        }
        return render(request, 'zohomodules/debitnote/view_debitnote.html', context)
    else:
        return redirect('/')
    
def convertDebit_note(request,id):
    if 'login_id' in request.session:
        rec_inv = debitnote.objects.get(id = id)
        rec_inv.status = 'Saved'
        rec_inv.save()
        return redirect(view_debitnote, id)
    else:
        return redirect('/')

def addDebit_noteComment(request, id):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Company':
            com = CompanyDetails.objects.get(login_details = log_details)
        else:
            com = StaffDetails.objects.get(login_details = log_details).company

        rec_inv = debitnote.objects.get(id = id)
        if request.method == "POST":
            cmt = request.POST['comment'].strip()

            debitnote_Comments.objects.create(company = com, debit_note = rec_inv, comments = cmt)
            return redirect(view_debitnote, id)
        return redirect(view_debitnote, id)
    return redirect('/')

def deleteDebit_noteComment(request,id):
    if 'login_id' in request.session:
        cmt = debitnote_Comments.objects.get(id = id)
        recInvId = cmt.debit_note.id
        cmt.delete()
        return redirect(view_debitnote, recInvId)
    else:
        return redirect('/')

def deletedebit_note(request, id):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Company':
            com = CompanyDetails.objects.get(login_details = log_details)
        else:
            com = StaffDetails.objects.get(login_details = log_details).company

        recInv = debitnote.objects.get( id = id)
        for i in debitnote_item.objects.filter(debit_note = recInv):
            item = Items.objects.get(id = i.item.id)
            item.current_stock += i.quantity
            item.save()
        
        debitnote_item.objects.filter(debit_note = recInv).delete()

        # Storing ref number to deleted table
        # if entry exists and lesser than the current, update and save => Only one entry per company
        if debitnote_Reference.objects.filter(company = com).exists():
            deleted = debitnote_Reference.objects.get(company = com)
            if int(recInv.reference_no) > int(deleted.reference_number):
                deleted.reference_number = recInv.reference_no
                deleted.save()
        else:
            debitnote_Reference.objects.create(company = com, login_details = com.login_details, reference_number = recInv.reference_no)
        
        recInv.delete()
        return redirect(debitnote_list)

def attachdebitnoteFile(request, id):
    if 'login_id' in request.session:
        inv = debitnote.objects.get(id = id)

        if request.method == 'POST' and len(request.FILES) != 0:
            inv.document = request.FILES.get('file')
            inv.save()

        return redirect(view_debitnote, id)
    else:
        return redirect('/')

def debitnotePdf(request,id):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Company':
            com = CompanyDetails.objects.get(login_details = log_details)
        else:
            com = StaffDetails.objects.get(login_details = log_details).company
        
        inv = debitnote.objects.get(id = id)
        itms = debitnote_item.objects.filter(debit_note = inv)
    
        context = {'recInvoice':inv, 'recInvItems':itms,'cmp':com}
        
        template_path = 'zohomodules/recurring_invoice/recurring_invoice_pdf.html'
        fname = 'debitnote_'+inv.debitnote_no
        # Create a Django response object, and specify content_type as pdftemp_
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] =f'attachment; filename = {fname}.pdf'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        # if error then show some funny view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        return redirect('/')

def sharedebitnoteeToEmail(request,id):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Company':
            com = CompanyDetails.objects.get(login_details = log_details)
        else:
            com = StaffDetails.objects.get(login_details = log_details).company
        
        inv = debitnote.objects.get(id = id)
        itms = debitnote_item.objects.filter(debit_note = inv)
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                # print(emails_list)
            
                context = {'recInvoice':inv, 'recInvItems':itms,'cmp':com}
                template_path = 'zohomodules/debitnote/debitnote_pdf.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                filename = f'debitnote_{inv.debitnote_no}'
                subject = f"debitnote_{inv.debitnote_no}"
                # from django.core.mail import EmailMessage as EmailMsg
                email = EmailMsg(subject, f"Hi,\nPlease find the attached debit note for - No.-{inv.debitnote_no}. \n{email_message}\n\n--\nRegards,\n{com.company_name}\n{com.address}\n{com.state} - {com.country}\n{com.contact}", from_email=settings.EMAIL_HOST_USER, to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                messages.success(request, 'debit note details has been shared via email successfully..!')
                return redirect(view_debitnote,id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(view_debitnote, id)
        
def editdebitnote(request, id):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Company':
            cmp = CompanyDetails.objects.get(login_details = log_details)
            dash_details = CompanyDetails.objects.get(login_details=log_details)
        else:
            cmp = StaffDetails.objects.get(login_details = log_details).company
            dash_details = StaffDetails.objects.get(login_details=log_details)

        allmodules= ZohoModules.objects.get(company = cmp)
       
        cust = Vendor.objects.filter(company = cmp, vendor_status = 'Active')
        trm = Bill.objects.filter(Company = cmp)
        repeat = CompanyRepeatEvery.objects.filter(company = cmp)
        bnk = Banking.objects.filter(company = cmp)
        priceList = PriceList.objects.filter(company = cmp, type = 'purchase', status = 'Active')
        itms = Items.objects.filter(company = cmp, activation_tag = 'active')
        units = Unit.objects.filter(company=cmp)
        accounts=Chart_of_Accounts.objects.filter(company=cmp)

        invoice = debitnote.objects.get(id = id)
       

        print(invoice)
        invItems = debitnote_item.objects.filter(debit_note = invoice)

        context = {
            'cmp':cmp,'allmodules':allmodules, 'details':dash_details, 'customers': cust,'pTerms':trm, 'repeat':repeat, 'banks':bnk, 'priceListItems':priceList, 'items':itms,
            'units': units,'accounts':accounts, 'invoice':invoice, 'invItems': invItems,
        }
        return render(request, 'zohomodules/debitnote/edit_debitnote.html', context)
    else:
        return redirect('/')
def get_bill_items(request):
    # Query the database to retrieve the bill object
    billnumber = request.GET.get('bill_number')
    print(billnumber)
    bill = get_object_or_404(Bill, Bill_Number=billnumber)
    print(bill)


    # Retrieve all items associated with the bill
    bill_items = BillItems.objects.filter(Bills=bill)

    # Prepare a list to store item details
    items_list = []
    

    # Iterate over each item and retrieve its details
    for item in bill_items:
        item_details = {
            'Items': item.Items,
            'HSN': item.HSN,
            'Quantity': item.Quantity,
            'Price': item.Price,
            'Tax_Rate': item.Tax_Rate,
            'Discount': item.Discount,
            'Total': item.Total
        }
        items_list.append(item_details)
        print(items_list)

    # Return item details as JSON response
    return JsonResponse(items_list, safe=False)

def checkdebitnoteNumber(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Company':
            com = CompanyDetails.objects.get(login_details = log_details)
        else:
            com = StaffDetails.objects.get(login_details = log_details).company
        
        RecInvNo = request.GET['RecInvNum']

        # Finding next rec_invoice number w r t last rec_invoice number if exists.
        nxtInv = ""
        lastInv = debitnote.objects.filter(company = com).last()
        if lastInv:
            inv_no = str(lastInv.debitnote_no)
            numbers = []
            stri = []
            for word in inv_no:
                if word.isdigit():
                    numbers.append(word)
                else:
                    stri.append(word)

            num = ''.join(numbers)
            st = ''.join(stri)

            inv_num = int(num) + 1
            if num[0] == 0:
                nxtInv = st + num.zfill(len(num)) 
            else:
                nxtInv = st + str(inv_num).zfill(len(num))
        # else:
        #     nxtInv = 'RI01'

        PatternStr = []
        for word in RecInvNo:
            if word.isdigit():
                pass
            else:
                PatternStr.append(word)
        
        pattern = ''
        for j in PatternStr:
            pattern += j

        pattern_exists = checkRecInvNumberPattern(pattern)

        if pattern !="" and pattern_exists:
            return JsonResponse({'status':False, 'message':'Debit Note No. Pattern already Exists.!'})
        elif debitnote.objects.filter(company = com, debitnote_no__iexact = RecInvNo).exists():
            return JsonResponse({'status':False, 'message':'Debit Note No. already Exists.!'})
        elif nxtInv != "" and RecInvNo != nxtInv:
            return JsonResponse({'status':False, 'message':'Debit Note No. is not continuous.!'})
        else:
            return JsonResponse({'status':True, 'message':'Number is okay.!'})
    else:
       return redirect('/')




def updatedebitnote(request, id):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Company':
            com = CompanyDetails.objects.get(login_details = log_details)
        else:
            com = StaffDetails.objects.get(login_details = log_details).company

        rec_inv = debitnote.objects.get(id = id)
        if request.method == 'POST':
            invNum = request.POST['rec_invoice_no']
            bill_id = Bill.objects.get(Bill_Number =  request.POST['bill_number'])


            PatternStr = []
            for word in invNum:
                if word.isdigit():
                    pass
                else:
                    PatternStr.append(word)
            
            pattern = ''
            for j in PatternStr:
                pattern += j

            pattern_exists = checkRecInvNumberPattern(pattern)

            if pattern !="" and pattern_exists:
                res = f'<script>alert("Debitnote No. Pattern already Exists.! Try another!");window.history.back();</script>'
                return HttpResponse(res)

            if rec_inv.debitnote_no != invNum and debitnote.objects.filter(company = com, debitnote_no__iexact = invNum).exists():
                res = f'<script>alert("Debit note Number `{invNum}` already exists, try another!");window.history.back();</script>'
                return HttpResponse(res)

            rec_inv.vendor = Vendor.objects.get(id = request.POST['customerId'])
            rec_inv.bills= Bill.objects.get(Bill_Number =  request.POST['bill_number'])
            rec_inv.vendor_email = request.POST['customer_email']
            rec_inv.billing_address = request.POST['bill_address']
            rec_inv.gst_type = request.POST['customer_gst_type']
            rec_inv.gstin = request.POST['customer_gstin']
            rec_inv.place_of_supply = request.POST['place_of_supply']
            # rec_inv.profile_name = request.POST['profile_name']
            # rec_inv.entry_type = None if request.POST['entry_type'] == "" else request.POST['entry_type']
            rec_inv.reference_no = request.POST['reference_number']
            rec_inv.debitnote_no = invNum
            # rec_inv.payment_terms = Company_Payment_Term.objects.get(id = request.POST['payment_term'])
            rec_inv.debitnote_date = request.POST['start_date']
            rec_inv.bill_no = request.POST['bill_number']
            # rec_inv.salesOrder_no = request.POST['order_number']
            rec_inv.price_list_applied = True if 'priceList' in request.POST else False
            rec_inv.price_list = None if request.POST['price_list_id'] == "" else PriceList.objects.get(id = request.POST['price_list_id'])
            # rec_inv.repeat_every = CompanyRepeatEvery.objects.get(id = request.POST['repeat_every'])
            rec_inv.payment_method = None if request.POST['payment_method'] == "" else request.POST['payment_method']
            rec_inv.cheque_number = None if request.POST['cheque_id'] == "" else request.POST['cheque_id']
            rec_inv.upi_number = None if request.POST['upi_id'] == "" else request.POST['upi_id']
            rec_inv.bank_account_number = None if request.POST['bnk_id'] == "" else request.POST['bnk_id']
            rec_inv.subtotal = 0.0 if request.POST['subtotal'] == "" else float(request.POST['subtotal'])
            rec_inv.igst = 0.0 if request.POST['igst'] == "" else float(request.POST['igst'])
            rec_inv.cgst = 0.0 if request.POST['cgst'] == "" else float(request.POST['cgst'])
            rec_inv.sgst = 0.0 if request.POST['sgst'] == "" else float(request.POST['sgst'])
            rec_inv.tax_amount = 0.0 if request.POST['taxamount'] == "" else float(request.POST['taxamount'])
            rec_inv.adjustment = 0.0 if request.POST['adj'] == "" else float(request.POST['adj'])
            rec_inv.shipping_charge = 0.0 if request.POST['ship'] == "" else float(request.POST['ship'])
            rec_inv.grandtotal = 0.0 if request.POST['grandtotal'] == "" else float(request.POST['grandtotal'])
            rec_inv.advance_paid = 0.0 if request.POST['advance'] == "" else float(request.POST['advance'])
            rec_inv.balance = request.POST['grandtotal'] if request.POST['balance'] == "" else float(request.POST['balance'])
            rec_inv.description = request.POST['note']
            rec_inv.terms_and_conditions = request.POST['terms']

            if len(request.FILES) != 0:
                rec_inv.document=request.FILES.get('file')
            rec_inv.save()


            # Save rec_invoice items.

            itemId = request.POST.getlist("item_id[]")
            itemName = request.POST.getlist("item_name[]")
            hsn  = request.POST.getlist("hsn[]")
            qty = request.POST.getlist("qty[]")
            price = request.POST.getlist("priceListPrice[]") if 'priceList' in request.POST else request.POST.getlist("price[]")
            tax = request.POST.getlist("taxGST[]") if request.POST['place_of_supply'] == com.state else request.POST.getlist("taxIGST[]")
            discount = request.POST.getlist("discount[]")
            total = request.POST.getlist("total[]")
            inv_item_ids = request.POST.getlist("id[]")
            invItem_ids = [int(id) for id in inv_item_ids]

            inv_items = debitnote_item.objects.filter(debit_note = rec_inv)
            object_ids = [obj.id for obj in inv_items]

            ids_to_delete = [obj_id for obj_id in object_ids if obj_id not in invItem_ids]
            for itmId in ids_to_delete:
                invItem = debitnote_item.objects.get(id = itmId)
                item = Items.objects.get(id = invItem.item.id)
                item.current_stock += invItem.quantity
                item.save()

            debitnote_item.objects.filter(id__in=ids_to_delete).delete()
            
            count = debitnote_item.objects.filter(debit_note = rec_inv).count()

            if len(itemId)==len(itemName)==len(hsn)==len(qty)==len(price)==len(tax)==len(discount)==len(total)==len(invItem_ids) and invItem_ids and itemId and itemName and hsn and qty and price and tax and discount and total:
                mapped = zip(itemId,itemName,hsn,qty,price,tax,discount,total,invItem_ids)
                mapped = list(mapped)
                for ele in mapped:
                    if int(len(itemId))>int(count):
                        if ele[8] == 0:
                            itm = Items.objects.get(id = int(ele[0]))
                            debitnote_item.objects.create(company = com, login_details = com.login_details, debit_note = rec_inv, item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax_rate = ele[5], discount = float(ele[6]), total = float(ele[7]))
                            itm.current_stock -= int(ele[3])
                            itm.save()
                        else:
                            itm = Items.objects.get(id = int(ele[0]))
                            inItm = debitnote_item.objects.get(id = int(ele[8]))
                            crQty = int(inItm.quantity)
                            
                            debitnote_item.objects.filter( id = int(ele[8])).update(debit_note = rec_inv, item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax_rate = ele[5], discount = float(ele[6]), total = float(ele[7]))

                            if crQty < int(ele[3]):
                                itm.current_stock -=  abs(crQty - int(ele[3]))
                            elif crQty > int(ele[3]):
                                itm.current_stock += abs(crQty - int(ele[3]))
                            itm.save()
                    else:
                        itm = Items.objects.get(id = int(ele[0]))
                        inItm = debitnote_item.objects.get(id = int(ele[8]))
                        crQty = int(inItm.quantity)

                        debitnote_item.objects.filter( id = int(ele[8])).update(debit_note = rec_inv, item = itm, hsn = ele[2], quantity = int(ele[3]), price = float(ele[4]), tax_rate = ele[5], discount = float(ele[6]), total = float(ele[7]))

                        if crQty < int(ele[3]):
                            itm.current_stock -=  abs(crQty - int(ele[3]))
                        elif crQty > int(ele[3]):
                            itm.current_stock += abs(crQty - int(ele[3]))
                        itm.save()
            
            # Save transaction
                    
            debitnote_History.objects.create(
                company = com,
                login_details = log_details,
                debit_note = rec_inv,
                action = 'Edited'
            )

            return redirect(view_debitnote, id)
        else:
            return redirect(view_debitnote, id)
    else:
       return redirect('/')
   
def downloaddebitnoteSampleImportFile(request):
    recInv_table_data = [['SLNO','VENDOR','DATE','PLACE OF SUPPLY','DB NO','PRICE LIST','DESCRIPTION','SUB TOTAL','IGST','CGST','SGST','TAX AMOUNT','ADJUSTMENT','SHIPPING CHARGE','GRAND TOTAL','ADVANCE'],['1', 'Kevin Debryne', '2024-03-20', '[KL]-Kerala','DB100','','','1000','0','25','25','50','0','0','1050','1000']]
    items_table_data = [['DB NO', 'PRODUCT','HSN','QUANTITY','PRICE','TAX PERCENTAGE','DISCOUNT','TOTAL'], ['1', 'Test Item 1','789987','1','1000','5','0','1000']]

    wb = Workbook()

    sheet1 = wb.active
    sheet1.title = 'DEBIT_NOTE'
    sheet2 = wb.create_sheet(title='items')

    # Populate the sheets with data
    for row in recInv_table_data:
        sheet1.append(row)

    for row in items_table_data:
        sheet2.append(row)

    # Create a response with the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=debit_note_sample_file.xlsx'

    # Save the workbook to the response
    wb.save(response)

    return response

def importdebitnoteFromExcel(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Company':
            com = CompanyDetails.objects.get(login_details = log_details)
        else:
            com = StaffDetails.objects.get(login_details = log_details).company 

        current_datetime = timezone.now()
        dateToday =  current_datetime.date()

        if request.method == "POST" and 'excel_file' in request.FILES:
        
            excel_file = request.FILES['excel_file']
            print("ok")

            wb = load_workbook(excel_file)

            # checking estimate sheet columns
            try:
                ws = wb["DEBIT_NOTE"]
            except:
                print('sheet not found')
                messages.error(request,'`DEBIT_NOTE` sheet not found.! Please check.')
                return redirect(debitnote_list)

            try:
                ws = wb["items"]
            except:
                print('sheet not found')
                messages.error(request,'`items` sheet not found.! Please check.')
                return redirect(debitnote_list)
            
            ws = wb["DEBIT_NOTE"]
            rec_inv_columns = ['SLNO','VENDOR','DATE','PLACE OF SUPPLY','DB NO','PRICE LIST','DESCRIPTION','SUB TOTAL','IGST','CGST','SGST','TAX AMOUNT','ADJUSTMENT','SHIPPING CHARGE','GRAND TOTAL','ADVANCE']
            rec_inv_sheet = [cell.value for cell in ws[1]]
            if rec_inv_sheet != rec_inv_columns:
                print('invalid sheet')
                messages.error(request,'`DEBIT_NOTE` sheet column names or order is not in the required formate.! Please check.')
                return redirect(debitnote_list)

            for row in ws.iter_rows(min_row=2, values_only=True):
                slno, vendor,date,place_of_supply, debitnote_no, price_list, description, subtotal, igst, cgst, sgst, taxamount, adjustment, shipping, grandtotal, advance = row
                if slno is None  or vendor is None  or date is None or place_of_supply is None  or debitnote_no is None  or subtotal is None or taxamount is None or grandtotal is None:
                    print('debitnote == invalid data')
                    messages.error(request,'`debitnote` sheet entries missing required fields.! Please check.')
                    return redirect(debitnote_list)
            
            # checking items sheet columns
            ws = wb["items"]
            items_columns = ['DB NO','PRODUCT','HSN','QUANTITY','PRICE','TAX PERCENTAGE','DISCOUNT','TOTAL']
            items_sheet = [cell.value for cell in ws[1]]
            if items_sheet != items_columns:
                print('invalid sheet')
                messages.error(request,'`items` sheet column names or order is not in the required formate.! Please check.')
                return redirect(debitnote_list)

            for row in ws.iter_rows(min_row=2, values_only=True):
                db_no,name,hsn,quantity,price,tax_percentage,discount,total = row
                if db_no is None or name is None or quantity is None or tax_percentage is None or total is None:
                    print('items == invalid data')
                    messages.error(request,'`items` sheet entries missing required fields.! Please check.')
                    return redirect(debitnote_list)
            
            # getting data from rec_invoice sheet and create rec_invoice.
            incorrect_data = []
            existing_pattern = []
            ws = wb['DEBIT_NOTE']
            for row in ws.iter_rows(min_row=2, values_only=True):
                slno, vendor,debit_note_date,place_of_supply, debit_note_no, price_list, description, subtotal, igst, cgst, sgst, taxamount, adjustment, shipping, grandtotal, advance = row
                recInvNo = slno
                if slno is None:
                    continue
                # Fetching last rec_inv and assigning upcoming rec_inv no as current + 1
                # Also check for if any rec_inv is deleted and rec_inv no is continuos w r t the deleted rec_inv
                latest_inv = debitnote.objects.filter(company = com).order_by('-id').first()
                
                new_number = int(latest_inv.reference_no) + 1 if latest_inv else 1

                if debitnote_Reference.objects.filter(company = com).exists():
                    deleted = debitnote_Reference.objects.get(company = com)
                    
                    if deleted:
                        while int(deleted.reference_number) >= new_number:
                            new_number+=1
                
                cust = vendor.split(' ')
            
                if len(cust) > 2:
                    cust[1] = cust[1] + ' ' + ' '.join(cust[2:])
                    cust = cust[:2]
                    fName = cust[0]
                    lName = cust[1]
                else:
                    fName = cust[0]
                    lName = cust[1]
                print(cust,fName,lName)

                if lName == "":  
                    if not Vendor.objects.filter(company = com, first_name = fName).exists():
                        print('No vendor1')
                        incorrect_data.append(slno)
                        continue
                    try:
                        c = Vendor.objects.filter(company = com, first_name = fName).first()
                        email = c.vendor_email
                        gstType = c.gst_treatment
                        gstIn = c.gst_number
                        adrs = f"{c.billing_address}, {c.billing_city}\n{c.billing_state}\n{c.billing_country}\n{c.billing_pin_code}"
                    except:
                        pass

                if fName != "" and lName != "":  
                    if not Vendor.objects.filter(company = com, first_name = fName, last_name = lName).exists():
                        print('No vendor2')
                        incorrect_data.append(slno)
                        continue
                    try:
                        c = Vendor.objects.filter(company = com, first_name = fName, last_name = lName).first()
                        email = c.vendor_email
                        gstType = c.gst_treatment
                        gstIn = c.gst_number
                        adrs = f"{c.billing_address}, {c.billing_city}\n{c.billing_state}\n{c.billing_country}\n{c.billing_pin_code}"
                    except:
                        pass

                if debit_note_date is None:
                    debit_note_date = dateToday
                else:
                    debit_note_date = datetime.strptime(debit_note_date, '%Y-%m-%d').date()

                PatternStr = []
                for word in debit_note_no:
                    if word.isdigit():
                        pass
                    else:
                        PatternStr.append(word)
                
                pattern = ''
                for j in PatternStr:
                    pattern += j

                pattern_exists = checkRecInvNumberPattern(pattern)

                if pattern !="" and pattern_exists:
                    existing_pattern.append(slno)
                    continue

                while debitnote.objects.filter(company = com, debitnote_no__iexact = debit_note_no).exists():
                    debit_note_no = getNextRINumber(debit_note_no)

                
                try:
                    priceList = PriceList.objects.get(company = com, name = price_list)
                except:
                    priceList = None

                

                recInv = debitnote(
                    company = com,
                    login_details = com.login_details,
                    vendor = None if c is None else c,
                    vendor_email = email,
                    billing_address = adrs,
                    gst_type = gstType,
                    gstin = gstIn,
                    place_of_supply = place_of_supply,
                    reference_no = new_number,
                    debitnote_no = debit_note_no,
                    debitnote_date = debit_note_date,
                    price_list_applied = True if priceList is not None else False,
                    price_list = priceList,
                    payment_method = None,
                    cheque_number = None,
                    upi_number = None,
                    bank_account_number = None,
                    subtotal = 0.0 if subtotal == "" else float(subtotal),
                    igst = 0.0 if igst == "" else float(igst),
                    cgst = 0.0 if cgst == "" else float(cgst),
                    sgst = 0.0 if sgst == "" else float(sgst),
                    tax_amount = 0.0 if taxamount == "" else float(taxamount),
                    adjustment = 0.0 if adjustment == "" else float(adjustment),
                    shipping_charge = 0.0 if shipping == "" else float(shipping),
                    grandtotal = 0.0 if grandtotal == "" else float(grandtotal),
                    advance_paid = 0.0 if advance == "" else float(advance),
                    balance = float(grandtotal) - float(advance),
                    description = description,
                    status = "Draft"
                )
                recInv.save()

                # Transaction history
                history = debitnote_History(
                    company = com,
                    login_details = log_details,
                    debit_note = recInv,
                    action = 'Created'
                )
                history.save()

                # Items for the estimate
                ws = wb['items']
                for row in ws.iter_rows(min_row=2, values_only=True):
                    rec_no,name,hsn,quantity,price,tax_percentage,discount,total = row
                    if int(rec_no) == int(recInvNo):
                        print(row)
                        if discount is None:
                            discount=0
                        if price is None:
                            price=0
                        if quantity is None:
                            quantity=0
                        if not Items.objects.filter(company = com, item_name = name).exists():
                            print('No Item')
                            incorrect_data.append(rec_no)
                            continue
                        try:
                            itm = Items.objects.filter(company = com, item_name = name).first()
                        except:
                            pass

                        debitnote_item.objects.create(company = com, login_details = com.login_details, debit_note = recInv, item = itm, hsn = hsn, quantity = quantity, price = price, tax_rate = tax_percentage, discount = discount, total = total)
                        itm.current_stock -= int(quantity)
                        itm.save()

            if not incorrect_data and not existing_pattern:
                messages.success(request, 'Data imported successfully.!')
                return redirect(debitnote_list)
            else:
                if incorrect_data:
                    messages.warning(request, f'Data with following SlNo could not import due to incorrect data provided -> {", ".join(str(item) for item in incorrect_data)}')
                if existing_pattern:
                    messages.warning(request, f'Data with following SlNo could not import due to DB No pattern exists already -> {", ".join(str(item) for item in existing_pattern)}')
                return redirect(debitnote_list)
        else:
            return redirect(debitnote_list)
    else:
        return redirect('/')
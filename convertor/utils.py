def generate_result_csv(data):
    import tempfile
    import re, csv
    def parse_row(row):
        print(row, 'row\n')
    
        product_name_pattern = r".+?(?=\d{8})"
        code_pattern = r"\d{8}"
        cat_pattern = r"(DN|DS)([A-Z0-9]+)"
        batch_pattern = r"([A-Z0-9]+)(?=[A-Z-]+\d{2}\.\d{4})"
        mfg_name_pattern = r"[A-Z-]+(?=\d{2}\.\d{4})"
        date_pattern = r"\d{2}\.\d{4}"
        numeric_pattern = r"\d+\.\d{2}|\d+,\d+\.\d{2}|-?\d+\.\d{2}"

        # Extracting data
        product_name = re.search(product_name_pattern, row)
        code = re.search(code_pattern, row)
        cat = re.search(cat_pattern, row)
        batch = re.search(batch_pattern, row)
        mfg_name = re.search(mfg_name_pattern, row)
        dates = re.findall(date_pattern, row)
        numerics = re.findall(numeric_pattern, row)

        # Constructing result
        result = {
            "Plant": 1309,
            "Order Type": "ZDPS",
            "Price grp": "",
            "Customer": "",
            "Customer Name": "",
            "City/Destination":"",
            "Invoice No":"",
            "Invoice Date":"",
            "Product Name": product_name.group() if product_name else None,
            "HSN/SAC Code": code.group() if code else None,
            "CAT": cat.group(2) if cat else None,
            "BATCH": batch.group(1) if batch else None,
            "MFG.NAME": mfg_name.group() if mfg_name else None,
            "MFG.DT": dates[0] if dates else None,
            "EXP.DT": dates[1] if dates else None,
            "GST Rate (%)": numerics[0] if numerics else None,
            "BILLED QTY": numerics[1] if numerics else None,
            "FREE QTY": numerics[2] if numerics else None,
            "MRP": numerics[3] if numerics else None,
            "Billing Rate": numerics[4] if numerics else None,
            "Taxable Amt": numerics[5] if numerics else None,
            "DISC%": numerics[6] if numerics else None,
            "Invoice Amount": numerics[7] if numerics else None,
            "Plant Name": "",
            "Dist. channel" :"",
            "Customer State": "",
            "Customer p0 Number": "Nil",
            "PO date": "",
            "System Order No.": "",
            "Order Date": "",
            "Product type": "ZFGS",
            "Local Sales Tax NO.": "",
            "Central Sales Tax NO.":"",
            "Material Group 3": "",
            "Division":"",
            "Mfg. Plant": "",	
            "Mfg. Date": "",	
            "Exp. Date": "",	
            "Free Quantity": "",	
            "Disc.": "",	
            "Cash Disc.": "",	
            "Tax Type": "",	
            "Tax %": "",	
            "Tax Amt.": "",	
            "Add. Tax": "",	
            "Surcharge": "",	
            "Total Tax": "",	
            "LBT	Ref.": "", "Invoice No.(Returns)": "",	
            "Ref. Inv. Dt.": "",	
            "Exc. Inv. No.": "",	
            "Exc. Inv. Dt.": "",	
            "Exc. Duty %": "",	
            "Exc. Inv. Amt": "",	
            "Product Status": "",	
            "Reason For Return": "",	
            "Reason For Rejection": "",	
            "Str. Loc.": "",	
            "Sales District": "",	
            "Sales Group": "",	
            "Customer Group": "",	
            "Emp. Code": "",	
            "Employee Name": "",	
            "C Form No.": "",	
            "HSN Code": "",	
            "Business Place": "",	
            "JOCG": "",	
            "JOSG": "",	
            "JOIG": "",	
            "JOUG": "",	
            "PTR": "",	
            "PTS": "",	
            "Disc. %": "",	
            "Prod. Category": "",	
            "Prod. Category Description": "",	
            "GSTIN No. of Customer": "",	
            "GST Inv. No.": "",   
        }
        return result
    # Extracting the product data section
    product_data_section = re.search(r'PRODUCT NAME,[^*]*', data, re.DOTALL)
    if product_data_section:
        product_lines = product_data_section.group().split('\n')[1:]  # Skip the header line

    # Process each product line and store in a list
    processed_data = [parse_row(line) for line in product_lines if parse_row(line)]
    csv_file_name = 'processed_data1.csv'

    # Define the field names (columns) based on the keys of the first dictionary in the list
    fieldnames = processed_data[0].keys() if processed_data else []
    # Writing to CSV
    with tempfile.NamedTemporaryFile(delete=False, mode='w+', newline='', encoding='utf-8') as temp_file:
        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)

        # Write the header
        writer.writeheader()

        # Write the rows
        for row in processed_data:
            writer.writerow(row)
    return temp_file

def convert_pdf_to_csv(pdf_file_path, file_name):
    import tabula
    tabula.convert_into(pdf_file_path, file_name, output_format="csv", pages=1)
    generate_result_csv(open(file_name, 'r').read())

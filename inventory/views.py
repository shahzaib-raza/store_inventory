from django.shortcuts import render, redirect
import pandas as pd
import datetime as dt
import sqlite3

loggedin = False
NAME = None

def auth_login(user, pas):
    con = sqlite3.connect("store_inventory.sqlite")
    cur = con.cursor()
    q = f"SELECT * FROM users WHERE (user='{user}') AND (password='{pas}')"
    res = cur.execute(q).fetchall()
    con.close()
    if len(res) > 0:
        return True
    return False

# Create your views here.
def login(request):
    global loggedin
    global NAME
    if 'user' in request.POST and 'password' in request.POST:
        un = request.POST.get('user')
        pas = request.POST.get('password')
        check = auth_login(un, pas)
        if check == True:
            loggedin = True
            NAME = un
            return redirect(to='/index/')
        else:
            return render(request, 'login.html', {'note': 'wrong userame or password'})
    return render(request, 'login.html')

def get_table():
    conn = sqlite3.connect("store_inventory.sqlite")
    try:
        df = pd.read_sql(con=conn, sql=f"SELECT * FROM stock;")
        df = df[df['Available_stock'] < 5].set_index('Code').sort_index().to_html()
    except:
        cols = ['Code', 'Item', 'Type', 'Category', 'Available_stock', 'Need_to_order']
        df = pd.DataFrame(columns=cols).set_index('Code').to_html()
    conn.close()
    return df


def handle_stock(request):

    if 'Home' in request.POST:
        return "OK"
    elif 'remove' in request.POST:
        code = int(request.POST.get('remove'))
        conn = sqlite3.connect("store_inventory.sqlite")
        qry = f"DELETE FROM stock WHERE Code = {code};"
        cur = conn.cursor()
        cur.execute(qry)
        conn.commit()
        conn.close()
        return f"stock {code} have been removed successfully!"
    elif 'Code' in request.POST:
        
        code = int(request.POST.get('Code'))
        item = str(request.POST.get('Item')).upper()
        type = str(request.POST.get('Type')).upper()
        cat = str(request.POST.get('Category'))
        avl = int(request.POST.get('Available_stock'))
        if avl < 5:
            nto = "Need_to_order"
        else:
            nto = ''
        conn = sqlite3.connect("store_inventory.sqlite")
        qry = f"INSERT INTO stock (Code, Item, Type, Category, Available_stock, Need_to_order) VALUES ({code}, '{item}', '{type}', '{cat}', {avl}, '{nto}');"
        cur = conn.cursor()
        cur.execute(qry)
        conn.commit()
        conn.close()
        return f"stock {code} have been added successfully!"
    else:
        return "error"

def stock(request):
    if loggedin == False:
        return redirect(to='/login/')
    if request.POST:
        ret = handle_stock(request)
    else:
        ret = ''
    if ret =='OK':
        return redirect(to='/index/')
    conn = sqlite3.connect("store_inventory.sqlite")
    df = pd.read_sql(con=conn, sql=f"SELECT * FROM stock;").set_index('Code').sort_index().to_html()
    conn.close()
    return render(request, 'stock.html', {'tab_data': df, 'ret': ret})


def handle_in(request):
    global NAME
    if 'Home' in request.POST:
        return "OK"
    elif 'remove' in request.POST:
        entry = int(request.POST.get('remove'))
        conn = sqlite3.connect("store_inventory.sqlite")
        qry = f"DELETE FROM stock_in WHERE entry = {entry};"
        cur = conn.cursor()
        cur.execute(qry)
        conn.commit()
        conn.close()
        return f"entry {entry} have been removed successfully!"
    elif 'Code' in request.POST:
        conn = sqlite3.connect("store_inventory.sqlite")
        max_e_q = "SELECT max(entry) FROM stock_in;"
        cur = conn.cursor()
        resp_1 = cur.execute(max_e_q).fetchall()
        ne = int(resp_1[0][0]) + 1
        # rd = dt.date.fromisoformat(str(request.POST.get('Receiving_date'))).strftime("%d/%m/%Y")
        rd = dt.date.today().strftime("%d/%m/%Y")
        code = str(request.POST.get('Code'))
        q_s = f"SELECT Item, Type, Available_stock FROM stock WHERE Code = {code};"
        item, type, av_stck = cur.execute(q_s).fetchall()[0]
        qty = int(request.POST.get('Quantity'))
        ppt = float(request.POST.get('Price_per_type'))
        pn = str(request.POST.get('Purchaser_name'))
        bd = dt.date.fromisoformat(str(request.POST.get('Billing_date'))).strftime("%d/%m/%Y")
        # rb = str(request.POST.get('Received_by'))
        rb = NAME.capitalize()
        rmk = str(request.POST.get('Remark'))
        new_st = int(av_stck) + qty
        ins_q = f"""
            INSERT INTO stock_in (entry, Receiving_Date, Code, Item, Type, Quantity, Price_per_type, Purchaser_name, Billing_date, Received_by, Remark)
            VALUES ({ne}, '{rd}', {code}, '{item}', '{type}', {qty}, {ppt}, '{pn}', '{bd}', '{rb}', '{rmk}');
        """
        cur.execute(ins_q)
        up_q = f"UPDATE stock SET Available_stock = {new_st} WHERE Code = {code};"
        cur.execute(up_q)
        if new_st >= 5:
            up_q = f"UPDATE stock SET Need_to_order = '' WHERE Code = {code};"
            cur.execute(up_q)
        conn.commit()
        conn.close()
        return f"entry {ne} have been added successfully!"
    else:
        return "error"


def inv_in(request):
    if loggedin == False:
        return redirect(to='/login/')
    if request.POST:
        ret = handle_in(request)
    else:
        ret = ''
    if ret =='OK':
        return redirect(to='/index/')
    conn = sqlite3.connect("store_inventory.sqlite")
    df = pd.read_sql(con=conn, sql=f"SELECT * FROM stock_in;").set_index('entry').sort_index().to_html()
    conn.close()
    return render(request, 'inventory_in.html',  {'tab_data': df, 'ret': ret})


def handle_out(request):
    global NAME
    if 'Home' in request.POST:
        return "OK"
    elif 'remove' in request.POST:
        entry = int(request.POST.get('remove'))
        conn = sqlite3.connect("store_inventory.sqlite")
        qry = f"DELETE FROM stock_out WHERE entry = {entry};"
        cur = conn.cursor()
        cur.execute(qry)
        conn.commit()
        conn.close()
        return f"entry {entry} have been removed successfully!"
    elif 'Code' in request.POST:
        conn = sqlite3.connect("store_inventory.sqlite")
        max_e_q = "SELECT max(entry) FROM stock_out;"
        cur = conn.cursor()
        resp_1 = cur.execute(max_e_q).fetchall()
        ne = int(resp_1[0][0]) + 1
        # rd = dt.date.fromisoformat(str(request.POST.get('Date'))).strftime("%d/%m/%Y")
        rd = dt.date.today().strftime("%d/%m/%Y")
        nm = request.POST.get('Name')
        dep = request.POST.get('Department')
        code = str(request.POST.get('Code'))
        q_s = f"SELECT Item, Type, Available_stock FROM stock WHERE Code = {code};"
        item, type, av_stck = cur.execute(q_s).fetchall()[0]
        qty = int(request.POST.get('Quantity'))
        # dil_b = str(request.POST.get('Delivered_by'))
        dil_b = NAME.capitalize()
        rmk = str(request.POST.get('Remark'))
        if qty <= av_stck:
            new_st = int(av_stck) - qty
            ins_q = f"""
                INSERT INTO stock_out (entry, Date, Name, Department, Code, Item, Type, Quantity, Delivered_by, Remarks)
                VALUES ({ne}, '{rd}', '{nm}', '{dep}', {code}, '{item}', '{type}', {qty}, '{dil_b}', '{rmk}');
            """
            cur.execute(ins_q)
            up_q = f"UPDATE stock SET Available_stock = {new_st} WHERE Code = {code};"
            cur.execute(up_q)
            up_q = f"UPDATE stock SET Need_to_order = 'Need_to_order' WHERE Code = {code};"
            cur.execute(up_q)
            conn.commit()
            conn.close()
            return f"entry {ne} have been added successfully!"
        else:
            return f"Unable to stock out {qty} items for {item}\navailable stock is {av_stck}"
    else:
        return "error"

def inv_out(request):
    if loggedin == False:
        return redirect(to='/login/')
    if request.POST:
        ret = handle_out(request)
    else:
        ret = ''
    if ret =='OK':
        return redirect(to='/index/')
    conn = sqlite3.connect("store_inventory.sqlite")
    df = pd.read_sql(con=conn, sql=f"SELECT * FROM stock_out;").set_index('entry').sort_index().to_html()
    conn.close()
    return render(request, 'inventory_out.html',  {'tab_data': df, 'ret': ret})


def index(request):
    global loggedin
    global NAME
    
    tab_data = get_table()

    if loggedin == True:
        if 'Stock' in request.POST:
            return redirect(to='/stock/')
        elif 'Inventory_In' in request.POST:
            return redirect(to='/inv_in/')
        elif 'Inventory_Out' in request.POST:
            return redirect(to='/inv_out/')
        elif 'Log_out' in request.POST:
            loggedin = False
            NAME = None
            return redirect(to='/login/')
        else:
            return render(request, 'index.html', {'tab_data': tab_data})
    else:
        return redirect(to='/login/')

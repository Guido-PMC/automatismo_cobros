import json
import requests
import time
import datetime
from datetime import date
from datetime import datetime
import gspread
import pandas as pd
import os
from binance.client import Client
from twilio.rest import Client as ClientTwilio
from oauth2client.service_account import ServiceAccountCredentials
import cronitor
cronitor.api_key = '5e67b190fd224e6ca399c5e1b7286199'
cronitor.Monitor.put(
    key='AutomatismoCobros',
    type='job'
)
monitor = cronitor.Monitor('AutomatismoCobros')

api_key = "elk9mwrD7IAZA4DhVWAHpxk4D6lemE3BG4DMVlXPF1XKdYpVhZDwToWrg5vFJLHV"
api_secret = "AVlfFnvUfKTaplr7lBFq0e1l208CTu30WT23wiivSvldurEOrkt3rwiGrnWrEPLX"
client = Client(api_key, api_secret)


wallet_pmc = "0x34fa7b1abfd6e397de3c39934635fedb925eea4d"
api_key = "3QWUD76YB246W8ZRUJBDNI69IDPCS6C36V"
gwei_to_eth = 1000000000000000000

if datetime.now().day >= 16:
    mesInicio = (datetime.now().month)
    mesFin = (datetime.now().month+1)
    diaInicio = 16
    diaFin = 15
if datetime.now().day <= 15:
    mesInicio = (datetime.now().month-1)
    mesFin = (datetime.now().month)
    diaInicio = 16
    diaFin = 15
ano = datetime.now().year

inicioPeriodoFacturacion = date(int(ano),int(mesInicio),int(diaInicio))
finPeriodoFacturacion = date(int(ano),int(mesFin),int(diaFin))
inicioUnixPeriodoFacturacion = time.mktime(inicioPeriodoFacturacion.timetuple())
finUnixPeriodoFacturacion = time.mktime(finPeriodoFacturacion.timetuple())
print("Inicio: "+str(diaInicio)+"/"+str(mesInicio))
print("Fin: "+str(diaFin)+"/"+str(mesFin))
print("Inicio unix: "+str(inicioUnixPeriodoFacturacion))
print("Fin unix: "+str(finUnixPeriodoFacturacion))
tuple_months = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
tuple_excel_columns = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","AA","AB","AC","AD","AE","AF","AG","AH","AI","AJ","AK","AL","AM","AN","AO","AP","AQ","AR","AS","AT","AU","AV","AW","AX","AY","AZ"]



class cobro:
    def __init__(self, id, nombre, wallet, comision, celular, pago, status ):
        self.id = id
        self.nombre = nombre
        self.wallet = wallet
        self.comision = comision
        self.celular = celular
        self.pago = pago
        self.status = status

def sendTwilioCobros(cliente_var, monto_var, fecha_var):
    account_sid = "AC7567d2dee446b304d2e30b9f277656a6"
    auth_token  = "3213ad8991dc85cb5254d856943d384e"
    wallet_pmc = "0x34fa7b1abfd6e397de3c39934635fedb925eea4d"
    red = "BEP 20"
    client = ClientTwilio(account_sid, auth_token)
    message = client.messages \
        .create(
             from_='whatsapp:+16625025249',
             body=f"Hola! Queremos comentarte lo siguiente:\nSe ha encontrado un pago en Blockchain y acreditado en sistema PMC.\nCliente: {cliente_var}\nRed: {red}\nMonto: {monto_var}\nFecha: {fecha_var}\n\nSaludos!",
             to='whatsapp:+5491121708911'
         )
    message = client.messages \
        .create(
             from_='whatsapp:+16625025249',
             body=f"Hola! Queremos comentarte lo siguiente:\nSe ha encontrado un pago en Blockchain y acreditado en sistema PMC.\nCliente: {cliente_var}\nRed: {red}\nMonto: {monto_var}\nFecha: {fecha_var}\n\nSaludos!",
             to='whatsapp:+5491130252911'
         )


def getCell(sheet, worksheet, string):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('/home/PMC/AutomatismosPMC/pilarminingco-c11e8da70b2f.json', scope)
    client = gspread.authorize(creds)
    work_sheet = client.open(sheet)
    sheet_instance = work_sheet.worksheet(worksheet)
    cell = sheet_instance.find(string)
    return (cell.row, cell.col)

def getMonthRow(sheet, worksheet, month):
    string = month + " eth"
    print (string)
    row, col = getCell(sheet, worksheet, string)
    return col


def getSheetsDataFrame(sheet, worksheet):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('/home/PMC/AutomatismosPMC/pilarminingco-c11e8da70b2f.json', scope)
    client = gspread.authorize(creds)
    work_sheet = client.open(sheet)
    sheet_instance = work_sheet.worksheet(worksheet)
    records_data = sheet_instance.get_all_records()
    return (pd.DataFrame.from_dict(records_data))

def telegram_message(message):
    headers_telegram = {"Content-Type": "application/x-www-form-urlencoded"}
    endpoint_telegram = "https://api.telegram.org/bot1956376371:AAFgQ8zc6HLwRReXnzdfN7csz_-iEl8E1oY/sendMessage"
    mensaje_telegram = {'chat_id': '-791201780', 'text': 'Problemas en RIG'}
    mensaje_telegram["text"] = message
    response = requests.post(endpoint_telegram, headers=headers_telegram, data=mensaje_telegram).json()
    if (response["ok"] == False):
        print("Voy a esperar xq se bloquio telegram")
        time.sleep(response["parameters"]["retry_after"]+5)
        response = requests.post(endpoint_telegram, headers=headers_telegram, data=mensaje_telegram).json()
    return response


def colorCell(documento, hoja, cell, red, green, blue):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('/home/PMC/AutomatismosPMC/pilarminingco-c11e8da70b2f.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open(documento)
    sheet_instance = sheet.worksheet(hoja)
    sheet_instance.format(cell, {'backgroundColor': {'red': red, 'green': green, 'blue': blue}})



def getPaymentsList(sheets):
    list_payments = []
    for id in sheets["id"]:
        endpoint_sheets = "https://sheets.googleapis.com/v4/spreadsheets/1vxTxT2Cxon69A2FT_hg9xFhVlLdiGqwSHdmwi20GltM?includeGridData=true&ranges="+str(month_letter_col)+str(id)+"&key=AIzaSyBTXGrTeo52t01avYbI4lXOcI00zvKVTxs"
        response = requests.get(endpoint_sheets).json()
        month = str(str(tuple_months[mesInicio-1]) + str(" eth"))
        try:
            if "red" in response["sheets"][0]["data"][0]["rowData"][0]["values"][0]["userEnteredFormat"]["backgroundColor"]:
                list_payments.append(cobro(sheets["id"][id-2],sheets["nombre"][id-2],sheets["wallet"][id-2],sheets["comision"][id-2],sheets["celular"][id-2],sheets[month][id-2],0))
            else:
                list_payments.append(cobro(sheets["id"][id-2],sheets["nombre"][id-2],sheets["wallet"][id-2],sheets["comision"][id-2],sheets["celular"][id-2],sheets[month][id-2],1))
        except Exception as e:
            print("Endpoint_sheets: "+endpoint_sheets)
    return list_payments

monitor.ping(state='run')

month_col = getMonthRow("Cobros - Autom", "Cobros", tuple_months[mesInicio-1])
print(month_col)
month_letter_col = tuple_excel_columns[month_col-1]

#print("--------------------------")
list_pending_payments = getPaymentsList(getSheetsDataFrame("Cobros - Autom","Cobros"))



endpoint_etherscan = "https://api.etherscan.io/api?module=account&action=txlist&address="+wallet_pmc+"&startblock=0&endblock=99999999&page=1&offset=200&sort=desc&apikey="+api_key
response_etherscan = requests.request("GET", endpoint_etherscan).json()

eth_deposits = (client.get_deposit_history(coin='ETH'))
#print(eth_deposits)
for deposit in eth_deposits:
    if inicioUnixPeriodoFacturacion <= int(deposit["insertTime"]/1000) <= finUnixPeriodoFacturacion:
        print(str(deposit["amount"])[:9])
        for pago in list_pending_payments:
            if pago.status == 0:
                if str(pago.pago) in str(deposit["amount"])[:9]:
                    colorCell("Cobros - Autom", "Cobros", month_letter_col+str(pago.id+1), 0,0.9,0)
                    sendTwilioCobros(pago.nombre, pago.pago, datetime.utcfromtimestamp(int(deposit["insertTime"])/1000).strftime('%d-%m-%Y %H:%M'))
                    telegram_message("Pago encontrado en Blockchain. \nCliente: "+pago.nombre+" \nRed: "+str(deposit["network"])+"\nMonto: "+str(deposit["amount"])[:9]+ "\nFecha: "+ datetime.utcfromtimestamp(int(deposit["insertTime"])/1000).strftime('%d-%m-%Y %H:%M'))
monitor.ping(state='complete')

from flask import Flask, jsonify, request
import pdfkit;
import os
import base64
import time
from decimal import Decimal, getcontext
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from barcode import Code128
from flask_cors import CORS

app=Flask(__name__)

CORS(app)
@app.route("/invoice", methods=["POST"])
def root():
    data = request.get_json()
    #invoicePdfHtml = open("/home/codelinesw/Documents/Celsia/OpenSGC/ApiGenerateInvoice/TemplateInvoiceHtml/Page1.html")
    pathFile = f'{os.getcwd()}/index.html'
    invoicePdfHtml = open(pathFile, encoding="utf8")
    contentTemplate = invoicePdfHtml.read()

    codigo=str(data["code"])
    direccion=data["address"]
    listaConceptos=data["listaConceptos"]
    total=str(data["totalConceptos"])
    _concepto=""
    
    for _item in listaConceptos:
        _concepto += "<tr>"
        _concepto += f"<td style='padding:10px'>{str(_item["concept"])}</td>"
        _concepto += f"<td style='padding:10px'>${str(_item["amount"])}</td>"
        _concepto +="</tr>"    
    contentTemplate = contentTemplate.replace("{listaConceptos}", _concepto)
    contentTemplate = contentTemplate.replace("{total}", total)
    contentTemplate=contentTemplate.replace("{code}",codigo)
    contentTemplate=contentTemplate.replace("{address}",direccion)

    
    labels = data["datosGrafica"]["labels"]
    sizes = data["datosGrafica"]["data"]
    colors = ['#FF812D', '#F60041', '#FFC300','#00C08C']



    fig, ax = plt.subplots()
    ax.pie(sizes, colors=colors, startangle=90, wedgeprops={'width': 0.3})


    centre_circle = plt.Circle((0,0), 0.70, color='white', fc='white')
    fig.gca().add_artist(centre_circle)


    ax.axis('equal')  

   
    ax.legend(labels, loc="center left", bbox_to_anchor=(1.05, 0.5), title="Conceptos")
    fig.tight_layout()
    
    time.sleep(2)
    # fileNameImage = 'image-example.png'
    #plt.show()
    plt.savefig(f"imagen.png", format="png") 
    #f"image-example_{data['datosFactura']['fechaEmision']}_{str(data['cabecera']['nic'])}.png"
    plt.close()
    contentTemplate = contentTemplate.replace("{image-graphic}",f"imagen.png")


    
    _conceptofin=""

    if(data["financiamiento"] is not None and len(data["financiamiento"]) > 0):
        finan=data["financiamiento"]
        for _it in finan:
            _conceptofin += "<tr>"
            _conceptofin += f"<td style='padding:10px'>{str(_it["concept"])}</td>"
            _conceptofin += f"<td style='padding:10px'>{str(_it["status"])}</td>"
            _conceptofin += f"<td style='padding:10px'>{str(_it["creationDate"])}</td>"
            _conceptofin += f"<td style='padding:10px'>{str(_it["totalFinanciado"])}</td>"
            _conceptofin += f"<td style='padding:10px'>{str(_it["totalCuotas"])}</td>"
            _conceptofin += f"<td style='padding:10px'>{str(_it["ownerName"])}</td>"
            _conceptofin +="</tr>"    
        contentTemplate = contentTemplate.replace("{financiamiento}", _conceptofin)
    else:
        _conceptofin += f"<tr ><td class='no-data-row' colspan='7' style='padding: 16px; text-align: center; '>No tienes pagos ni deudas pendientes relacionadas con financiaciones.</td></tr>"
        contentTemplate = contentTemplate.replace("{financiamiento}", _conceptofin)
    


    file_name = f"EstadoDeCuenta.html"
    with open(file_name, 'w',encoding="utf8") as file:
        file.write(contentTemplate)
    options = {
      "enable-local-file-access": "",
      "page-width": "1080px",
      "page-height": "1920px",
    }
    fileNamePdf = f"EstadoDeCuenta.pdf"
    pdfkit.from_file(file_name, fileNamePdf, options=options)
    encodedPdf = ""
    with open(fileNamePdf, "rb") as pdf_file:
        encodedPdf = base64.b64encode(pdf_file.read()).decode('utf-8')
    encodedPdf = encodedPdf.replace("'","")
    apiResponse = {
      "fileName": fileNamePdf,
      "base64": encodedPdf
    }
    return jsonify(apiResponse), 201


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000,debug=True, threaded=False)
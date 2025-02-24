import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import base64
import io
import os
import pandas as pd
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from process_dna import read_dna_file, connect_to_database, assemble_report_data, generate_pdf

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout of the app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Genomic Report Generator"), className="mb-4")
    ]),
    dbc.Row([
        dbc.Col(dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select a Genomic File')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=False
        ), width=6),
        dbc.Col(html.Div(id='output-data-upload'), width=6)
    ]),
    dbc.Row([
        dbc.Col(dbc.Button("Submit", id="submit-button", color="primary", className="mr-2"), width=12)
    ]),
    dbc.Row([
        dbc.Col(dcc.Loading(
            id="loading-spinner",
            type="default",
            children=html.Div(id="loading-output")
        ), width=12)
    ]),
    dbc.Row([
        dbc.Col(html.A("Download Report", id="download-link", href="",
                target="_blank", className="btn btn-primary", style={"display": "none"}), width=12)
    ])
])

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'txt' in filename:
            # Assume that the user uploaded a text file
            snps = read_dna_file(io.StringIO(decoded.decode('utf-8')))
            return snps
        else:
            return None
    except Exception as e:
        print(e)
        return None

@app.callback(
    Output('output-data-upload', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_output(contents, filename):
    if contents is not None:
        snps = parse_contents(contents, filename)
        if snps is not None:
            return html.Div([
                html.H5(filename),
                html.H6("File uploaded successfully.")
            ])
        else:
            return html.Div([
                html.H5(filename),
                html.H6("There was an error processing the file.")
            ])
    return ""

@app.callback(
    Output('loading-output', 'children'),
    Output('download-link', 'href'),
    Output('download-link', 'style'),
    Input('submit-button', 'n_clicks'),
    State('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def generate_report(n_clicks, contents, filename):
    if n_clicks is not None and contents is not None:
        snps = parse_contents(contents, filename)
        if snps is not None:
            # Connect to the database and generate the report
            engine = connect_to_database()
            with engine.connect() as conn:
                report_data = assemble_report_data(conn, snps)
                output_pdf = "genomic_report.pdf"
                generate_pdf(report_data, output_pdf, conn)
                return html.Div([
                    html.H6("Report generated successfully.")
                ]), f"/download/{output_pdf}", {"display": "block"}
        else:
            return html.Div([
                html.H6("There was an error processing the file.")
            ]), "", {"display": "none"}
    return "", "", {"display": "none"}

@app.server.route('/download/<path:filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run_server(debug=True)
import tempfile
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
import logging


if os.environ.get('DEBUG',False):
    from dotenv import load_dotenv
    load_dotenv()
    
    
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d',
    handlers=[
        logging.StreamHandler()
    ]
)


# Define the absolute path for reports
absolute_report_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'reports'))
os.makedirs(absolute_report_path, exist_ok=True)

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # Expose the server variable for GCP
logging.info(
    f"{os.environ['INSTANCE_CONNECTION_NAME']}, {os.environ['DB_USER']}, {os.environ['DB_PASS']}, {os.environ['DB_NAME']}")

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
        dbc.Col(dcc.Loading(
            id="loading-upload",
            type="default",
            children=html.Div(id='output-data-upload')
        ), width=6)
    ]),
    dbc.Row([
        dbc.Col(dbc.Checkbox(id='test-checkbox', label='Generate Dummy Report', className="mr-2"), width=12)
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


def dummy_generate_pdf(output_path):
    """
    Creates a dummy PDF with Lorem Ipsum text for testing purposes.
    """
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "Lorem Ipsum Report")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 75, "A dummy report for testing purposes")

    lorem_ipsum_text = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
        "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. "
        "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
        "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    )

    c.setFont("Helvetica", 10)
    txt_obj = c.beginText(50, height - 110)
    for line in lorem_ipsum_text.split('. '):
        txt_obj.textLine(line.strip() + '.')
    c.drawText(txt_obj)

    c.save()

def parse_contents(contents, filename):
    logging.info(f"Parsing contents of file: {filename}")
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'txt' in filename:
            # Assume that the user uploaded a text file
            with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as temp_file:
                temp_file.write(decoded.decode('utf-8'))
                temp_file_path = temp_file.name
            snps = read_dna_file(temp_file_path)
            logging.info("File parsed successfully.")
            return snps
        else:
            logging.error("Unsupported file type.")
            return None
    except Exception as e:
        logging.error(f"Error parsing file: {e}")
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
            logging.info(f"File {filename} uploaded and processed successfully.")
            return html.Div([
                html.H5(filename),
                html.H6("File uploaded successfully.")
            ])
        else:
            logging.error(f"Error processing file {filename}.")
            return html.Div([
                html.H5(filename),
                html.H6("There was an error processing the file.")
            ])
    return html.Div()


@app.callback(
    Output('loading-output', 'children'),
    Output('download-link', 'href'),
    Output('download-link', 'style'),
    Input('submit-button', 'n_clicks'),
    State('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('test-checkbox', 'value')
)
def generate_report(n_clicks, contents, filename, test_checkbox):
    if n_clicks is not None and contents is not None:
        logging.info("Submit button clicked.")
        snps = parse_contents(contents, filename)
        if snps is not None:
            output_pdf = os.path.join(absolute_report_path, "genomic_report.pdf")
            if test_checkbox:
                dummy_generate_pdf(output_pdf)
            else:
                # Connect to the database and generate the report
                logging.info("Connecting to the database.")
                engine = connect_to_database()
                with engine.connect() as conn:
                    logging.info("Assembling report data.")
                    report_data = assemble_report_data(conn, snps)
                    logging.info(f"Output PDF path: {output_pdf}")
                    logging.info("Generating PDF report.")
                    generate_pdf(report_data, output_pdf, conn)
                    logging.info("Report generated successfully.")
            return html.Div([
                html.H6("Report generated successfully.")
            ]), f"/download/{os.path.basename(output_pdf)}", {"display": "block"}
        else:
            logging.error("Error processing the file for report generation.")
            return html.Div([
                html.H6("There was an error processing the file.")
            ]), "", {"display": "none"}
    return "", "", {"display": "none"}


@app.server.route('/download/<path:filename>')
def download_file(filename):
    file_path = os.path.join(absolute_report_path, filename)
    logging.info(f"Downloading file: {file_path}")
    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    app.run_server(debug=os.environ.get('DEBUG',False), host=os.environ.get('HOST','0.0.0.0'), port=int(os.environ.get('PORT', 8080)))
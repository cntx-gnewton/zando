import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

from app.core.config import settings

logger = logging.getLogger(__name__)

class PDFService:
    """
    Service for generating PDF reports from analysis data.
    """
    
    @staticmethod
    async def generate_pdf_report(report_data: Dict[str, Any], output_path: str, db: Optional[AsyncSession] = None) -> str:
        """
        Creates a PDF summarizing the relevant SNPs and recommended ingredients.
        
        Args:
            report_data: Complete analysis data
            output_path: Path to save the PDF
            db: Database session (for dynamic summaries)
            
        Returns:
            Path to the generated PDF
        """
        logger.info(f"Generating standard PDF report to {output_path}")
        
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 50, "Your Genetic Skincare Report")
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 75, "A story written by your DNA")

        # Get or create summary text
        summary_text = report_data.get("summary", 
            "Your genes reveal how your skin naturally behaves. This report guides you on how to optimize your skincare based on your genetics.")
       
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 110, "Summary: The Story of Your Skin")
        c.setFont("Helvetica", 10)
       
        txt_obj = c.beginText(50, height - 130)
        for line in summary_text.split('\n'):
            txt_obj.textLine(line.strip())
        c.drawText(txt_obj)

        y = height - 400
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Your Genetic Mutations")
        y -= 20

        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Gene")
        c.drawString(120, y, "rsID")
        c.drawString(190, y, "Alleles")
        c.drawString(250, y, "Impact")
        y -= 15
        c.setFont("Helvetica", 10)

        for mutation in report_data.get("mutations", []):
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 10)
               
            line = f"{mutation['gene']}   {mutation['rsid']}   {mutation['allele1']}/{mutation['allele2']}   {mutation['effect']}"
            c.drawString(50, y, line)
            y -= 15

        y -= 20
        if y < 100:
            c.showPage()
            y = height - 50
           
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Ingredient Recommendations")
        y -= 20

        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Prioritize These:")
        y -= 15
        c.setFont("Helvetica", 10)
       
        seen_ingredients = set()
        unique_prioritize = []
        
        for ingr in report_data.get("ingredient_recommendations", {}).get("prioritize", []):
            if ingr['ingredient_name'] not in seen_ingredients:
                seen_ingredients.add(ingr['ingredient_name'])
                unique_prioritize.append(ingr)

        for ingr in unique_prioritize:
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 10)
               
            line = f"{ingr['ingredient_name']}: {ingr['benefit_mechanism']}"
            c.drawString(60, y, line)
            y -= 12

        y -= 15
        if y < 100:
            c.showPage()
            y = height - 50
           
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Approach With Caution:")
        y -= 15
        c.setFont("Helvetica", 10)

        seen_cautions = set()
        unique_cautions = []
        
        for ingr in report_data.get("ingredient_recommendations", {}).get("caution", []):
            if ingr['ingredient_name'] not in seen_cautions:
                seen_cautions.add(ingr['ingredient_name'])
                unique_cautions.append(ingr)

        for ingr in unique_cautions:
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 10)
               
            line = f"{ingr['ingredient_name']}: {ingr['risk_mechanism']}"
            c.drawString(60, y, line)
            y -= 12

        c.save()
        
        logger.info(f"PDF report generated successfully: {output_path}")
        return output_path
    
    @staticmethod
    def markdown_to_pdf(markdown_content: str, output_path: str) -> str:
        """
        Convert markdown content to a PDF file using ReportLab.
        
        Args:
            markdown_content: Markdown formatted text
            output_path: Path to save the PDF
            
        Returns:
            Path to the generated PDF file
        """
        logger.info(f"Converting markdown to PDF: {output_path}")
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72, 
            leftMargin=72,
            topMargin=72, 
            bottomMargin=72
        )
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Create custom styles with unique names
        custom_heading1 = ParagraphStyle(
            name='CustomHeading1',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=12
        )
        
        custom_heading2 = ParagraphStyle(
            name='CustomHeading2',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=10,
            spaceBefore=12
        )
        
        custom_heading3 = ParagraphStyle(
            name='CustomHeading3',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=10
        )
        
        custom_body = ParagraphStyle(
            name='CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            leading=14
        )
        
        custom_list_item = ParagraphStyle(
            name='CustomListItem',
            parent=styles['BodyText'],
            fontSize=11,
            leading=14,
            leftIndent=20
        )
        
        # Add the custom styles to the stylesheet
        styles.add(custom_heading1)
        styles.add(custom_heading2)
        styles.add(custom_heading3)
        styles.add(custom_body)
        styles.add(custom_list_item)
        
        # Split markdown into sections
        sections = markdown_content.split('\n## ')
        
        # Prepare elements for the PDF
        elements = []
        
        # Process the title section
        title_section = sections[0].strip()
        title_lines = title_section.split('\n')
        
        # Main title
        title = title_lines[0].replace('# ', '')
        elements.append(Paragraph(title, styles['CustomHeading1']))
        elements.append(Spacer(1, 12))
        
        # Subtitle if present
        if len(title_lines) > 1:
            subtitle = title_lines[1].replace('## ', '')
            elements.append(Paragraph(subtitle, styles['CustomHeading3']))
            elements.append(Spacer(1, 12))
        
        # Process other sections
        for i, section in enumerate(sections[1:], 1):
            section_lines = section.split('\n')
            section_title = section_lines[0]
            section_content = '\n'.join(section_lines[1:])
            
            # Add section header
            elements.append(Paragraph(section_title, styles['CustomHeading2']))
            elements.append(Spacer(1, 6))
            
            # Process content based on section type
            if "Your Genetic Mutations" in section_title:
                # Process table
                table_lines = [line.strip() for line in section_content.split('\n') if '|' in line and line.strip()]
                if len(table_lines) >= 2:  # Header and separator line
                    header = table_lines[0]
                    data_rows = table_lines[2:]  # Skip separator line
                    
                    # Parse header
                    headers = [cell.strip() for cell in header.split('|')[1:-1]]
                    
                    # Create table data
                    table_data = [headers]
                    for row in data_rows:
                        cells = [cell.strip() for cell in row.split('|')[1:-1]]
                        table_data.append(cells)
                    
                    # Create table
                    table = Table(table_data, repeatRows=1)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ]))
                    
                    elements.append(table)
                    elements.append(Spacer(1, 12))
                
            else:
                # Process regular paragraphs and lists
                paragraphs = section_content.split('\n\n')
                for paragraph in paragraphs:
                    if paragraph.strip():
                        # Check if it's a header section
                        if paragraph.startswith('### '):
                            header_text = paragraph.replace('### ', '')
                            elements.append(Paragraph(header_text, styles['CustomHeading3']))
                        # Check if it's a list
                        elif paragraph.startswith('- '):
                            list_items = paragraph.split('\n- ')
                            for item in list_items:
                                if item.strip():
                                    # Replace markdown bold with HTML bold
                                    item = item.replace('**', '<b>', 1).replace('**', '</b>', 1)
                                    elements.append(Paragraph(f"• {item.strip()}", styles['CustomListItem']))
                                    elements.append(Spacer(1, 4))
                        else:
                            # Regular paragraph
                            elements.append(Paragraph(paragraph, styles['CustomBody']))
                            elements.append(Spacer(1, 8))
        
        # Build the PDF
        doc.build(elements)
        
        logger.info(f"Markdown PDF report generated successfully: {output_path}")
        return output_path
    
    @staticmethod
    def generate_markdown(report_data: Dict[str, Any], output_path: str) -> str:
        """
        Creates a markdown-formatted report content.
        
        Args:
            report_data: Complete analysis data
            output_path: Path to save the markdown (for reference)
            
        Returns:
            Markdown content as string
        """
        logger.info(f"Generating markdown report content")
        
        # Get or create summary text
        summary_text = report_data.get("summary", 
            "Your genes reveal how your skin naturally behaves. This report guides you on how to optimize your skincare based on your genetics.")
        
        # Build the markdown content
        markdown_content = f"""# Your Genetic Skincare Report
## A story written by your DNA

## Summary: The Story of Your Skin
{summary_text}

## Your Genetic Mutations

| Gene | rsID | Alleles | Impact |
|------|------|---------|--------|
"""
        
        # Add mutation rows
        for mutation in report_data.get("mutations", []):
            alleles = f"{mutation['allele1']}/{mutation['allele2']}"
            markdown_content += f"| {mutation['gene']} | {mutation['rsid']} | {alleles} | {mutation['effect']} |\n"
        
        # Add characteristics section if available
        any_characteristics = False
        for mutation in report_data.get("mutations", []):
            if mutation.get('characteristics') and len(mutation['characteristics']) > 0:
                any_characteristics = True
                break
        
        if any_characteristics:
            markdown_content += "\n## Skin Characteristics Affected\n\n"
            markdown_content += "\n"
            for mutation in report_data.get("mutations", []):
                if mutation.get('characteristics') and len(mutation['characteristics']) > 0:
                    markdown_content += f"### {mutation['gene']} ({mutation.get('category', 'Unknown')})\n\n"
                    for char in mutation['characteristics']:
                        effect = char.get('effect_direction', 'Affects')
                        markdown_content += f"- **{char['name']}**: {effect} - {char['description']}\n"
                    markdown_content += "\n"
        
        # Add ingredient recommendations
        markdown_content += "\n## Ingredient Recommendations\n\n"
        
        # Prioritized ingredients
        markdown_content += "\n### Prioritize These\n\n"
        
        seen_ingredients = set()
        unique_prioritize = []
        
        for ingr in report_data.get("ingredient_recommendations", {}).get("prioritize", []):
            if ingr['ingredient_name'] not in seen_ingredients:
                seen_ingredients.add(ingr['ingredient_name'])
                unique_prioritize.append(ingr)
        
        for ingr in unique_prioritize:
            markdown_content += f"- **{ingr['ingredient_name']}**: {ingr['benefit_mechanism']}\n"
        
        # Cautionary ingredients
        markdown_content += "\n### Approach With Caution\n\n"
        
        seen_cautions = set()
        unique_cautions = []
        
        for ingr in report_data.get("ingredient_recommendations", {}).get("caution", []):
            if ingr['ingredient_name'] not in seen_cautions:
                seen_cautions.add(ingr['ingredient_name'])
                unique_cautions.append(ingr)
        
        for ingr in unique_cautions:
            markdown_content += f"- **{ingr['ingredient_name']}**: {ingr['risk_mechanism']}\n"
        
        # Save markdown content to file if path provided
        if output_path:
            md_path = output_path.replace('.pdf', '.md')
            with open(md_path, 'w') as f:
                f.write(markdown_content)
        
        return markdown_content
    
    @staticmethod
    async def generate_markdown_report(report_data: Dict[str, Any], output_path: str, db: Optional[AsyncSession] = None) -> str:
        """
        Creates a markdown-formatted report and converts it to PDF.
        
        Args:
            report_data: Complete analysis data
            output_path: Path to save the PDF
            db: Database session (for dynamic summaries)
            
        Returns:
            Path to the generated PDF
        """
        # Generate markdown content
        markdown_content = PDFService.generate_markdown(report_data, output_path)
        
        # Convert markdown to PDF
        return PDFService.markdown_to_pdf(markdown_content, output_path)
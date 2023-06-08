import yaml
from reportlab.pdfgen import canvas
import textwrap

def yaml_to_pdf(yaml_file_path, pdf_file_path):
    # Open the yaml file
    with open(yaml_file_path, 'r') as yaml_file:
        # Load yaml content
        yaml_content = yaml.safe_load(yaml_file)

    # Initialize pdf file
    pdf = canvas.Canvas(pdf_file_path)

    # Set initial coordinates
    x = 20  # margin from the left
    y = 800  # start from the top

    # Set font size
    pdf.setFont("Helvetica", 10)

    for section, data in yaml_content.items():
        pdf.drawString(x, y, f"{section}:")
        y -= 15

        for key, value in data.items():
            line = f"{key}: {value}"
            # Wrap the text if the line is too long
            lines = textwrap.wrap(line, 70) # adjust the number according to the width of your pdf page
            for line in lines:
                pdf.drawString(x+10, y, line)
                y -= 15

                # Check if page is filled
                if y < 30:
                    pdf.showPage()
                    y = 800

    # Save the pdf file
    pdf.save()


# Use the function
yaml_to_pdf("/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/make_input_data/parameters.yaml",
            "/Users/tobiassjoli/Documents/Master/Appendix/parameters.png")

from fpdf import FPDF
from PIL import Image
import io

# --- Constants ---
PRIMARY_COLOR = (70, 130, 180)  # SteelBlue
SECONDARY_COLOR = (220, 220, 220) # Gainsboro

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_fill_color(*PRIMARY_COLOR)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, 'Rapport de Diagnostic Médical', 1, 1, 'C', fill=True)
        self.set_text_color(0, 0, 0) # Reset text color
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        self.cell(0, 10, 'Avertissement: Ce rapport ne remplace pas un avis médical professionnel.', 0, 0, 'R')

    def section_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(*SECONDARY_COLOR)
        self.cell(0, 8, title, 0, 1, 'L', fill=True)
        self.ln(4)

    def draw_line(self):
        self.set_draw_color(*PRIMARY_COLOR)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(5)

def generate_pdf_report(analysis_data):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 11)
    pdf.set_auto_page_break(auto=True, margin=15)

    page_width = pdf.w - pdf.l_margin - pdf.r_margin

    # --- Timestamp ---
    timestamp = analysis_data.get('timestamp')
    if timestamp:
        pdf.set_font('Arial', 'I', 9)
        pdf.cell(0, 8, f"Date de l'analyse : {timestamp.strftime('%d/%m/%Y %H:%M:%S')}", 0, 1, 'R')
        pdf.set_font('Arial', '', 11)

    pdf.ln(5)

    # --- Radiography Analysis ---
    if analysis_data['type'] == 'Analyse Radiographique':
        pdf.section_title("Rapport d'Analyse Radiographique")

        # --- Main Results & Image ---
        if 'image' in analysis_data:
            # Save image to buffer to get its properties and display it
            img_buffer = io.BytesIO()
            analysis_data['image'].save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            with Image.open(img_buffer) as img:
                width, height = img.size
            
            aspect_ratio = height / width
            image_w = 80 # Define a fixed width for the image
            image_h = image_w * aspect_ratio
            
            # Draw image on the left
            img_y_pos = pdf.get_y()
            pdf.image(img_buffer, x=pdf.l_margin, y=img_y_pos, w=image_w, h=image_h, type='PNG')
        else:
            image_h = 0

        # --- Results on the right ---
        results_x_pos = pdf.l_margin + image_w + 10 if 'image' in analysis_data else pdf.l_margin
        pdf.set_xy(results_x_pos, img_y_pos)
        
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 7, "Diagnostic Principal :")
        pdf.ln()

        pdf.set_font('Arial', '', 11)
        predicted_disease = analysis_data.get('predicted_disease', 'N/A')
        pdf.multi_cell(page_width - results_x_pos, 7, f"Maladie Prédite : {predicted_disease}")
        pdf.set_x(results_x_pos)
        pdf.multi_cell(page_width - results_x_pos, 7, f"Probabilité : {analysis_data.get('prediction_probability', 0):.2%}")
        pdf.ln(5)
        
        # Move cursor down past the image and results section
        pdf.set_y(img_y_pos + image_h + 10)

        # --- Detailed Probabilities Table ---
        if 'all_predictions' in analysis_data:
            pdf.draw_line()
            pdf.section_title("Détail des Probabilités par Maladie")
            
            # Table Header
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(page_width * 0.6, 8, "Maladie", 1, 0, 'C')
            pdf.cell(page_width * 0.4, 8, "Probabilité", 1, 1, 'C')
            
            # Table Body
            pdf.set_font('Arial', '', 10)
            DISEASE_MAP = {
                0: "Atelectasis", 1: "COVID19", 2: "Cardiomegaly", 3: "Consolidation",
                4: "Edema", 5: "Effusion", 6: "Emphysema", 7: "Fibrosis", 8:"Image_Nom_radiographique",
                9: "Infiltration", 10: "Mass", 11: "Nodule", 12: "Normal",
                13: "Pleural Thickening", 14: "Pneumonia", 15: "Pneumothorax", 16: "Tuberculosis"
            }
            
            # Sort predictions for better readability
            predictions_with_names = sorted(
                [(DISEASE_MAP.get(i, f"Unknown {i}"), prob) for i, prob in enumerate(analysis_data['all_predictions'])],
                key=lambda item: item[1],
                reverse=True
            )

            for disease_name, prob in predictions_with_names:
                pdf.cell(page_width * 0.6, 8, disease_name, 1)
                pdf.cell(page_width * 0.4, 8, f"{prob:.2%}", 1, 1, 'R')

    # --- Symptom Analysis ---
    elif analysis_data['type'] == 'Analyse de Symptômes':
        pdf.section_title("Rapport d'Analyse de Symptômes")

        pdf.set_font('Arial', 'B', 11)
        pdf.cell(page_width, 8, "Informations du patient :", 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.multi_cell(page_width, 7, f"Âge : {analysis_data['age']} ans")
        pdf.multi_cell(page_width, 7, f"Poids : {analysis_data['weight']} kg")
        pdf.ln(5)

        pdf.draw_line()
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(page_width, 8, "Symptômes décrits :", 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.multi_cell(page_width, 7, analysis_data['symptoms'])
        pdf.ln(5)

        pdf.draw_line()
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(page_width, 8, "Recommandation :", 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.multi_cell(page_width, 7, analysis_data['analysis']['recommendation'])

    elif analysis_data['type'] == 'heart_disease_prediction':
        pdf.section_title("Rapport de Prédiction de Maladies Cardiaques")

        pdf.set_font('Arial', 'B', 11)
        pdf.cell(page_width, 8, "Informations saisies :", 0, 1)
        pdf.set_font('Arial', '', 11)
        for feature, value in analysis_data['input_features'].items():
            pdf.multi_cell(page_width, 7, f"- {feature.replace('_', ' ').capitalize()} : {value}")
        pdf.ln(5)

        pdf.draw_line()
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(page_width, 8, "Résultat de la Prédiction :", 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.multi_cell(page_width, 7, analysis_data['result_message'])
        pdf.multi_cell(page_width, 7, f"Probabilité de maladie cardiaque : {analysis_data['prediction_probability_positive']:.2%}")
        pdf.multi_cell(page_width, 7, f"Probabilité de non-maladie cardiaque : {analysis_data['prediction_probability_negative']:.2%}")

    return bytes(pdf.output())
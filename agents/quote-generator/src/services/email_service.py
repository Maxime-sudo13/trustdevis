"""
Service d'envoi d'emails
"""

from typing import Optional
from datetime import datetime
from src.models.quote import GeneratedQuote, EmailRequest, EmailResponse


class EmailService:
    """Service d'envoi d'emails pour les devis"""
    
    def __init__(self):
        self.sent_emails = []
    
    def generate_email_content(self, quote: GeneratedQuote, include_comparison: bool = True) -> str:
        """Génère le contenu HTML de l'email"""
        
        variants = quote.variants
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: #2563EB; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; max-width: 800px; margin: 0 auto; }}
                .quote-box {{ border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; }}
                .economy {{ border-left: 4px solid #10B981; }}
                .standard {{ border-left: 4px solid #3B82F6; }}
                .premium {{ border-left: 4px solid #F59E0B; }}
                .price {{ font-size: 24px; font-weight: bold; color: #2563EB; }}
                .recommendation {{ background: #EFF6FF; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background: #F3F4F6; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏠 Vos estimations de travaux - TrustDevis</h1>
                <p>Devis généré le {quote.created_at.strftime('%d/%m/%Y')}</p>
            </div>
            
            <div class="content">
                <h2>Type de travaux : {quote.work_description.work_type.value.title()}</h2>
                <p><strong>Description :</strong> {quote.work_description.description}</p>
                
                <h3>📊 Nos 3 estimations</h3>
                
                <div class="quote-box economy">
                    <h4>💚 Solution Économique</h4>
                    <p class="price">{variants['economique'].cost_breakdown.total_ttc:.2f} € TTC</p>
                    <p>Durée : {variants['economique'].timeline.days_min}-{variants['economique'].timeline.days_max} jours</p>
                    <p>Garantie : {variants['economique'].warranty_years} an</p>
                </div>
                
                <div class="quote-box standard">
                    <h4>💙 Solution Standard (Recommandée)</h4>
                    <p class="price">{variants['standard'].cost_breakdown.total_ttc:.2f} € TTC</p>
                    <p>Durée : {variants['standard'].timeline.days_min}-{variants['standard'].timeline.days_max} jours</p>
                    <p>Garantie : {variants['standard'].warranty_years} ans</p>
                </div>
                
                <div class="quote-box premium">
                    <h4>💛 Solution Premium</h4>
                    <p class="price">{variants['premium'].cost_breakdown.total_ttc:.2f} € TTC</p>
                    <p>Durée : {variants['premium'].timeline.days_min}-{variants['premium'].timeline.days_max} jours</p>
                    <p>Garantie : {variants['premium'].warranty_years} ans</p>
                </div>
        """
        
        if include_comparison:
            html += f"""
                <div class="recommendation">
                    <h3>⭐ Notre recommandation</h3>
                    <p><strong>{quote.comparison.value_for_money_recommendation.value.title()}</strong></p>
                    <p>{quote.comparison.explanation}</p>
                </div>
            """
        
        html += """
                <div class="footer">
                    <p>Ces estimations sont fournies à titre indicatif par TrustDevis.</p>
                    <p>Les prix réels peuvent varier selon les artisans et les spécificités de votre chantier.</p>
                    <p><a href="https://trustdevis.com">trustdevis.com</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_quote_email(self, request: EmailRequest, quote: GeneratedQuote) -> EmailResponse:
        """Envoie le devis par email"""
        
        try:
            # Simuler l'envoi (à remplacer par vrai service SMTP)
            content = self.generate_email_content(quote, request.include_comparison)
            
            # Log de l'envoi
            self.sent_emails.append({
                "quote_id": request.quote_id,
                "email": request.email,
                "sent_at": datetime.utcnow(),
                "content_length": len(content)
            })
            
            return EmailResponse(
                success=True,
                message=f"Devis envoyé avec succès à {request.email}",
                sent_at=datetime.utcnow()
            )
            
        except Exception as e:
            return EmailResponse(
                success=False,
                message=f"Erreur lors de l'envoi: {str(e)}",
                sent_at=None
            )
    
    def generate_text_version(self, quote: GeneratedQuote) -> str:
        """Génère une version texte de l'email"""
        
        variants = quote.variants
        
        text = f"""
VOS ESTIMATIONS DE TRAVAUX - TRUSTDEVIS
========================================

Type de travaux : {quote.work_description.work_type.value.title()}
Description : {quote.work_description.description}

NOS 3 ESTIMATIONS :
-------------------

SOLUTION ÉCONOMIQUE : {variants['economique'].cost_breakdown.total_ttc:.2f} € TTC
- Durée : {variants['economique'].timeline.days_min}-{variants['economique'].timeline.days_max} jours
- Garantie : {variants['economique'].warranty_years} an

SOLUTION STANDARD (Recommandée) : {variants['standard'].cost_breakdown.total_ttc:.2f} € TTC
- Durée : {variants['standard'].timeline.days_min}-{variants['standard'].timeline.days_max} jours
- Garantie : {variants['standard'].warranty_years} ans

SOLUTION PREMIUM : {variants['premium'].cost_breakdown.total_ttc:.2f} € TTC
- Durée : {variants['premium'].timeline.days_min}-{variants['premium'].timeline.days_max} jours
- Garantie : {variants['premium'].warranty_years} ans

NOTRE RECOMMANDATION : {quote.comparison.value_for_money_recommendation.value.upper()}
{quote.comparison.explanation}

---
Ces estimations sont fournies à titre indicatif.
TrustDevis - https://trustdevis.com
"""
        
        return text

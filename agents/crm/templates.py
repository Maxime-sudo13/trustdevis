# Templates d'emails et notifications pour le CRM TrustDevis

TEMPLATES = {
    "bienvenue": {
        "sujet": "Bienvenue sur TrustDevis - Votre premier devis vous attend !",
        "contenu_html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2563eb; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }
        .content { background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }
        .button { display: inline-block; background: #2563eb; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }
        .footer { text-align: center; margin-top: 30px; font-size: 12px; color: #6b7280; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Bienvenue sur TrustDevis !</h1>
        </div>
        <div class="content">
            <p>Bonjour <strong>{nom}</strong>,</p>
            
            <p>Merci de nous avoir rejoints ! TrustDevis est votre allié pour vérifier vos devis en toute sérénité.</p>
            
            <h3>🚀 Pour bien démarrer :</h3>
            <ul>
                <li>Uploader votre premier devis PDF</li>
                <li>Recevez une analyse détaillée en quelques minutes</li>
                <li>Identifiez les anomalies potentielles</li>
            </ul>
            
            <div style="text-align: center;">
                <a href="{url_upload}" class="button">Uploader mon premier devis</a>
            </div>
            
            <p>Votre essai gratuit de 14 jours commence aujourd'hui. Profitez-en pour tester toutes nos fonctionnalités !</p>
            
            <p>Des questions ? Répondez simplement à cet email.</p>
            
            <p>L'équipe TrustDevis</p>
        </div>
        <div class="footer">
            <p>TrustDevis - Vérifiez vos devis en toute confiance</p>
        </div>
    </div>
</body>
</html>
""",
        "contenu_text": """
Bonjour {nom},

Merci de nous avoir rejoints ! TrustDevis est votre allié pour vérifier vos devis en toute sérénité.

Pour bien démarrer :
1. Uploader votre premier devis PDF
2. Recevez une analyse détaillée en quelques minutes
3. Identifiez les anomalies potentielles

Commencez maintenant : {url_upload}

Votre essai gratuit de 14 jours commence aujourd'hui. Profitez-en pour tester toutes nos fonctionnalités !

Des questions ? Répondez simplement à cet email.

L'équipe TrustDevis
TrustDevis - Vérifiez vos devis en toute confiance
"""
    },
    
    "relance_upload": {
        "sujet": "Votre devis vous attend sur TrustDevis",
        "contenu_html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #f59e0b; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }
        .content { background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }
        .button { display: inline-block; background: #f59e0b; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }
        .highlight { background: #fef3c7; padding: 15px; border-radius: 6px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📄 Prêt à analyser votre devis ?</h1>
        </div>
        <div class="content">
            <p>Bonjour <strong>{nom}</strong>,</p>
            
            <p>Vous vous êtes inscrit sur TrustDevis il y a {jours} jour(s), mais vous n'avez pas encore uploadé de devis.</p>
            
            <div class="highlight">
                <strong>Pourquoi analyser votre devis ?</strong>
                <ul>
                    <li>✅ Détection des anomalies tarifaires</li>
                    <li>✅ Vérification des cohérences techniques</li>
                    <li>✅ Comparaison avec les prix du marché</li>
                    <li>✅ Rapport détaillé en 2 minutes</li>
                </ul>
            </div>
            
            <div style="text-align: center;">
                <a href="{url_upload}" class="button">Analyser mon devis maintenant</a>
            </div>
            
            <p>C'est rapide, gratuit pendant votre essai, et ça peut vous faire économiser des centaines d'euros !</p>
            
            <p>L'équipe TrustDevis</p>
        </div>
    </div>
</body>
</html>
""",
        "contenu_text": """
Bonjour {nom},

Vous vous êtes inscrit sur TrustDevis il y a {jours} jour(s), mais vous n'avez pas encore uploadé de devis.

Pourquoi analyser votre devis ?
✅ Détection des anomalies tarifaires
✅ Vérification des cohérences techniques
✅ Comparaison avec les prix du marché
✅ Rapport détaillé en 2 minutes

Analyser mon devis maintenant : {url_upload}

C'est rapide, gratuit pendant votre essai, et ça peut vous faire économiser des centaines d'euros !

L'équipe TrustDevis
"""
    },
    
    "resultat_analyse": {
        "sujet": "Votre analyse TrustDevis est prête !",
        "contenu_html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #10b981; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }
        .content { background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }
        .button { display: inline-block; background: #10b981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }
        .score-box { text-align: center; padding: 20px; background: white; border-radius: 8px; margin: 20px 0; }
        .score { font-size: 48px; font-weight: bold; color: #10b981; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Votre analyse est prête !</h1>
        </div>
        <div class="content">
            <p>Bonjour <strong>{nom}</strong>,</p>
            
            <p>Nous avons terminé l'analyse de votre devis <strong>{nom_fichier}</strong>.</p>
            
            <div class="score-box">
                <p>Score de confiance</p>
                <div class="score">{score}/100</div>
                <p>{interpretation_score}</p>
            </div>
            
            <div style="text-align: center;">
                <a href="{url_resultat}" class="button">Voir l'analyse complète</a>
            </div>
            
            <p><strong>Résumé :</strong></p>
            <ul>
                <li>Nombre de lignes analysées : {nb_lignes}</li>
                <li>Montant total : {montant_total} €</li>
                <li>Anomalies détectées : {nb_anomalies}</li>
            </ul>
            
            <p>Consultez le rapport complet pour voir les détails et nos recommandations.</p>
            
            <p>L'équipe TrustDevis</p>
        </div>
    </div>
</body>
</html>
""",
        "contenu_text": """
Bonjour {nom},

Nous avons terminé l'analyse de votre devis {nom_fichier}.

Score de confiance : {score}/100
{interpretation_score}

Voir l'analyse complète : {url_resultat}

Résumé :
- Nombre de lignes analysées : {nb_lignes}
- Montant total : {montant_total} €
- Anomalies détectées : {nb_anomalies}

Consultez le rapport complet pour voir les détails et nos recommandations.

L'équipe TrustDevis
"""
    },
    
    "nps": {
        "sujet": "Votre avis compte pour TrustDevis",
        "contenu_html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #8b5cf6; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }
        .content { background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }
        .nps-scale { display: flex; justify-content: center; gap: 5px; margin: 20px 0; }
        .nps-btn { display: inline-block; width: 40px; height: 40px; line-height: 40px; text-align: center; background: #e5e7eb; color: #374151; text-decoration: none; border-radius: 4px; font-weight: bold; }
        .nps-btn:hover { background: #8b5cf6; color: white; }
        .nps-labels { display: flex; justify-content: space-between; font-size: 12px; color: #6b7280; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💜 Votre avis compte !</h1>
        </div>
        <div class="content">
            <p>Bonjour <strong>{nom}</strong>,</p>
            
            <p>Vous utilisez TrustDevis depuis {jours} jours maintenant. Nous aimerions connaître votre opinion !</p>
            
            <p><strong>À quel point recommanderiez-vous TrustDevis à un collègue ou un ami ?</strong></p>
            <p style="text-align: center; font-size: 12px; color: #6b7280;">(0 = Pas du tout, 10 = Très probablement)</p>
            
            <div class="nps-scale">
                {nps_buttons}
            </div>
            <div class="nps-labels">
                <span>Peu probable</span>
                <span>Très probable</span>
            </div>
            
            <p style="margin-top: 30px;">Votre retour nous aide à améliorer TrustDevis chaque jour. Merci !</p>
            
            <p>L'équipe TrustDevis</p>
        </div>
    </div>
</body>
</html>
""",
        "contenu_text": """
Bonjour {nom},

Vous utilisez TrustDevis depuis {jours} jours maintenant. Nous aimerions connaître votre opinion !

À quel point recommanderiez-vous TrustDevis à un collègue ou un ami ?
(0 = Pas du tout, 10 = Très probablement)

Donnez votre avis : {url_nps}

Votre retour nous aide à améliorer TrustDevis chaque jour. Merci !

L'équipe TrustDevis
"""
    },
    
    "renouvellement": {
        "sujet": "Votre abonnement TrustDevis expire bientôt",
        "contenu_html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #ef4444; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }
        .content { background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }
        .button { display: inline-block; background: #ef4444; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }
        .button-secondary { display: inline-block; background: #6b7280; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 5px; }
        .alert { background: #fee2e2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; }
        .benefits { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⏰ Renouvellement de votre abonnement</h1>
        </div>
        <div class="content">
            <p>Bonjour <strong>{nom}</strong>,</p>
            
            <div class="alert">
                <strong>Votre abonnement {plan} expire dans {jours_restant} jours.</strong>
            </div>
            
            <p>Pour continuer à bénéficier de TrustDevis sans interruption, pensez à renouveler votre abonnement :</p>
            
            <div class="benefits">
                <h3>✨ Ce que vous continuez à obtenir :</h3>
                <ul>
                    <li>Analyses de devis illimitées</li>
                    <li>Rapports détaillés PDF</li>
                    <li>Support prioritaire</li>
                    <li>Mises à jour incluses</li>
                    <li>Historique de vos analyses</li>
                </ul>
            </div>
            
            <div style="text-align: center;">
                <a href="{url_renouvellement}" class="button">Renouveler maintenant</a>
                <a href="{url_modifier_plan}" class="button-secondary">Modifier mon plan</a>
            </div>
            
            <p style="font-size: 12px; color: #6b7280; margin-top: 30px;">
                Si vous ne renouvelez pas, votre accès sera suspendu à l'expiration. Vos données seront conservées 30 jours.
            </p>
            
            <p>L'équipe TrustDevis</p>
        </div>
    </div>
</body>
</html>
""",
        "contenu_text": """
Bonjour {nom},

Votre abonnement {plan} expire dans {jours_restant} jours.

Pour continuer à bénéficier de TrustDevis sans interruption, pensez à renouveler votre abonnement :

Ce que vous continuez à obtenir :
✅ Analyses de devis illimitées
✅ Rapports détaillés PDF
✅ Support prioritaire
✅ Mises à jour incluses
✅ Historique de vos analyses

Renouveler maintenant : {url_renouvellement}
Modifier mon plan : {url_modifier_plan}

Si vous ne renouvelez pas, votre accès sera suspendu à l'expiration. Vos données seront conservées 30 jours.

L'équipe TrustDevis
"""
    },
    
    "conversion_essai": {
        "sujet": "Passez à la vitesse supérieure avec TrustDevis Pro",
        "contenu_html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2563eb; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }
        .content { background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }
        .button { display: inline-block; background: #2563eb; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }
        .highlight { background: #dbeafe; padding: 15px; border-radius: 6px; margin: 20px 0; }
        .pricing { text-align: center; padding: 20px; background: white; border-radius: 8px; margin: 20px 0; }
        .price { font-size: 36px; font-weight: bold; color: #2563eb; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Passez à TrustDevis Pro</h1>
        </div>
        <div class="content">
            <p>Bonjour <strong>{nom}</strong>,</p>
            
            <p>Votre essai gratuit se termine dans {jours_restant} jours. Ne perdez pas l'avantage que vous avez pris !</p>
            
            <div class="highlight">
                <strong>Vous avez déjà analysé {nb_devis} devis avec nous.</strong><br>
                Imaginez tout ce que vous pourriez faire avec un accès illimité...
            </div>
            
            <div class="pricing">
                <p class="price">29€<span style="font-size: 16px;">/mois</span></p>
                <p>Plan Pro - Sans engagement</p>
            </div>
            
            <h3>✨ En passant à Pro :</h3>
            <ul>
                <li>Analyses de devis illimitées</li>
                <li>Rapports PDF téléchargeables</li>
                <li>Comparaison avec le marché</li>
                <li>Support email sous 24h</li>
                <li>Historique illimité</li>
            </ul>
            
            <div style="text-align: center;">
                <a href="{url_upgrade}" class="button">Passer à Pro maintenant</a>
            </div>
            
            <p style="font-size: 12px; color: #6b7280; margin-top: 20px;">
                Offre spéciale : -20% sur votre première année avec le code <strong>TRUST20</strong>
            </p>
            
            <p>L'équipe TrustDevis</p>
        </div>
    </div>
</body>
</html>
""",
        "contenu_text": """
Bonjour {nom},

Votre essai gratuit se termine dans {jours_restant} jours. Ne perdez pas l'avantage que vous avez pris !

Vous avez déjà analysé {nb_devis} devis avec nous.
Imaginez tout ce que vous pourriez faire avec un accès illimité...

---
29€/mois - Plan Pro - Sans engagement
---

En passant à Pro :
✅ Analyses de devis illimitées
✅ Rapports PDF téléchargeables
✅ Comparaison avec le marché
✅ Support email sous 24h
✅ Historique illimité

Passer à Pro maintenant : {url_upgrade}

Offre spéciale : -20% sur votre première année avec le code TRUST20

L'équipe TrustDevis
"""
    }
}

def get_template(nom_template: str, **kwargs) -> dict:
    """
    Récupère un template et remplace les variables.
    
    Args:
        nom_template: Nom du template (bienvenue, relance_upload, etc.)
        **kwargs: Variables à remplacer dans le template
    
    Returns:
        dict avec 'sujet', 'contenu_html', 'contenu_text'
    """
    if nom_template not in TEMPLATES:
        raise ValueError(f"Template '{nom_template}' non trouvé")
    
    template = TEMPLATES[nom_template].copy()
    
    # Remplacer les variables dans tous les champs
    for key in ['sujet', 'contenu_html', 'contenu_text']:
        if key in template:
            try:
                template[key] = template[key].format(**kwargs)
            except KeyError as e:
                # Variable manquante, on laisse le placeholder
                pass
    
    return template

def generate_nps_buttons(base_url: str, client_id: int) -> str:
    """Génère les boutons NPS 0-10 pour le template HTML."""
    buttons = []
    for i in range(11):
        url = f"{base_url}/nps?client_id={client_id}&score={i}"
        buttons.append(f'<a href="{url}" class="nps-btn">{i}</a>')
    return '\n'.join(buttons)

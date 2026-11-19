from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Client, Relance, NPS, RelanceType, RelanceStatus, PlanType
from templates import get_template, generate_nps_buttons
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CRMScheduler:
    def __init__(self, db_session_factory, email_sender=None, base_url="https://trustdevis.com"):
        self.scheduler = BackgroundScheduler()
        self.SessionLocal = db_session_factory
        self.email_sender = email_sender
        self.base_url = base_url
    
    def start(self):
        """Démarre le planificateur de tâches."""
        # Relances onboarding - tous les jours à 9h
        self.scheduler.add_job(
            self.process_onboarding_relances,
            CronTrigger(hour=9, minute=0),
            id="onboarding_relances",
            replace_existing=True
        )
        
        # Relances conversion essai → payant - tous les jours à 10h
        self.scheduler.add_job(
            self.process_conversion_relances,
            CronTrigger(hour=10, minute=0),
            id="conversion_relances",
            replace_existing=True
        )
        
        # Demandes NPS - tous les jours à 11h
        self.scheduler.add_job(
            self.process_nps_requests,
            CronTrigger(hour=11, minute=0),
            id="nps_requests",
            replace_existing=True
        )
        
        # Relances renouvellement - tous les jours à 12h
        self.scheduler.add_job(
            self.process_renewal_relances,
            CronTrigger(hour=12, minute=0),
            id="renewal_relances",
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("✅ Planificateur CRM démarré")
    
    def stop(self):
        """Arrête le planificateur."""
        self.scheduler.shutdown()
        logger.info("🛑 Planificateur CRM arrêté")
    
    def process_onboarding_relances(self):
        """Traite les relances d'onboarding (J+1, J+3, J+7)."""
        db = self.SessionLocal()
        try:
            now = datetime.utcnow()
            
            # J+1 : Relance upload devis
            j1_date = now - timedelta(days=1)
            clients_j1 = db.query(Client).filter(
                Client.date_inscription <= j1_date,
                Client.date_inscription > j1_date - timedelta(days=1),
                Client.actif == 1
            ).all()
            
            for client in clients_j1:
                self._create_relance_if_not_exists(
                    db, client.id, RelanceType.ONBOARDING_J1,
                    f"Relance J+1 - Bienvenue et upload",
                    now
                )
            
            # J+3 : Relance upload si pas encore de devis
            j3_date = now - timedelta(days=3)
            clients_j3 = db.query(Client).filter(
                Client.date_inscription <= j3_date,
                Client.date_inscription > j3_date - timedelta(days=1),
                Client.actif == 1
            ).all()
            
            for client in clients_j3:
                # Vérifier si le client a déjà uploadé un devis
                has_devis = len(client.devis) > 0
                if not has_devis:
                    self._create_relance_if_not_exists(
                        db, client.id, RelanceType.ONBOARDING_J3,
                        f"Relance J+3 - Upload devis",
                        now
                    )
            
            # J+7 : Dernière relance onboarding
            j7_date = now - timedelta(days=7)
            clients_j7 = db.query(Client).filter(
                Client.date_inscription <= j7_date,
                Client.date_inscription > j7_date - timedelta(days=1),
                Client.actif == 1
            ).all()
            
            for client in clients_j7:
                has_devis = len(client.devis) > 0
                if not has_devis:
                    self._create_relance_if_not_exists(
                        db, client.id, RelanceType.ONBOARDING_J7,
                        f"Relance J+7 - Dernière chance essai",
                        now
                    )
            
            db.commit()
            logger.info(f"📧 Relances onboarding créées: J+1({len(clients_j1)}), J+3({len(clients_j3)}), J+7({len(clients_j7)})")
            
        except Exception as e:
            logger.error(f"❌ Erreur relances onboarding: {e}")
            db.rollback()
        finally:
            db.close()
    
    def process_conversion_relances(self):
        """Traite les relances de conversion essai → payant."""
        db = self.SessionLocal()
        try:
            now = datetime.utcnow()
            
            # J-3 avant fin d'essai
            j3_before_end = now + timedelta(days=3)
            clients_j3 = db.query(Client).filter(
                Client.date_fin_essai <= j3_before_end,
                Client.date_fin_essai > j3_before_end - timedelta(days=1),
                Client.plan == PlanType.ESSAI,
                Client.actif == 1
            ).all()
            
            for client in clients_j3:
                self._create_relance_if_not_exists(
                    db, client.id, RelanceType.CONVERSION,
                    f"Conversion - Votre essai se termine bientôt",
                    now,
                    jours_restant=3
                )
            
            # J-1 avant fin d'essai
            j1_before_end = now + timedelta(days=1)
            clients_j1 = db.query(Client).filter(
                Client.date_fin_essai <= j1_before_end,
                Client.date_fin_essai > j1_before_end - timedelta(days=1),
                Client.plan == PlanType.ESSAI,
                Client.actif == 1
            ).all()
            
            for client in clients_j1:
                self._create_relance_if_not_exists(
                    db, client.id, RelanceType.CONVERSION,
                    f"Conversion - Dernier jour de votre essai",
                    now,
                    jours_restant=1
                )
            
            db.commit()
            logger.info(f"📧 Relances conversion créées: J-3({len(clients_j3)}), J-1({len(clients_j1)})")
            
        except Exception as e:
            logger.error(f"❌ Erreur relances conversion: {e}")
            db.rollback()
        finally:
            db.close()
    
    def process_nps_requests(self):
        """Traite les demandes NPS (J+30 après inscription)."""
        db = self.SessionLocal()
        try:
            now = datetime.utcnow()
            
            # J+30 après inscription
            j30_date = now - timedelta(days=30)
            clients_j30 = db.query(Client).filter(
                Client.date_inscription <= j30_date,
                Client.date_inscription > j30_date - timedelta(days=1),
                Client.actif == 1
            ).all()
            
            for client in clients_j30:
                # Vérifier si NPS pas déjà envoyé
                existing_nps = db.query(Relance).filter(
                    Relance.client_id == client.id,
                    Relance.type == RelanceType.NPS
                ).first()
                
                if not existing_nps:
                    self._create_relance_if_not_exists(
                        db, client.id, RelanceType.NPS,
                        f"NPS - Votre avis compte",
                        now,
                        jours=30
                    )
            
            db.commit()
            logger.info(f"📧 Demandes NPS créées: {len(clients_j30)}")
            
        except Exception as e:
            logger.error(f"❌ Erreur demandes NPS: {e}")
            db.rollback()
        finally:
            db.close()
    
    def process_renewal_relances(self):
        """Traite les relances de renouvellement d'abonnement."""
        db = self.SessionLocal()
        try:
            now = datetime.utcnow()
            
            # J-7 avant fin d'abonnement
            j7_before_end = now + timedelta(days=7)
            clients_j7 = db.query(Client).filter(
                Client.date_fin_abonnement <= j7_before_end,
                Client.date_fin_abonnement > j7_before_end - timedelta(days=1),
                Client.plan != PlanType.ESSAI,
                Client.actif == 1
            ).all()
            
            for client in clients_j7:
                self._create_relance_if_not_exists(
                    db, client.id, RelanceType.RENOUVELLEMENT,
                    f"Renouvellement - Votre abonnement expire dans 7 jours",
                    now,
                    jours_restant=7
                )
            
            # J-1 avant fin d'abonnement
            j1_before_end = now + timedelta(days=1)
            clients_j1 = db.query(Client).filter(
                Client.date_fin_abonnement <= j1_before_end,
                Client.date_fin_abonnement > j1_before_end - timedelta(days=1),
                Client.plan != PlanType.ESSAI,
                Client.actif == 1
            ).all()
            
            for client in clients_j1:
                self._create_relance_if_not_exists(
                    db, client.id, RelanceType.RENOUVELLEMENT,
                    f"Renouvellement - Votre abonnement expire demain",
                    now,
                    jours_restant=1
                )
            
            db.commit()
            logger.info(f"📧 Relances renouvellement créées: J-7({len(clients_j7)}), J-1({len(clients_j1)})")
            
        except Exception as e:
            logger.error(f"❌ Erreur relances renouvellement: {e}")
            db.rollback()
        finally:
            db.close()
    
    def _create_relance_if_not_exists(self, db: Session, client_id: int, 
                                       relance_type: RelanceType, sujet: str,
                                       now: datetime, **extra_data):
        """Crée une relance si elle n'existe pas déjà pour ce client/type."""
        existing = db.query(Relance).filter(
            Relance.client_id == client_id,
            Relance.type == relance_type,
            Relance.date_planification >= now - timedelta(days=1)
        ).first()
        
        if not existing:
            relance = Relance(
                client_id=client_id,
                type=relance_type,
                sujet=sujet,
                date_planification=now,
                status=RelanceStatus.PLANIFIE,
                contenu=str(extra_data) if extra_data else None
            )
            db.add(relance)
            return relance
        return None
    
    def send_pending_emails(self):
        """Envoie les emails en attente (à appeler par un worker séparé)."""
        db = self.SessionLocal()
        try:
            pending = db.query(Relance).filter(
                Relance.status == RelanceStatus.PLANIFIE,
                Relance.date_planification <= datetime.utcnow()
            ).limit(100).all()
            
            for relance in pending:
                try:
                    self._send_email_for_relance(db, relance)
                except Exception as e:
                    logger.error(f"❌ Erreur envoi email relance {relance.id}: {e}")
                    relance.status = RelanceStatus.ERREUR
            
            db.commit()
            logger.info(f"📤 Emails envoyés: {len(pending)}")
            
        except Exception as e:
            logger.error(f"❌ Erreur envoi emails: {e}")
            db.rollback()
        finally:
            db.close()
    
    def _send_email_for_relance(self, db: Session, relance: Relance):
        """Envoie un email pour une relance donnée."""
        client = db.query(Client).filter(Client.id == relance.client_id).first()
        if not client:
            return
        
        # Préparer le template
        template_data = {
            "nom": client.nom,
            "email": client.email,
            "entreprise": client.entreprise or "",
            "url_upload": f"{self.base_url}/upload",
            "url_resultat": f"{self.base_url}/dashboard",
            "url_renouvellement": f"{self.base_url}/renew",
            "url_upgrade": f"{self.base_url}/upgrade",
            "url_modifier_plan": f"{self.base_url}/plans",
            "url_nps": f"{self.base_url}/nps?client_id={client.id}",
        }
        
        # Ajouter les données spécifiques
        if relance.contenu:
            import json
            try:
                extra = json.loads(relance.contenu.replace("'", '"'))
                template_data.update(extra)
            except:
                pass
        
        # Sélectionner le template
        template_name = self._get_template_name(relance.type)
        
        if template_name and self.email_sender:
            try:
                template = get_template(template_name, **template_data)
                self.email_sender.send(
                    to=client.email,
                    subject=template["sujet"],
                    html=template["contenu_html"],
                    text=template["contenu_text"]
                )
                relance.status = RelanceStatus.ENVOYE
                relance.date_envoi = datetime.utcnow()
                logger.info(f"✅ Email envoyé à {client.email} ({relance.type.value})")
            except Exception as e:
                logger.error(f"❌ Erreur envoi: {e}")
                relance.status = RelanceStatus.ERREUR
    
    def _get_template_name(self, relance_type: RelanceType) -> str:
        """Retourne le nom du template pour un type de relance."""
        mapping = {
            RelanceType.ONBOARDING_J1: "bienvenue",
            RelanceType.ONBOARDING_J3: "relance_upload",
            RelanceType.ONBOARDING_J7: "relance_upload",
            RelanceType.CONVERSION: "conversion_essai",
            RelanceType.NPS: "nps",
            RelanceType.RENOUVELLEMENT: "renouvellement",
        }
        return mapping.get(relance_type)


# Fonction utilitaire pour créer le scheduler
def create_scheduler(db_session_factory, email_sender=None, base_url="https://trustdevis.com"):
    """Crée et configure le scheduler CRM."""
    return CRMScheduler(db_session_factory, email_sender, base_url)

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import CybercrimeType

@receiver(post_migrate)
def create_default_cybercrimes(sender, **kwargs):
    if sender.name == "cases":
        defaults = [
            {"name": "Phishing", "description": "Fraudulent attempts to obtain sensitive information via email or fake websites."},
            {"name": "Identity Theft", "description": "Stealing someone’s personal data to impersonate them online."},
            {"name": "Online Fraud", "description": "Using the internet to deceive individuals or organizations for financial gain."},
            {"name": "Cyberbullying", "description": "Harassment or bullying behavior using digital platforms."},
            {"name": "Ransomware", "description": "Malware that encrypts files and demands a ransom for decryption."},
            {"name": "Hacking", "description": "Unauthorized access to or control of a computer system or network."},
            {"name": "Social Engineering", "description": "Manipulating people into revealing confidential information."},
            {"name": "Malware Distribution", "description": "Spreading malicious software designed to harm systems or steal data."},
            {"name": "Online Scams", "description": "Deceptive practices that trick people into giving money or information."},
        ]

        for item in defaults:
            CybercrimeType.objects.get_or_create(
                name=item["name"],
                defaults={"description": item["description"]}
            )

from django.core.management import BaseCommand
from argparse import ArgumentParser
import requests

class Command(BaseCommand):

    def handle(self, *args, **options):

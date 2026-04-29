from faker import Faker
from utils.helpers import generar_documento

fake = Faker("es_ES")

primer_nombre = "Certificación"
segundo_nombre = fake.first_name()
primer_apellido = fake.last_name()
segundo_apellido = fake.last_name()
documento = generar_documento()
correo = "david.castro@olimpiait.com"
celular = 3192097403


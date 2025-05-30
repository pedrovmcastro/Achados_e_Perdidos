from pymongo import MongoClient

uri = (
    "mongodb+srv://mahousenshi:mZo8U6lAgbhpMgFK"
    "@ac-5uf98mb.sn8qnsa.mongodb.net/"
    "?retryWrites=true"
    "&w=majority"
    "&tls=true"
    # forçando a ignorar validação de certificado
    "&tlsAllowInvalidCertificates=true"
)

client = MongoClient(uri)
try:
    print("DBs:", client.list_database_names())
except Exception as e:
    print("Erro com tlsAllowInvalidCertificates:", e)

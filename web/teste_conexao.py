from pymongo import MongoClient

uri = "mongodb+srv://mahousenshi:mZo8U6lAgbhpMgFK@cluster0.sn8qnsa.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)

try:
    print(client.list_database_names())
except Exception as e:
    print("Erro de conexão:", e)

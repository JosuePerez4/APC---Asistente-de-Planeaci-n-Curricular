import requests
import json

def fetch_and_transform_pensum():
    url = 'https://horarioapp.0025600.xyz/pensum'
    token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6ImIyNDg2Mzc0OTVjYjM4N2U0OWViNmRlMThkZjk5N2VlOGU1YWUyOTciLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiSkVTVVMgREFOSUVMIExPWkFOTyBFUkFaTyIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NKdHFhTGFpSXZFS2d3Z1lKcXdSM3RGVjFRZWhCTElkRENpVUZ1dk82MF93eElUOWNYMz1zOTYtYyIsImlzcyI6Imh0dHBzOi8vc2VjdXJldG9rZW4uZ29vZ2xlLmNvbS9mb3JtYWwtYW5hbHl6ZXItNDE3NzAxIiwiYXVkIjoiZm9ybWFsLWFuYWx5emVyLTQxNzcwMSIsImF1dGhfdGltZSI6MTc4NDYwNDUzOSwidXNlcl9pZCI6IjBYMDBEeVZJTU1PcThwZWhiTWE1MUdxSU9qcjIiLCJzdWIiOiIwWDAwRHlWSU1NT3E4cGVoYk1hNTFHcUlPanIyIiwiaWF0IjoxNzg0NjA0NTM5LCJleHAiOjE3ODQ2MDgxMzksImVtYWlsIjoiamVzdXNkYW5pZWxsZUB1ZnBzLmVkdS5jbyIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7Imdvb2dsZS5jb20iOlsiMTEwMDg0ODExNTI0NjQwMzY3MjU1Il0sImVtYWlsIjpbImplc3VzZGFuaWVsbGVAdWZwcy5lZHUuY28iXX0sInNpZ25faW5fcHJvdmlkZXIiOiJnb29nbGUuY29tIn19.ZcLA0gVECg5ZgZuNqI6MwzQ5L2Jep15UepzS6FCI7PPhWFzHbG1jZWh9X6RqaYbSNPHWn6_i4p2nY-e-62wsuixMIAGeViFEuv5ua9HhZRICt5lXb0V8P0xH2_up_cLGaULagoSqG9d0x3vwuexIfyon9Aybc1AsleVbfK6nmWaWs4qWkBkvMEcU_mgTHTGfils91sJ6_fHWjpiPNyNmNntAsu1sfLcj9E6zfDZBu2L4YJv5BaSOXC0udIx6GBiGkNaEttAnt-fc-5XSpSKxVY2so72KDq8bSJsqw1bhyS8aK5ZMYbTJNJuQO5CIiROwq6x17WB1hd2gBPgZSKSFuw'
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Transformar los datos
        transformed_data = transform_data(data)
        
        # Guardar en un archivo JSON
        with open('pensum_filtrado.json', 'w', encoding='utf-8') as f:
            json.dump(transformed_data, f, ensure_ascii=False, indent=2)
        
        print("Archivo guardado como 'pensum_filtrado.json'")
        return transformed_data
        
    except requests.exceptions.RequestException as e:
        print(f"Error en la petición: {e}")
        return None

def transform_data(data):
    """Transforma los datos para quedarse solo con los campos necesarios"""
    transformed = {
        "subjects": []
    }
    
    for subject in data.get("subjects", []):
        # Campos principales
        new_subject = {
            "id": subject.get("id"),
            "code": subject.get("code"),
            "name": subject.get("name"),
            "credits": subject.get("credits"),
            "semester": subject.get("semester"),
            "requiredCredits": subject.get("requiredCredits"),
            "type": subject.get("type"),
            "requisites": [],
            "groups": []
        }
        
        # Transformar requisites (solo id, name, code)
        for req in subject.get("requisites", []):
            new_subject["requisites"].append({
                "id": req.get("id"),
                "name": req.get("name"),
                "code": req.get("code")
            })
        
        # Transformar groups (con sesiones simplificadas)
        for group in subject.get("groups", []):
            new_group = {
                "id": group.get("id"),
                "code": group.get("code"),
                "teacher": group.get("teacher"),
                "program": group.get("program"),
                "maxCapacity": group.get("maxCapacity"),
                "availableCapacity": group.get("availableCapacity"),
                "sessions": []
            }
            
            # Transformar sesiones
            for session in group.get("sessions", []):
                new_group["sessions"].append({
                    "id": session.get("id"),
                    "day": session.get("day"),
                    "beginHour": session.get("beginHour"),
                    "endHour": session.get("endHour"),
                    "classroom": session.get("classroom")
                })
            
            new_subject["groups"].append(new_group)
        
        transformed["subjects"].append(new_subject)
    
    return transformed

if __name__ == "__main__":
    fetch_and_transform_pensum()
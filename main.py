import requests

def fetch_user(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching user data:", response.status_code)
        return None
    

if __name__ == "__main__":
    user = input("Enter GitHub username: ")
    data = fetch_user(user)
    print(data)
import requests
r = requests.post(
    "https://api.deepai.org/api/torch-srgan",
    files={
        'image': open('aaa.jpg', 'rb'),
    },
    headers={'api-key': 'quickstart-QUdJIGlzIGNvbWluZy4uLi4K'}
)
print(r.json())
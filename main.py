from fastapi import FastAPI
import os

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get('/ctf')
def root():
    token="abcd"
    os.system(f"docker run --name {token} -p 3000 ctf_1")
    return 'ctf'
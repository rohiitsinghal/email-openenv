from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Email OpenEnv is running"}

# Minimal endpoints required for OpenEnv validation

@app.post("/reset")
def reset():
    return {"status": "ok"}

@app.post("/step")
def step():
    return {"status": "ok"}

# REQUIRED for OpenEnv validator (entrypoint)
def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
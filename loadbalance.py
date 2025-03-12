import subprocess
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Docker Manager API")

# Docker image to use
DOCKER_IMAGE = "bharanidharan/galaxykick:v42"

class UserRequest(BaseModel):
    username: str

class UpdateRequest(BaseModel):
    username: str
    arguments: str

def container_exists(username):
    """Check if container exists for the given username"""
    try:
        result = subprocess.run(
            ["udocker", "--allow-root", "ps"],
            capture_output=True,
            text=True,
            check=True
        )
        return username in result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Error checking container existence: {e}")
        return False

def container_running(username):
    """Check if container is running for the given username"""
    try:
        result = subprocess.run(
            ["udocker", "--allow-root", "ps"],
            capture_output=True,
            text=True,
            check=True
        )
        lines = result.stdout.splitlines()
        for line in lines:
            if username in line and "RUNNING" in line:
                return True
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Error checking container status: {e}")
        return False

@app.post("/startDocker")
async def start_docker(user_request: UserRequest):
    username = user_request.username
    
    if container_exists(username):
        if container_running(username):
            return {"message": f"Container for {username} is already running"}
        
        try:
            subprocess.run(["udocker", "--allow-root", "start", username], check=True)
            return {"message": f"Container for {username} started successfully"}
        except subprocess.CalledProcessError as e:
            logger.error(f"Error starting container: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to start container: {str(e)}")
    
    try:
        subprocess.run(["udocker", "--allow-root", "pull", DOCKER_IMAGE], check=True)
        subprocess.run(["udocker", "--allow-root", "create", "--name=" + username, DOCKER_IMAGE], check=True)
        subprocess.run(["udocker", "--allow-root", "run", username], check=True)
        return {"message": f"Container for {username} created and started successfully"}
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating/starting container: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create/start container: {str(e)}")

@app.post("/stopDocker")
async def stop_docker(user_request: UserRequest):
    username = user_request.username
    
    if not container_exists(username):
        raise HTTPException(status_code=404, detail=f"Container for {username} not found")
    
    try:
        # Use rm command directly as requested
        result = subprocess.run(
            ["udocker", "--allow-root", "rm", username],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Container removal result: {result.stdout}")
        return {"message": f"Container for {username} stopped and removed successfully"}
    except subprocess.CalledProcessError as e:
        logger.error(f"Error removing container: {e}")
        logger.error(f"Command stderr: {e.stderr}")
        raise HTTPException(status_code=500, detail=f"Failed to remove container: {str(e)}")

@app.post("/updateDocker")
async def update_docker(update_request: UpdateRequest):
    username = update_request.username
    arguments = update_request.arguments
    
    if not container_exists(username):
        raise HTTPException(status_code=404, detail=f"Container for {username} not found")
    
    if not container_running(username):
        raise HTTPException(status_code=400, detail=f"Container for {username} is not running")
    
    try:
        subprocess.run(["udocker", "--allow-root", "exec", username, arguments], check=True)
        return {"message": f"Command executed in container {username} successfully"}
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing command in container: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to execute command: {str(e)}")

@app.get("/containerStatus/{username}")
async def container_status(username: str):
    if not container_exists(username):
        return {"status": "not_exists"}
    
    if container_running(username):
        return {"status": "running"}
    else:
        return {"status": "stopped"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
